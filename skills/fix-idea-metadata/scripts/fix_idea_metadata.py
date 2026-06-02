#!/usr/bin/env python3
"""Fix known stale absolute project paths in JetBrains .idea metadata."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath


PROPERTY_PATH_FIELDS = {
    "last_opened_file_path": "`workspace.xml`: last_opened_file_path",
    "ts.external.directory.path": "`workspace.xml`: ts.external.directory.path",
}
PROPERTY_KEY_PATTERN = "|".join(re.escape(key) for key in PROPERTY_PATH_FIELDS)
RAW_PROPERTY_PATH_RE = re.compile(
    rf'(?P<prefix>"(?P<key>{PROPERTY_KEY_PATTERN})"\s*:\s*")'
    r'(?P<path>[^"]+)(?P<suffix>")'
)
ESCAPED_PROPERTY_PATH_RE = re.compile(
    rf"(?P<prefix>&quot;(?P<key>{PROPERTY_KEY_PATTERN})&quot;\s*:\s*&quot;)"
    r"(?P<path>.*?)(?P<suffix>&quot;)"
)
COPILOT_KEY_RE = re.compile(
    r'(?P<prefix><entry\b[^>]*\bkey=")(?P<key>[^"]+)(?P<suffix>"[^>]*>)'
)
COPILOT_COMPONENT_RE = re.compile(
    r'(?P<component><component\b[^>]*\bname="CopilotPersistence"[^>]*>.*?</component>)',
    re.DOTALL,
)
MODULE_NAME_RE = re.compile(
    r'(?P<prefix><module\b[^>]*\bname=")(?P<name>[^"]*)(?P<suffix>"[^>]*>)'
)

RESULT_TYPES = (
    ("changed", "Successfully Processed Repositories"),
    ("unchanged", "Repositories Requiring No Changes"),
    ("failed", "Failed Repositories"),
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


@dataclass(frozen=True)
class WorkItem:
    project_root: Path
    idea_dir: Path
    iml_path: Path | None
    old_iml_name: str | None
    new_iml_name: str
    project_names: frozenset[str]

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
    if "node_modules" in start_dir.parts:
        return idea_dirs

    for root, dirnames, _filenames in os.walk(start_dir):
        dirnames[:] = sorted(dirname for dirname in dirnames if dirname != "node_modules")
        if ".idea" in dirnames:
            idea_dirs.append(Path(root) / ".idea")
            dirnames.remove(".idea")

    return sorted(idea_dirs)


def list_iml_files(idea_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in idea_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".iml"
    )


def paths_refer_to_same_file(left: Path, right: Path) -> bool:
    try:
        return left.samefile(right)
    except OSError:
        return False


def build_work_items(idea_dirs: list[Path]) -> tuple[list[WorkItem], list[WorkResult]]:
    work_items: list[WorkItem] = []
    failures: list[WorkResult] = []

    for idea_dir in idea_dirs:
        project_root = idea_dir.parent
        iml_files = list_iml_files(idea_dir)

        if len(iml_files) > 1:
            names = ", ".join(path.name for path in iml_files)
            failures.append(
                WorkResult(
                    project_root=project_root,
                    status="failed",
                    reason=f".idea contains multiple .iml files: {names}",
                )
            )
            continue

        iml_path = iml_files[0] if iml_files else None
        old_iml_name = iml_path.name if iml_path else None
        new_iml_name = f"{project_root.name}.iml"

        project_names = {project_root.name}
        if iml_path:
            project_names.add(iml_path.stem)
            target_iml = idea_dir / new_iml_name
            if (
                iml_path.name != new_iml_name
                and target_iml.exists()
                and not paths_refer_to_same_file(iml_path, target_iml)
            ):
                failures.append(
                    WorkResult(
                        project_root=project_root,
                        status="failed",
                        reason=f"target IML file already exists: {target_iml}",
                    )
                )
                continue

        work_items.append(
            WorkItem(
                project_root=project_root,
                idea_dir=idea_dir,
                iml_path=iml_path,
                old_iml_name=old_iml_name,
                new_iml_name=new_iml_name,
                project_names=frozenset(project_names),
            )
        )

    return work_items, failures


def split_posix_path(value: str) -> list[str] | None:
    if not value.startswith("/"):
        return None

    path = PurePosixPath(value)
    parts = list(path.parts)
    if not parts or parts[0] != "/":
        return None
    return parts


def replace_stale_project_prefix(
    value: str,
    project_root: Path,
    project_names: frozenset[str],
) -> tuple[str, bool]:
    parts = split_posix_path(value)
    if parts is None:
        return value, False

    current_root = project_root.as_posix()
    if value == current_root or value.startswith(f"{current_root}/"):
        return value, False

    for index, part in enumerate(parts):
        if part not in project_names:
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


def fix_property_paths(text: str, item: WorkItem) -> tuple[str, set[str]]:
    fields: set[str] = set()

    def replace_match(match: re.Match[str]) -> str:
        old_path = match.group("path")
        new_path, changed = replace_stale_project_prefix(
            old_path,
            item.project_root,
            item.project_names,
        )
        if not changed:
            return match.group(0)

        fields.add(PROPERTY_PATH_FIELDS[match.group("key")])
        return f"{match.group('prefix')}{new_path}{match.group('suffix')}"

    text = RAW_PROPERTY_PATH_RE.sub(replace_match, text)
    text = ESCAPED_PROPERTY_PATH_RE.sub(replace_match, text)
    return text, fields


def fix_copilot_keys(text: str, item: WorkItem) -> tuple[str, set[str]]:
    fields: set[str] = set()

    def replace_key_match(match: re.Match[str]) -> str:
        key = match.group("key")
        if not key.startswith("_/"):
            return match.group(0)

        path_value = key[1:]
        new_path, changed = replace_stale_project_prefix(
            path_value,
            item.project_root,
            item.project_names,
        )
        if not changed:
            return match.group(0)

        fields.add("`workspace.xml`: CopilotPersistence entry key")
        return f"{match.group('prefix')}_{new_path}{match.group('suffix')}"

    def replace_component_match(match: re.Match[str]) -> str:
        component = match.group("component")
        return COPILOT_KEY_RE.sub(replace_key_match, component)

    return COPILOT_COMPONENT_RE.sub(replace_component_match, text), fields


def fix_module_names(text: str, item: WorkItem) -> tuple[str, set[str]]:
    fields: set[str] = set()

    if item.iml_path is None:
        return text, fields

    old_project_name = item.iml_path.stem
    new_project_name = item.project_root.name
    if old_project_name == new_project_name:
        return text, fields

    def replace_match(match: re.Match[str]) -> str:
        module_name = match.group("name")
        if module_name != old_project_name:
            return match.group(0)

        fields.add("`workspace.xml`: module name")
        return f"{match.group('prefix')}{new_project_name}{match.group('suffix')}"

    return MODULE_NAME_RE.sub(replace_match, text), fields


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


def make_case_rename_temp_path(target: Path) -> Path:
    for _attempt in range(100):
        candidate = target.with_name(
            f".{target.name}.tmp-case-rename-{os.getpid()}-{uuid.uuid4().hex}"
        )
        if not candidate.exists():
            return candidate

    raise OSError(f"failed to allocate temporary IML rename path for {target}")


def rename_iml_file(source: Path, target: Path) -> None:
    if source.name.casefold() != target.name.casefold():
        source.rename(target)
        return

    temp = make_case_rename_temp_path(target)
    source.rename(temp)

    try:
        temp.rename(target)
    except OSError:
        try:
            temp.rename(source)
        except OSError:
            pass
        raise


def process_workspace_xml(item: WorkItem) -> tuple[set[str], WorkResult | None]:
    workspace_xml = item.idea_dir / "workspace.xml"

    if not workspace_xml.exists():
        return set(), None
    if not workspace_xml.is_file():
        return set(), WorkResult(
            project_root=item.project_root,
            status="failed",
            reason=".idea/workspace.xml is not a regular file",
        )

    try:
        original = workspace_xml.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        return set(), WorkResult(
            project_root=item.project_root,
            status="failed",
            reason=f"workspace.xml is not valid UTF-8: {error}",
        )
    except OSError as error:
        return set(), WorkResult(
            project_root=item.project_root,
            status="failed",
            reason=f"failed to read workspace.xml: {error}",
        )

    updated, property_fields = fix_property_paths(original, item)
    updated, copilot_fields = fix_copilot_keys(updated, item)
    updated, module_name_fields = fix_module_names(updated, item)
    fields = property_fields | copilot_fields | module_name_fields

    if updated == original:
        return set(), None

    try:
        atomic_write_text(workspace_xml, updated)
    except OSError as error:
        return set(), WorkResult(
            project_root=item.project_root,
            status="failed",
            reason=f"failed to write workspace.xml: {error}",
        )

    return fields, None


def process_iml_metadata(item: WorkItem) -> tuple[set[str], WorkResult | None]:
    fields: set[str] = set()

    if item.iml_path is None or item.old_iml_name is None:
        return fields, None
    if item.old_iml_name == item.new_iml_name:
        return fields, None

    modules_xml = item.idea_dir / "modules.xml"
    if modules_xml.exists():
        if not modules_xml.is_file():
            return fields, WorkResult(
                project_root=item.project_root,
                status="failed",
                reason=".idea/modules.xml is not a regular file",
            )

        try:
            original_modules = modules_xml.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            return fields, WorkResult(
                project_root=item.project_root,
                status="failed",
                reason=f"modules.xml is not valid UTF-8: {error}",
            )
        except OSError as error:
            return fields, WorkResult(
                project_root=item.project_root,
                status="failed",
                reason=f"failed to read modules.xml: {error}",
            )

        updated_modules = original_modules.replace(item.old_iml_name, item.new_iml_name)
        if updated_modules != original_modules:
            try:
                atomic_write_text(modules_xml, updated_modules)
            except OSError as error:
                return fields, WorkResult(
                    project_root=item.project_root,
                    status="failed",
                    reason=f"failed to write modules.xml: {error}",
                )
            fields.add("`modules.xml`: module fileurl/filepath")

    target_iml = item.idea_dir / item.new_iml_name
    try:
        rename_iml_file(item.iml_path, target_iml)
    except OSError as error:
        return fields, WorkResult(
            project_root=item.project_root,
            status="failed",
            reason=f"failed to rename IML file: {error}",
        )

    fields.add(f"`{item.old_iml_name}`: renamed to `{item.new_iml_name}`")
    return fields, None


def process_work_item(item: WorkItem) -> WorkResult:
    fields: set[str] = set()

    workspace_fields, workspace_failure = process_workspace_xml(item)
    if workspace_failure:
        return workspace_failure
    fields.update(workspace_fields)

    iml_fields, iml_failure = process_iml_metadata(item)
    if iml_failure:
        return iml_failure
    fields.update(iml_fields)

    if not fields:
        return WorkResult(project_root=item.project_root, status="unchanged")

    return WorkResult(project_root=item.project_root, status="changed", fields=fields)


def print_report(results: list[WorkResult]) -> None:
    by_status: dict[str, list[WorkResult]] = {key: [] for key, _label in RESULT_TYPES}
    for result in results:
        by_status[result.status].append(result)

    for status, label in RESULT_TYPES:
        items = sorted(by_status[status], key=lambda item: item.project_root.as_posix())
        print(f"- {label} ({len(items)}):")
        for item in items:
            if status == "changed":
                print(f"    - `{item.name}`. Fixed files and fields:")
                for field in sorted(item.fields):
                    print(f"        - {field}")
            elif status == "failed":
                print(f"    - `{item.name}`. Reason: {item.reason}")
            else:
                print(f"    - `{item.name}`")


def main() -> int:
    args = parse_args()
    start_dir = Path(args.start_dir).expanduser().resolve()

    if not start_dir.exists():
        print(f"Starting working directory does not exist: {start_dir}", file=sys.stderr)
        return 2
    if not start_dir.is_dir():
        print(f"Starting working directory is not a directory: {start_dir}", file=sys.stderr)
        return 2

    idea_dirs = collect_idea_dirs(start_dir)
    work_items, preflight_failures = build_work_items(idea_dirs)

    if preflight_failures:
        print("Aborted: preflight failed. No files were modified.")
        print_report(preflight_failures)
        return 1

    results = [process_work_item(item) for item in work_items]
    print_report(results)

    return 1 if any(result.status == "failed" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
