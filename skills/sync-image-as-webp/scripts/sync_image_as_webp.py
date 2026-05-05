#!/usr/bin/env python3
"""Sync a directory tree, converting PNG files to lossless WebP."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileMapping:
    source: Path
    target: Path
    relative_source: Path
    relative_target: Path
    is_png: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert PNG files to lossless WebP while copying non-PNG files, "
            "preserving directory structure and timestamps."
        )
    )
    parser.add_argument("source", help="Source directory")
    parser.add_argument("target", help="Target directory")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing mapped target files.",
    )
    return parser.parse_args()


def resolve_target(path: Path) -> Path:
    if path.exists():
        return path.resolve()

    parent = path.parent
    while not parent.exists() and parent != parent.parent:
        parent = parent.parent

    return parent.resolve() / path.relative_to(parent)


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def is_png(path: Path) -> bool:
    return path.suffix.lower() == ".png"


def target_relative_path(relative_source: Path) -> Path:
    if is_png(relative_source):
        return relative_source.with_suffix(".webp")
    return relative_source


def collect_mappings(source: Path, target: Path) -> tuple[list[Path], list[FileMapping]]:
    dirs: list[Path] = []
    mappings: list[FileMapping] = []

    for root, dirnames, filenames in os.walk(source):
        root_path = Path(root)
        dirnames.sort()
        filenames.sort()

        relative_dir = root_path.relative_to(source)
        dirs.append(relative_dir)

        for filename in filenames:
            source_file = root_path / filename
            relative_source = source_file.relative_to(source)
            relative_target = target_relative_path(relative_source)
            mappings.append(
                FileMapping(
                    source=source_file,
                    target=target / relative_target,
                    relative_source=relative_source,
                    relative_target=relative_target,
                    is_png=is_png(relative_source),
                )
            )

    return dirs, mappings


def validate_preflight(
    source: Path,
    target: Path,
    dirs: list[Path],
    mappings: list[FileMapping],
    overwrite: bool,
) -> list[str]:
    errors: list[str] = []

    if is_relative_to(target, source):
        errors.append(f"target must not be inside source: {target}")

    by_exact_target: dict[str, list[FileMapping]] = {}
    by_casefold_target: dict[str, list[FileMapping]] = {}

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

    for relative_dir in dirs:
        target_dir = target / relative_dir
        if target_dir.exists() and not target_dir.is_dir():
            errors.append(f"target directory path exists as non-directory: {target_dir}")

    for mapping in mappings:
        if mapping.target.exists():
            if mapping.target.is_dir():
                errors.append(f"target file path exists as directory: {mapping.target}")
            elif not overwrite:
                errors.append(f"target already exists: {mapping.target}")

    return errors


def run_command(args: list[str]) -> tuple[int, str]:
    completed = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def set_creation_time(source: Path, target: Path) -> tuple[bool, str | None]:
    get_file_info = shutil.which("GetFileInfo")
    set_file = shutil.which("SetFile")
    if not get_file_info or not set_file:
        return False, "GetFileInfo/SetFile unavailable"

    get_code, created = run_command([get_file_info, "-d", str(source)])
    if get_code != 0 or not created:
        return False, f"GetFileInfo failed for {source}: {created}"

    set_code, output = run_command([set_file, "-d", created, str(target)])
    if set_code != 0:
        return False, f"SetFile failed for {target}: {output}"

    return True, None


def stat_birthtime(path: Path) -> int | None:
    birthtime = getattr(path.stat(), "st_birthtime", None)
    if birthtime is None:
        return None
    return int(birthtime)


def list_relative_dirs(root: Path) -> set[Path]:
    if not root.exists():
        return set()
    return {Path(dirpath).relative_to(root) for dirpath, _, _ in os.walk(root)}


def list_relative_files(root: Path) -> set[Path]:
    if not root.exists():
        return set()

    files: set[Path] = set()
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            files.add((Path(dirpath) / filename).relative_to(root))
    return files


def main() -> int:
    args = parse_args()

    cwebp = shutil.which("cwebp")
    if not cwebp:
        print("error: cwebp is required but was not found on PATH", file=sys.stderr)
        return 2

    source = Path(args.source).expanduser().resolve()
    target = resolve_target(Path(args.target).expanduser())

    if not source.exists() or not source.is_dir():
        print(f"error: source directory does not exist: {source}", file=sys.stderr)
        return 2

    dirs, mappings = collect_mappings(source, target)
    preflight_errors = validate_preflight(source, target, dirs, mappings, args.overwrite)
    if preflight_errors:
        print("preflight failed:", file=sys.stderr)
        for error in preflight_errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    png_count = sum(1 for mapping in mappings if mapping.is_png)
    non_png_count = len(mappings) - png_count
    converted_count = 0
    copied_count = 0
    dirs_created = 0
    command_failures = 0
    timestamp_failures = 0
    creation_time_diff = 0
    mtime_diff = 0
    missing_targets = 0

    creation_time_warning = None
    can_sync_creation_time = True
    if sys.platform != "darwin":
        can_sync_creation_time = False
        creation_time_warning = "not macOS; creation times were not synced"
    elif not shutil.which("GetFileInfo") or not shutil.which("SetFile"):
        can_sync_creation_time = False
        creation_time_warning = "GetFileInfo/SetFile unavailable; creation times were not synced"

    for relative_dir in dirs:
        target_dir = target / relative_dir
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            dirs_created += 1
        else:
            target_dir.mkdir(parents=True, exist_ok=True)

    for mapping in mappings:
        mapping.target.parent.mkdir(parents=True, exist_ok=True)

        if mapping.is_png:
            code, output = run_command(
                [cwebp, "-quiet", "-lossless", str(mapping.source), "-o", str(mapping.target)]
            )
            if code != 0:
                command_failures += 1
                print(f"conversion failed: {mapping.source} -> {mapping.target}", file=sys.stderr)
                if output:
                    print(output, file=sys.stderr)
                continue
            converted_count += 1
        else:
            try:
                shutil.copy2(mapping.source, mapping.target)
            except OSError as exc:
                command_failures += 1
                print(f"copy failed: {mapping.source} -> {mapping.target}: {exc}", file=sys.stderr)
                continue
            copied_count += 1

        try:
            shutil.copystat(mapping.source, mapping.target)
        except OSError as exc:
            timestamp_failures += 1
            print(f"mtime sync failed: {mapping.source} -> {mapping.target}: {exc}", file=sys.stderr)
            continue

        if can_sync_creation_time:
            synced, warning = set_creation_time(mapping.source, mapping.target)
            if not synced:
                timestamp_failures += 1
                if warning:
                    print(f"creation time sync failed: {warning}", file=sys.stderr)

    expected_targets = {mapping.relative_target for mapping in mappings}
    actual_target_files = list_relative_files(target)
    source_dirs = set(dirs)
    target_dirs = list_relative_dirs(target)

    for mapping in mappings:
        if not mapping.target.is_file():
            missing_targets += 1
            continue

        source_mtime = int(mapping.source.stat().st_mtime)
        target_mtime = int(mapping.target.stat().st_mtime)
        if source_mtime != target_mtime:
            mtime_diff += 1

        if can_sync_creation_time:
            source_birth = stat_birthtime(mapping.source)
            target_birth = stat_birthtime(mapping.target)
            if source_birth is not None and target_birth is not None and source_birth != target_birth:
                creation_time_diff += 1

    target_only_files = sorted(actual_target_files - expected_targets)
    source_only_dirs = sorted(source_dirs - target_dirs)
    target_only_dirs = sorted(target_dirs - source_dirs)

    print(f"source={source}")
    print(f"target={target}")
    print(f"source_png_files={png_count}")
    print(f"source_non_png_files={non_png_count}")
    print(f"source_dirs={len(source_dirs)}")
    print(f"converted_png_files={converted_count}")
    print(f"copied_non_png_files={copied_count}")
    print(f"dirs_created={dirs_created}")
    print(f"missing_targets={missing_targets}")
    print(f"mtime_diff={mtime_diff}")
    print(f"creation_time_synced={'yes' if can_sync_creation_time else 'no'}")
    if can_sync_creation_time:
        print(f"creation_time_diff={creation_time_diff}")
    else:
        print("creation_time_diff=skipped")
    print(f"command_failures={command_failures}")
    print(f"timestamp_failures={timestamp_failures}")
    print(f"target_only_files={len(target_only_files)}")
    print(f"source_only_dirs={len(source_only_dirs)}")
    print(f"target_only_dirs={len(target_only_dirs)}")

    if creation_time_warning:
        print(f"warning: {creation_time_warning}")

    if target_only_files:
        print("target_only_file_list:")
        for path in target_only_files:
            print(f"- {path}")

    if source_only_dirs:
        print("source_only_dir_list:")
        for path in source_only_dirs:
            print(f"- {path}")

    if target_only_dirs:
        print("target_only_dir_list:")
        for path in target_only_dirs:
            print(f"- {path}")

    if (
        command_failures
        or timestamp_failures
        or missing_targets
        or mtime_diff
        or creation_time_diff
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
