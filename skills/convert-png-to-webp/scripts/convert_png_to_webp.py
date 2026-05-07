#!/usr/bin/env python3
"""Convert PNG files in a directory tree to lossless WebP in place."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PngMapping:
    source: Path
    target: Path
    relative_source: Path
    relative_target: Path


@dataclass
class Failure:
    path: Path
    kind: str
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert PNG files in a directory tree to same-location lossless WebP "
            "files, preserving timestamps and deleting originals after success."
        )
    )
    parser.add_argument("directory", help="Directory tree to process")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing mapped WebP files.",
    )
    return parser.parse_args()


def is_png(path: Path) -> bool:
    return path.suffix.lower() == ".png"


def target_for(source: Path) -> Path:
    return source.with_suffix(".webp")


def collect_mappings(directory: Path) -> list[PngMapping]:
    mappings: list[PngMapping] = []

    for root, dirnames, filenames in os.walk(directory):
        dirnames.sort()
        filenames.sort()
        root_path = Path(root)

        for filename in filenames:
            source = root_path / filename
            if not is_png(source):
                continue

            target = target_for(source)
            mappings.append(
                PngMapping(
                    source=source,
                    target=target,
                    relative_source=source.relative_to(directory),
                    relative_target=target.relative_to(directory),
                )
            )

    return mappings


def run_command(args: list[str]) -> tuple[int, str]:
    completed = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def find_case_conflict(path: Path) -> Path | None:
    parent = path.parent
    if not parent.exists() or not parent.is_dir():
        return None

    target_name = path.name
    target_fold = target_name.casefold()
    for child in parent.iterdir():
        if child.name.casefold() == target_fold and child.name != target_name:
            return child
    return None


def validate_preflight(
    mappings: list[PngMapping],
    overwrite: bool,
) -> list[str]:
    errors: list[str] = []
    by_exact_target: dict[str, list[PngMapping]] = {}
    by_casefold_target: dict[str, list[PngMapping]] = {}

    for mapping in mappings:
        exact_key = str(mapping.relative_target)
        casefold_key = exact_key.casefold()
        by_exact_target.setdefault(exact_key, []).append(mapping)
        by_casefold_target.setdefault(casefold_key, []).append(mapping)

    for target_rel, colliding in sorted(by_exact_target.items()):
        if len(colliding) > 1:
            sources = ", ".join(str(item.relative_source) for item in colliding)
            errors.append(f"target collision at {target_rel}: {sources}")

    for _target_rel, colliding in sorted(by_casefold_target.items()):
        exact_targets = {str(item.relative_target) for item in colliding}
        if len(exact_targets) > 1:
            sources = ", ".join(str(item.relative_source) for item in colliding)
            targets = ", ".join(sorted(exact_targets))
            errors.append(f"case-insensitive target collision at {targets}: {sources}")

    for mapping in mappings:
        if mapping.source.is_symlink():
            errors.append(f"refusing symlinked PNG: {mapping.source}")

        if mapping.target.exists():
            if mapping.target.is_dir():
                errors.append(f"target WebP path exists as directory: {mapping.target}")
            elif mapping.target.is_symlink():
                errors.append(f"target WebP path exists as symlink: {mapping.target}")
            elif not overwrite:
                errors.append(
                    "target WebP already exists: "
                    f"png={mapping.source} webp={mapping.target}"
                )

        case_conflict = find_case_conflict(mapping.target)
        if case_conflict:
            errors.append(
                "case-insensitive target WebP conflict: "
                f"png={mapping.source} webp={mapping.target} existing={case_conflict}"
            )

    return errors


def get_creation_time(source: Path) -> tuple[str | None, str | None]:
    get_file_info = shutil.which("GetFileInfo")
    if not get_file_info:
        return None, "GetFileInfo unavailable"

    code, output = run_command([get_file_info, "-d", str(source)])
    if code != 0 or not output:
        return None, f"GetFileInfo failed for {source}: {output}"

    return output, None


def set_creation_time(target: Path, created: str) -> str | None:
    set_file = shutil.which("SetFile")
    if not set_file:
        return "SetFile unavailable"

    code, output = run_command([set_file, "-d", created, str(target)])
    if code != 0:
        return f"SetFile failed for {target}: {output}"

    return None


def stat_birthtime(path: Path) -> int | None:
    birthtime = getattr(path.stat(), "st_birthtime", None)
    if birthtime is None:
        return None
    return int(birthtime)


def make_temp_path(target: Path) -> Path:
    return target.with_name(f".{target.name}.tmp-{os.getpid()}-{uuid.uuid4().hex}")


def cleanup(path: Path) -> None:
    try:
        if path.exists() or path.is_symlink():
            path.unlink()
    except OSError:
        pass


def convert_one(
    cwebp: str,
    mapping: PngMapping,
    sync_creation_time: bool,
) -> tuple[str | None, str | None]:
    temp = make_temp_path(mapping.target)
    created, creation_error = (None, None)

    if sync_creation_time:
        created, creation_error = get_creation_time(mapping.source)
        if creation_error:
            return "timestamp", creation_error

    code, output = run_command(
        [cwebp, "-quiet", "-lossless", str(mapping.source), "-o", str(temp)]
    )
    if code != 0:
        cleanup(temp)
        return "conversion", f"cwebp failed: {output}"

    if not temp.is_file() or temp.stat().st_size <= 0:
        cleanup(temp)
        return "conversion", "converted WebP is missing or empty"

    try:
        shutil.copystat(mapping.source, temp, follow_symlinks=False)
    except OSError as exc:
        cleanup(temp)
        return "timestamp", f"mtime sync failed: {exc}"

    if sync_creation_time and created:
        creation_error = set_creation_time(temp, created)
        if creation_error:
            cleanup(temp)
            return "timestamp", creation_error

    try:
        os.replace(temp, mapping.target)
    except OSError as exc:
        cleanup(temp)
        return "write", f"final WebP replace failed: {exc}"

    source_mtime = int(mapping.source.stat().st_mtime)
    target_mtime = int(mapping.target.stat().st_mtime)
    if source_mtime != target_mtime:
        return "timestamp", f"mtime verification failed: source={source_mtime} target={target_mtime}"

    if sync_creation_time:
        source_birth = stat_birthtime(mapping.source)
        target_birth = stat_birthtime(mapping.target)
        if source_birth is not None and target_birth is not None and source_birth != target_birth:
            return "timestamp", f"creation time verification failed: source={source_birth} target={target_birth}"

    try:
        mapping.source.unlink()
    except OSError as exc:
        return "delete", f"original PNG delete failed: {exc}"

    return None, None


def main() -> int:
    args = parse_args()

    cwebp = shutil.which("cwebp")
    if not cwebp:
        print("error: cwebp is required but was not found on PATH", file=sys.stderr)
        return 2

    directory = Path(args.directory).expanduser().resolve()
    if not directory.exists() or not directory.is_dir():
        print(f"error: directory does not exist: {directory}", file=sys.stderr)
        return 2

    sync_creation_time = False
    creation_time_status = "skipped"
    if sys.platform == "darwin":
        if not shutil.which("GetFileInfo") or not shutil.which("SetFile"):
            print(
                "error: GetFileInfo and SetFile are required on macOS to preserve creation times",
                file=sys.stderr,
            )
            return 2
        sync_creation_time = True
        creation_time_status = "yes"

    mappings = collect_mappings(directory)
    preflight_errors = validate_preflight(mappings, args.overwrite)
    if preflight_errors:
        print("preflight failed:", file=sys.stderr)
        for error in preflight_errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    converted_count = 0
    deleted_count = 0
    conversion_failures = 0
    timestamp_failures = 0
    write_failures = 0
    delete_failures = 0
    failures: list[Failure] = []

    for mapping in mappings:
        kind, error = convert_one(cwebp, mapping, sync_creation_time)
        if error:
            if kind == "conversion":
                conversion_failures += 1
            elif kind == "timestamp":
                timestamp_failures += 1
            elif kind == "write":
                write_failures += 1
            elif kind == "delete":
                delete_failures += 1

            failures.append(Failure(mapping.relative_source, kind or "unknown", error))
            print(f"failed: {mapping.source}: {error}", file=sys.stderr)
            continue

        converted_count += 1
        deleted_count += 1

    print(f"directory={directory}")
    print(f"png_found={len(mappings)}")
    print(f"converted_webp_files={converted_count}")
    print(f"deleted_original_png_files={deleted_count}")
    print(f"creation_time_synced={creation_time_status}")
    print(f"conversion_failures={conversion_failures}")
    print(f"timestamp_failures={timestamp_failures}")
    print(f"write_failures={write_failures}")
    print(f"delete_failures={delete_failures}")
    print(f"failed_files={len(failures)}")

    if failures:
        print("failed_file_list:")
        for failure in failures:
            print(f"- {failure.path}: {failure.kind}: {failure.reason}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
