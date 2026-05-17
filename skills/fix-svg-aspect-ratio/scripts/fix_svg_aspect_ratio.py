#!/usr/bin/env python3
"""Fix root SVG attributes that can distort aspect ratio."""

from __future__ import annotations

import argparse
import html
import math
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


PRESERVE_ASPECT_RATIO = "xMidYMid meet"
SVG_START_RE = re.compile(r"<(?P<tag>(?:[A-Za-z_][\w.-]*:)?svg)\b", re.IGNORECASE)
ATTR_RE = re.compile(
    r"(?P<name>[A-Za-z_][\w:.-]*)\s*=\s*(?P<quote>[\"'])(?P<value>.*?)(?P=quote)",
    re.DOTALL,
)
RESULT_TYPES = (
    ("fixed", "Fixed"),
    ("already_correct", "Already Correct"),
    ("unsupported", "Unsupported"),
    ("failed", "Failed"),
)


@dataclass
class Result:
    path: Path
    status: str
    reason: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fix root SVG attributes so SVGs preserve their viewBox aspect ratio."
    )
    parser.add_argument("path", help="SVG file or directory tree to process")
    return parser.parse_args()


def is_svg_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".svg"


def collect_svg_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]

    files: list[Path] = []
    for root, dirnames, filenames in os.walk(path):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            candidate = Path(root) / filename
            if is_svg_file(candidate):
                files.append(candidate)
    return files


def local_name(tag: str) -> str:
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    return tag.rsplit(":", 1)[-1]


def parse_view_box(value: str | None) -> tuple[str, str] | None:
    if not value:
        return None

    parts = [part for part in re.split(r"[\s,]+", value.strip()) if part]
    if len(parts) != 4:
        return None

    try:
        width = float(parts[2])
        height = float(parts[3])
    except ValueError:
        return None

    if not math.isfinite(width) or not math.isfinite(height) or width <= 0 or height <= 0:
        return None

    return parts[2], parts[3]


def find_svg_start_tag(text: str) -> tuple[re.Match[str], int] | None:
    match = SVG_START_RE.search(text)
    if not match:
        return None

    quote: str | None = None
    index = match.end()
    while index < len(text):
        char = text[index]
        if quote:
            if char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char == ">":
            return match, index + 1
        index += 1

    return None


def parse_root_attrs(start_tag: str) -> tuple[str, list[tuple[str, str]], bool]:
    tag_match = SVG_START_RE.match(start_tag)
    if not tag_match:
        raise ValueError("root SVG start tag was not found")

    tag_name = tag_match.group("tag")
    inner = start_tag[tag_match.end() : -1]
    self_closing = inner.rstrip().endswith("/")
    if self_closing:
        inner = inner.rstrip()[:-1]

    attrs: list[tuple[str, str]] = []
    for attr_match in ATTR_RE.finditer(inner):
        attrs.append((attr_match.group("name"), attr_match.group("value")))

    return tag_name, attrs, self_closing


def strip_display_block(style: str) -> str | None:
    kept: list[str] = []

    for declaration in style.split(";"):
        item = declaration.strip()
        if not item:
            continue

        if ":" not in item:
            kept.append(item)
            continue

        prop, value = item.split(":", 1)
        prop_normalized = prop.strip().lower()
        value_normalized = re.sub(r"\s+", " ", value.strip().lower())
        if prop_normalized == "display" and value_normalized in {"block", "block !important"}:
            continue

        kept.append(f"{prop.strip()}: {value.strip()}")

    if not kept:
        return None

    return "; ".join(kept) + ";"


def build_start_tag(
    tag_name: str,
    attrs: list[tuple[str, str]],
    self_closing: bool,
    width: str,
    height: str,
) -> tuple[str, bool]:
    updates = {
        "preserveAspectRatio": PRESERVE_ASPECT_RATIO,
        "width": width,
        "height": height,
    }
    seen: set[str] = set()
    changed = False
    rebuilt: list[tuple[str, str]] = []

    for name, value in attrs:
        if name == "style":
            next_value = strip_display_block(value)
            if next_value is None:
                changed = True
                continue
            if next_value != value:
                changed = True
            rebuilt.append((name, next_value))
            continue

        if name in updates:
            seen.add(name)
            next_value = updates[name]
            if value != next_value:
                changed = True
            rebuilt.append((name, next_value))
            continue

        rebuilt.append((name, value))

    for name in ("preserveAspectRatio", "width", "height"):
        if name not in seen:
            rebuilt.append((name, updates[name]))
            changed = True

    attr_text = "".join(
        f' {name}="{html.escape(value, quote=True)}"' for name, value in rebuilt
    )
    closing = " />" if self_closing else ">"
    return f"<{tag_name}{attr_text}{closing}", changed


def write_atomic(path: Path, text: str) -> None:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        handle.write(text)

    try:
        shutil.copystat(path, temp_path, follow_symlinks=False)
        os.replace(temp_path, path)
    except OSError:
        try:
            temp_path.unlink()
        except OSError:
            pass
        raise


def fix_one(path: Path) -> Result:
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return Result(path, "failed", f"not valid UTF-8: {exc}")
    except OSError as exc:
        return Result(path, "failed", f"read failed: {exc}")

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        return Result(path, "failed", f"XML parse failed: {exc}")

    if local_name(root.tag) != "svg":
        return Result(path, "unsupported", "root element is not <svg>")

    dimensions = parse_view_box(root.attrib.get("viewBox"))
    if not dimensions:
        return Result(path, "unsupported", "missing or invalid viewBox")

    tag_location = find_svg_start_tag(text)
    if not tag_location:
        return Result(path, "failed", "root SVG start tag was not found")

    start_match, tag_end = tag_location
    start_tag = text[start_match.start() : tag_end]

    try:
        tag_name, attrs, self_closing = parse_root_attrs(start_tag)
    except ValueError as exc:
        return Result(path, "failed", str(exc))

    next_start_tag, changed = build_start_tag(
        tag_name,
        attrs,
        self_closing,
        width=dimensions[0],
        height=dimensions[1],
    )

    if not changed and start_tag == next_start_tag:
        return Result(path, "already_correct")

    next_text = text[: start_match.start()] + next_start_tag + text[tag_end:]

    try:
        write_atomic(path, next_text)
    except OSError as exc:
        return Result(path, "failed", f"write failed: {exc}")

    return Result(path, "fixed")


def print_result_group(results: list[Result], status: str, label: str, stream) -> None:
    matching = [result for result in results if result.status == status]
    count = len(matching)
    suffix = ":" if count else ""
    print(f"- {label} ({count}){suffix}", file=stream)

    if not matching:
        return

    for result in matching:
        if result.reason:
            print(f"  - {result.path}: {result.reason}", file=stream)
        else:
            print(f"  - {result.path}", file=stream)


def print_results(results: list[Result]) -> None:
    for status, label in RESULT_TYPES:
        print_result_group(results, status, label, sys.stdout)


def main() -> int:
    args = parse_args()
    target = Path(args.path).expanduser().resolve()

    if not target.exists():
        print(f"error: path does not exist: {target}", file=sys.stderr)
        return 2

    if not target.is_file() and not target.is_dir():
        print(f"error: path is not a file or directory: {target}", file=sys.stderr)
        return 2

    files = collect_svg_files(target)
    results = [fix_one(path) for path in files]
    print_results(results)

    has_problem = any(result.status in {"unsupported", "failed"} for result in results)
    return 1 if has_problem else 0


if __name__ == "__main__":
    raise SystemExit(main())
