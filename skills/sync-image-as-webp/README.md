English | [中文](README.zh.md)

# Sync Image As WebP

## Why Do I Need This Skill?

When publishing or reorganizing image assets, you may want a target directory that mirrors the source but stores PNG files as lossless WebP. Doing that by hand is tedious because the workflow has to preserve directory structure, copy non-PNG files, keep timestamps, and avoid accidental overwrites.

This skill gives an agent a cautious synchronization workflow for building that target tree. It is useful when you want a WebP-ready copy of an asset folder while keeping the source directory untouched.



## What Does It Do?

- Syncs a source directory into a target directory while preserving relative paths.
- Converts PNG files to same-name `.webp` files with lossless WebP.
- Copies non-PNG files unchanged.
- Creates empty target directories when needed.
- Preserves modification time and, on macOS when available, creation time.
- Verifies expected files, timestamps, directory differences, and source-only or target-only items.

The result is a separate target directory that mirrors the source structure, with PNG assets converted to WebP and the original source left unchanged.



## How to Install This Skill?

### With an AI Agent

In Codex, Claude Code, Cursor, OpenClaw, or another AI agent that supports skills, just say:

```text
Please help me install this skill:
https://github.com/cssmagic/agent-skills/tree/master/skills/sync-image-as-webp
```

### Manually

Run:

```bash
npx skills add cssmagic/agent-skills -s sync-image-as-webp -g
```



## How to Use It?

After installation, give your AI agent both the source directory and target directory:

```text
Invoke sync-image-as-webp
Source directory: /path/to/source-images
Target directory: /path/to/target-images
```

The skill refuses unsafe mappings before writing, including target path collisions, existing mapped files unless overwrite is explicitly allowed, and a target directory nested inside the source. After it finishes, the agent should report conversion, copy, timestamp, and verification results.



***

## More Useful Skills

The author of this skill has open-sourced several other useful skills. Take a look:<br>
https://github.com/cssmagic/agent-skills#readme
