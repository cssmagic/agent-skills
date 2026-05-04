---
name: sync-image-as-webp
description: Use this skill when converting a source directory tree of PNG files to lossless WebP with `cwebp`, copying all non-PNG files unchanged, preserving directory structure, syncing macOS creation/modification times, and analyzing Finder item-count differences. If source or target directory is not provided, ask the user before proceeding.
---

# Sync Image As WebP

## Purpose

Convert a source directory into a target directory while preserving structure:

- Convert PNG files to same-name `.webp` using lossless WebP.
- Copy all non-PNG files unchanged.
- Preserve empty directories when matching Finder item counts matters.
- Optionally sync target file creation time and modification time from source files.
- Verify file, directory, timestamp, and item-count differences.



## Required Inputs

Each run needs:

- Source directory
- Target directory

If either directory is missing or ambiguous, ask the user for the missing path before running commands.

Do not infer a target directory from the source directory unless the user explicitly asks for that behavior.

After paths are known, normalize `~` and relative paths to absolute paths before reporting or running destructive-looking operations.



## Defaults

Use these mappings:

- Source PNG file -> target `.webp`
- Source non-PNG file -> target same filename
- Source directory -> target same relative directory

Treat PNG extensions case-insensitively unless the user explicitly asks for case-sensitive matching.

Never delete files unless the user explicitly asks.



## Prerequisites

Prefer the official WebP CLI:

```bash
command -v cwebp
```

On macOS, timestamp syncing uses:

```bash
command -v GetFileInfo
command -v SetFile
```

If writing outside the current workspace, request approval before running commands that create files, copy files, convert images, or update metadata.



## Workflow

Set source and target directories from the user's provided paths:

```bash
src="/absolute/path/to/source"
dst="/absolute/path/to/target"
```

Inspect counts before writing:

```bash
find "$src" -type f -iname '*.png' | wc -l
find "$src" -type f ! -iname '*.png' | wc -l
find "$src" -type d | wc -l
```

Create all directories, including empty ones:

```bash
while IFS= read -r -d '' d; do
  rel="${d#$src/}"
  if [[ "$d" == "$src" ]]; then
    mkdir -p "$dst"
  else
    mkdir -p "$dst/$rel"
  fi
done < <(find "$src" -type d -print0)
```

Convert PNG files to lossless WebP:

```bash
while IFS= read -r -d '' f; do
  rel="${f#$src/}"
  out="$dst/${rel%.*}.webp"
  mkdir -p "$(dirname "$out")"
  cwebp -quiet -lossless "$f" -o "$out"
done < <(find "$src" -type f -iname '*.png' -print0)
```

Copy all non-PNG files unchanged:

```bash
while IFS= read -r -d '' f; do
  rel="${f#$src/}"
  out="$dst/$rel"
  mkdir -p "$(dirname "$out")"
  cp -p "$f" "$out"
done < <(find "$src" -type f ! -iname '*.png' -print0)
```



## Sync Timestamps

For each source file, map to its target file and sync:

- modification time with `touch -r`
- macOS creation time with `GetFileInfo` + `SetFile`

```bash
synced=0
failed=0

while IFS= read -r -d '' f; do
  rel="${f#$src/}"

  if [[ "$rel" =~ \.[Pp][Nn][Gg]$ ]]; then
    out="$dst/${rel%.*}.webp"
  else
    out="$dst/$rel"
  fi

  if [[ ! -f "$out" ]]; then
    printf 'missing target: %s\n' "$out" >&2
    failed=$((failed + 1))
    continue
  fi

  touch -r "$f" "$out"

  created="$(GetFileInfo -d "$f")"
  SetFile -d "$created" "$out"

  synced=$((synced + 1))
done < <(find "$src" -type f -print0)

printf 'synced=%d\nfailed=%d\n' "$synced" "$failed"
```



## Verification

Verify expected target files exist:

```bash
missing=0

while IFS= read -r -d '' f; do
  rel="${f#$src/}"

  if [[ "$rel" =~ \.[Pp][Nn][Gg]$ ]]; then
    out="$dst/${rel%.*}.webp"
  else
    out="$dst/$rel"
  fi

  if [[ ! -f "$out" ]]; then
    printf 'missing: %s\n' "$out"
    missing=$((missing + 1))
  fi
done < <(find "$src" -type f -print0)

printf 'missing=%d\n' "$missing"
```

Verify timestamp parity:

```bash
checked=0
mtime_diff=0
creation_time_diff=0

while IFS= read -r -d '' f; do
  rel="${f#$src/}"

  if [[ "$rel" =~ \.[Pp][Nn][Gg]$ ]]; then
    out="$dst/${rel%.*}.webp"
  else
    out="$dst/$rel"
  fi

  src_m="$(stat -f '%m' "$f")"
  out_m="$(stat -f '%m' "$out")"
  [[ "$src_m" == "$out_m" ]] || mtime_diff=$((mtime_diff + 1))

  src_b="$(stat -f '%B' "$f")"
  out_b="$(stat -f '%B' "$out")"
  [[ "$src_b" == "$out_b" ]] || creation_time_diff=$((creation_time_diff + 1))

  checked=$((checked + 1))
done < <(find "$src" -type f -print0)

printf 'checked=%d\nmtime_diff=%d\ncreation_time_diff=%d\n' \
  "$checked" "$mtime_diff" "$creation_time_diff"
```



## Finder Item Count Analysis

Finder item counts may include both files and folders. If Finder shows an item-count difference, compare directory trees as well as files.

```bash
printf 'source files: '
find "$src" -type f | wc -l

printf 'target files: '
find "$dst" -type f | wc -l

printf 'source dirs: '
find "$src" -type d | wc -l

printf 'target dirs: '
find "$dst" -type d | wc -l
```

Find directories only present on one side:

```bash
src_dirs="$(mktemp)"
dst_dirs="$(mktemp)"

find "$src" -type d -print | sed "s#^$src#.#" | sort > "$src_dirs"
find "$dst" -type d -print | sed "s#^$dst#.#" | sort > "$dst_dirs"

printf 'dirs only in source:\n'
comm -23 "$src_dirs" "$dst_dirs"

printf 'dirs only in target:\n'
comm -13 "$src_dirs" "$dst_dirs"
```

If file counts match but directory counts differ, the usual cause is an empty directory that was not created during file-driven copy/conversion.



## Reporting

Summarize with:

- source directory
- target directory
- PNG converted count
- non-PNG copied count
- directories created count if relevant
- missing target count
- timestamp diff counts
- any source-only or target-only directories/files
