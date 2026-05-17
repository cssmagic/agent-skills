---
name: fix-svg-aspect-ratio
description: "Use when SVG files render with a distorted aspect ratio, especially vector SVG assets exported by Figma Desktop MCP."
license: MIT
metadata:
  author: cssmagic
---

# Fix SVG Aspect Ratio

## Purpose

Fix SVG files whose root `<svg>` attributes can make the artwork stretch instead of preserving its natural aspect ratio.

This skill is intentionally small and script-backed so other skills can call it as an atomic utility.



## Required Input

Each run needs one path:

- A single SVG file.
- A directory tree containing SVG files.

If the path is missing or ambiguous, ask the user for it before running commands.

Normalize `~` and relative paths to absolute paths before reporting or running the script.



## Defaults

When given a directory, scan `.svg` files recursively and case-insensitively.

Modify files in place.

Output a non-interactive report every run. This is safe for atomic calls because the script never prompts for input.

Do not infer dimensions from paths, CSS, rendered output, or child elements. If a file has no valid `viewBox`, report it as unsupported.



## Fixes Applied

For each valid SVG root with a valid `viewBox`, set these root `<svg>` attributes:

- `preserveAspectRatio="xMidYMid meet"`
- `width` from the third `viewBox` number
- `height` from the fourth `viewBox` number

Also remove `display: block` from the root `style` attribute. If the style attribute has other declarations, keep them.

Do not modify internal SVG content such as `<g>`, `<path>`, `<defs>`, gradients, ids, or fill values.



## Workflow

Set the path from the user's provided input:

```bash
target="/absolute/path/to/file-or-directory"
```

Run the bundled script from this skill directory:

```bash
python3 scripts/fix_svg_aspect_ratio.py "$target"
```

The script validates each SVG before writing, writes to a temporary file beside the source, then atomically replaces the original file.



## Reporting

The script outputs every SVG file grouped by result type:

- `Fixed` - processing succeeded and the file was changed.
- `Already Correct` - the SVG already matched the expected root attributes.
- `Unsupported` - the SVG was readable but not safe to process, such as a missing or invalid `viewBox`.
- `Failed` - the script could not read, parse, or write the file.

Example output:

```text
- Fixed (1):
    - /absolute/path/to/file-1.svg
- Already Correct (2):
    - /absolute/path/to/file-2.svg
    - /absolute/path/to/file-3.svg
- Unsupported (1):
    - /absolute/path/to/file-4.svg: missing or invalid viewBox
- Failed (4):
    - /absolute/path/to/file-5.svg: not valid UTF-8: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
    - /absolute/path/to/file-6.svg: XML parse failed: mismatched tag: line 1, column 10
    - /absolute/path/to/file-7.svg: root SVG start tag was not found
    - /absolute/path/to/file-8.svg: write failed: [Errno 13] Permission denied
```
