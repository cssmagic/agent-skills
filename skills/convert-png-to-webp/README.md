English | [中文](README.zh.md)

# Convert PNG to WebP

## Why Do I Need This Skill?

PNG assets can quietly take up a lot of space. When you already know you want WebP replacements in the same directory tree, manually converting files, preserving timestamps, and deleting originals is repetitive and easy to get wrong.

This skill provides a cautious, script-backed workflow for converting PNG files to lossless WebP in place. It is useful when you need to reduce image asset disk usage while preserving original file timestamps.



## What Does It Do?

- Finds PNG files in one directory tree, case-insensitively.
- Converts each PNG to a same-directory, same-basename `.webp` file with lossless WebP.
- Preserves modification time and, on macOS, creation time.
- Refuses unsafe runs before writing, including existing mapped WebP files, target collisions, and symlinked PNG files.
- Deletes each source PNG only after its WebP replacement is complete.

The result is an in-place WebP asset tree with the original PNG files removed only after successful replacement.



## How to Install This Skill?

### With an AI Agent

In Codex, Claude Code, Cursor, OpenClaw, or another AI agent that supports skills, just say:

```text
Please help me install this skill:
https://github.com/cssmagic/agent-skills/tree/master/skills/convert-png-to-webp
```

### Manually

Run:

```bash
npx skills add cssmagic/agent-skills -s convert-png-to-webp -g
```



## How to Use It?

After installation, give your AI agent the directory you want to process:

```text
Invoke convert-png-to-webp
Process this directory: /path/to/image-directory
```

The skill checks prerequisites and refuses to overwrite existing mapped WebP files unless you explicitly allow overwrite behavior. After it finishes, the agent should report how many PNG files were found, converted, deleted, and whether timestamps were synced.



***

## More Useful Skills

The author of this skill has open-sourced several other useful skills. Take a look:<br>
https://github.com/cssmagic/agent-skills#readme
