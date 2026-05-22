#!/usr/bin/env python3
"""Fix known stale absolute project paths in JetBrains .idea metadata."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath


RAW_LAST_OPENED_RE = re.compile(
    r'(?P<prefix>"last_opened_file_path"\s*:\s*")(?P<path>[^"]+)(?P<suffix>")'
)
ESCAPED_LAST_OPENED_RE = re.compile(
    r"(?P<prefix>&quot;last_opened_file_path&quot;\s*:\s*&quot;)"
    r"(?P<path>.*?)(?P<suffix>&quot;)"
)
COPILOT_KEY_RE = re.compile(
    r'(?P<prefix><entry\b[^>]*\bkey=")(?P<key>[^"]+)(?P<suffix>"[^>]*>)'
)
COPILOT_COMPONENT_RE = re.compile(
    r'(?P<component><component\b[^>]*\bname="CopilotPersistence"[^>]*>.*?</component>)',
    re.DOTALL,
)

RESULT_TYPES = (
    ("changed", "已成功处理仓库"),
    ("unchanged", "无需处理仓库"),
    ("failed", "处理失败仓库"),
)


@dataclass
class WorkResult:
    project_root: Path
    status: str
    fields: set[str] = field(default_factory=set)
    reason: str | None = None

    @property
    def name(self) -> str:
        return self.project_root.name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fix known stale absolute project paths in JetBrains .idea/workspace.xml "
            "metadata under a starting directory."
        )
    )
    parser.add_argument("start_dir", help="Starting directory to scan for .idea directories")
    return parser.parse_args()


def collect_idea_dirs(start_dir: Path) -> list[Path]:
    idea_dirs: list[Path] = []

    for root, dirnames, _filenames in os.walk(start_dir):
        dirnames.sort()
        if ".idea" in dirnames:
            idea_dirs.append(Path(root) / ".idea")
            dirnames.remove(".idea")

    return sorted(idea_dirs)


def split_posix_path(value: str) -> list[str] | None:
    if not value.startswith("/"):
        return None

    path = PurePosixPath(value)
    parts = list(path.parts)
    if not parts or parts[0] != "/":
        return None
    return parts


def replace_stale_project_prefix(value: str, project_root: Path) -> tuple[str, bool]:
    parts = split_posix_path(value)
    if parts is None:
        return value, False

    project_name = project_root.name
    current_root = project_root.as_posix()

    for index, part in enumerate(parts):
        if part != project_name:
            continue

        old_root = PurePosixPath(*parts[: index + 1]).as_posix()
        if old_root == current_root:
            return value, False

        suffix_parts = parts[index + 1 :]
        if suffix_parts:
            replacement = PurePosixPath(current_root, *suffix_parts).as_posix()
        else:
            replacement = current_root
        return replacement, True

    return value, False


def fix_last_opened_paths(text: str, project_root: Path) -> tuple[str, set[str]]:
    fields: set[str] = set()

    def replace_match(match: re.Match[str]) -> str:
        old_path = match.group("path")
        new_path, changed = replace_stale_project_prefix(old_path, project_root)
        if not changed:
            return match.group(0)

        fields.add("workspace.xml: last_opened_file_path")
        return f"{match.group('prefix')}{new_path}{match.group('suffix')}"

    text = RAW_LAST_OPENED_RE.sub(replace_match, text)
    text = ESCAPED_LAST_OPENED_RE.sub(replace_match, text)
    return text, fields


def fix_copilot_keys(text: str, project_root: Path) -> tuple[str, set[str]]:
    fields: set[str] = set()

    def replace_key_match(match: re.Match[str]) -> str:
        key = match.group("key")
        if not key.startswith("_/"):
            return match.group(0)

        path_value = key[1:]
        new_path, changed = replace_stale_project_prefix(path_value, project_root)
        if not changed:
            return match.group(0)

        fields.add("workspace.xml: CopilotPersistence entry key")
        return f"{match.group('prefix')}_{new_path}{match.group('suffix')}"

    def replace_component_match(match: re.Match[str]) -> str:
        component = match.group("component")
        return COPILOT_KEY_RE.sub(replace_key_match, component)

    return COPILOT_COMPONENT_RE.sub(replace_component_match, text), fields


def atomic_write_text(path: Path, text: str) -> None:
    mode = path.stat().st_mode
    temp_name: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.tmp-",
            delete=False,
        ) as temp_file:
            temp_name = temp_file.name
            temp_file.write(text)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        temp_path = Path(temp_name)
        os.chmod(temp_path, mode)
        os.replace(temp_path, path)
    except Exception:
        if temp_name:
            try:
                Path(temp_name).unlink()
            except OSError:
                pass
        raise


def process_idea_dir(idea_dir: Path) -> WorkResult:
    project_root = idea_dir.parent
    workspace_xml = idea_dir / "workspace.xml"

    if not workspace_xml.exists():
        return WorkResult(project_root=project_root, status="unchanged")
    if not workspace_xml.is_file():
        return WorkResult(
            project_root=project_root,
            status="failed",
            reason=".idea/workspace.xml is not a regular file",
        )

    try:
        original = workspace_xml.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        return WorkResult(
            project_root=project_root,
            status="failed",
            reason=f"workspace.xml is not valid UTF-8: {error}",
        )
    except OSError as error:
        return WorkResult(
            project_root=project_root,
            status="failed",
            reason=f"failed to read workspace.xml: {error}",
        )

    updated, last_opened_fields = fix_last_opened_paths(original, project_root)
    updated, copilot_fields = fix_copilot_keys(updated, project_root)
    fields = last_opened_fields | copilot_fields

    if updated == original:
        return WorkResult(project_root=project_root, status="unchanged")

    try:
        atomic_write_text(workspace_xml, updated)
    except OSError as error:
        return WorkResult(
            project_root=project_root,
            status="failed",
            reason=f"failed to write workspace.xml: {error}",
        )

    return WorkResult(project_root=project_root, status="changed", fields=fields)


def print_report(results: list[WorkResult]) -> None:
    by_status: dict[str, list[WorkResult]] = {key: [] for key, _label in RESULT_TYPES}
    for result in results:
        by_status[result.status].append(result)

    for status, label in RESULT_TYPES:
        items = sorted(by_status[status], key=lambda item: item.project_root.as_posix())
        print(f"- {label} ({len(items)})：")
        for item in items:
            print(f"    - {item.name}")
            if status == "changed":
                fields = ", ".join(sorted(item.fields))
                print(f"        - 已修正字段：{fields}")
            elif status == "failed":
                print(f"        - 失败原因：{item.reason}")


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).expanduser().resolve()

    if not start_dir.exists():
        print(f"起始工作目录不存在：{start_dir}", file=sys.stderr)
        return 2
    if not start_dir.is_dir():
        print(f"起始工作目录不是目录：{start_dir}", file=sys.stderr)
        return 2

    idea_dirs = collect_idea_dirs(start_dir)
    results = [process_idea_dir(idea_dir) for idea_dir in idea_dirs]
    print_report(results)

    return 1 if any(result.status == "failed" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
