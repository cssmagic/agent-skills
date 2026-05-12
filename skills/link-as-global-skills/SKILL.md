---
name: link-as-global-skills
description: Use when developing AI agent skills in a local repository and needing to symlink that repository's skill directories into the global `~/.agents/skills` directory so local agents can discover and use them.
license: MIT
metadata:
  author: cssmagic
---

# Link As Global Skills

## Purpose

Link locally developed skills into the global skills directory for this machine:

- Start: a user-provided directory to search from, usually a skill development repository.
- Source: the parent directory containing sibling skill directories, detected from the first `SKILL.md` found under the start directory.
- Target: `~/.agents/skills` by default.
- Result: each first-level source skill directory is available as a symlink under the target directory.

This skill is for skill developers. Ordinary skill users should normally install skills with the skills CLI instead of using this workflow.



## Required Inputs

Each run needs a start directory.

Choose the start directory in this order:

- If the user provides a directory when invoking the skill, use it as the start directory.
- Otherwise, use the current working directory as the start directory.

From the start directory, search downward for the first `SKILL.md` file. The directory containing that file is a skill directory, and its sibling directories are also treated as skill directories. The parent of that detected skill directory is the source skills directory whose first-level child directories will be linked.

If the current conversation has no corresponding workspace and the user did not provide a start directory, ask the user for the start directory before running the script.

If no `SKILL.md` file is found under the start directory, ask the user for a different start directory before running the script again.



## Defaults

- Target directory: `~/.agents/skills`
- Link scope: all first-level directories in the source skills directory
- Existing symlink targets: update them to point at the current source directories
- Existing non-symlink targets: refuse to overwrite and stop
- Missing target directory: create it

Never delete source directories or target entries.



## Workflow

Normalize the start path and resolved source path before reporting or running commands.

Run the bundled script from this skill directory. When the current working directory is the desired start directory, the start argument may be omitted:

```bash
python3 scripts/link_as_global_skills.py
```

When the start directory is explicit:

```bash
python3 scripts/link_as_global_skills.py "/absolute/path/to/start"
```

To use a non-default global skills directory:

```bash
python3 scripts/link_as_global_skills.py "/absolute/path/to/start" --target-dir "/absolute/path/to/target/skills"
```

The script performs preflight checks before linking:

- start path exists and is a directory
- a `SKILL.md` file is found at or under the start path
- source skills directory contains at least one first-level directory
- target path is not an existing file
- each existing mapped target is either absent or a symlink



## Reporting

Summarize with:

- source skills directory
- target global skills directory
- linked skill count
- updated symlink count
- unchanged symlink count
- any skipped non-directory source entries

If the script refuses to overwrite an existing non-symlink target, report that path and ask the user how they want to handle it.
