#!/usr/bin/env python3
"""Symlink first-level skill directories into a global skills directory."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import Optional


def expand_path(raw_path: str) -> Path:
	return Path(raw_path).expanduser().resolve()


def find_source_dir(start_dir: Path) -> Path:
	if not start_dir.exists():
		raise ValueError(f"Start directory does not exist: {start_dir}")

	if not start_dir.is_dir():
		raise ValueError(f"Start path is not a directory: {start_dir}")

	for root, dir_names, file_names in os.walk(start_dir):
		dir_names.sort(key=str.lower)
		file_names.sort(key=str.lower)

		if "SKILL.md" in file_names:
			return Path(root).resolve().parent

	raise ValueError(f"Could not find a SKILL.md file under: {start_dir}")


def iter_source_entries(source_dir: Path) -> tuple[list[Path], list[Path]]:
	directories: list[Path] = []
	skipped: list[Path] = []

	for entry in sorted(source_dir.iterdir(), key=lambda path: path.name.lower()):
		if entry.is_dir():
			directories.append(entry)
		else:
			skipped.append(entry)

	return directories, skipped


def preflight(source_dirs: list[Path], target_dir: Path) -> list[Path]:
	conflicts: list[Path] = []

	if target_dir.exists() and not target_dir.is_dir():
		conflicts.append(target_dir)

	for source in source_dirs:
		target = target_dir / source.name
		if target.exists() and not target.is_symlink():
			conflicts.append(target)

	return conflicts


def link_skills(source_dirs: list[Path], target_dir: Path) -> tuple[int, int, int]:
	created = 0
	updated = 0
	unchanged = 0

	target_dir.mkdir(parents=True, exist_ok=True)

	for source in source_dirs:
		target = target_dir / source.name
		existing_link = None

		if target.is_symlink():
			existing_link = Path(os.readlink(target)).expanduser()
			if not existing_link.is_absolute():
				existing_link = (target.parent / existing_link).resolve()
			else:
				existing_link = existing_link.resolve()

		if existing_link == source:
			unchanged += 1
			continue

		if target.is_symlink():
			target.unlink()
			updated += 1
		else:
			created += 1

		target.symlink_to(source, target_is_directory=True)

	return created, updated, unchanged


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Symlink first-level skill directories into a global skills directory.",
	)
	parser.add_argument(
		"start_dir",
		nargs="?",
		help="Directory to search from. The first SKILL.md found under it determines the source.",
	)
	parser.add_argument(
		"--target-dir",
		default="~/.agents/skills",
		help="Global skills directory to link into. Defaults to ~/.agents/skills.",
	)
	return parser


def main(argv: Optional[list[str]] = None) -> int:
	args = build_parser().parse_args(argv)

	try:
		start_dir = expand_path(args.start_dir) if args.start_dir else Path.cwd().resolve()
		source_dir = find_source_dir(start_dir)
	except ValueError as error:
		print(error, file=sys.stderr)
		return 2

	target_dir = expand_path(args.target_dir)

	source_dirs, skipped = iter_source_entries(source_dir)

	if not source_dirs:
		print(f"No first-level skill directories found in: {source_dir}", file=sys.stderr)
		return 2

	conflicts = preflight(source_dirs, target_dir)
	if conflicts:
		print("Refusing to overwrite existing non-symlink target paths:", file=sys.stderr)
		for conflict in conflicts:
			print(f"- {conflict}", file=sys.stderr)
		return 1

	created, updated, unchanged = link_skills(source_dirs, target_dir)

	print(f"Source skills directory: {source_dir}")
	print(f"Target global skills directory: {target_dir}")
	print(f"Linked skill count: {len(source_dirs)}")
	print(f"Created symlinks: {created}")
	print(f"Updated symlinks: {updated}")
	print(f"Unchanged symlinks: {unchanged}")

	if skipped:
		print(f"Skipped non-directory entries: {len(skipped)}")
		for entry in skipped:
			print(f"- {entry.name}")
	else:
		print("Skipped non-directory entries: 0")

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
