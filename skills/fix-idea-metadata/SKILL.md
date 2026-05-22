---
name: fix-idea-metadata
description: "Use when a local JetBrains IDE project was moved or copied and its `.idea` metadata may still contain stale absolute project paths."
license: MIT
metadata:
  author: cssmagic
---

# Fix IDEA Metadata

## Purpose

Fix known `.idea` metadata fields that can keep stale absolute project paths after a local repository is moved.

This skill is intentionally script-backed. It should only repair fields that are known to contain movable local project paths.



## Required Input

Each run needs one starting working directory.

If the starting directory is missing from the user's request and the conversation context does not clearly provide it, ask the user for the path before running commands.

Normalize `~` and relative paths to an absolute path before reporting or running the script.



## Fixes Applied

Search recursively under the starting directory for `.idea` directories. Treat each `.idea` parent directory as one work item.

For each work item, inspect `.idea/workspace.xml` and fix only these known fields:

- `PropertiesComponent` data containing `last_opened_file_path`
- `CopilotPersistence > persistenceIdMap > entry@key`

When either field contains an absolute path whose project directory name matches the current work item but whose root path differs from the current work item path, replace only that stale project-root prefix with the current work item path.

Preserve trailing subpaths and unrelated values. For Copilot persistence entries, preserve the existing entry `value`.



## Do Not Fix

Do not rewrite:

- `$PROJECT_DIR$`, `$MODULE_DIR$`, or `$USER_HOME$` paths
- remote deployment paths such as `/opt/...`
- IDE installation paths such as `/Applications/PyCharm.app/...`
- arbitrary absolute paths whose project directory name does not match the current work item
- `.idea` files other than `workspace.xml`



## Workflow

Set the starting directory from the user's provided path:

```bash
start_dir="/absolute/path/to/start-directory"
```

Run the bundled script from this skill directory:

```bash
python3 scripts/fix_idea_metadata.py "$start_dir"
```

The script scans work items deterministically, writes changes in place only when content changes, and uses a same-directory temporary file followed by atomic replacement.



## Reporting

Report the script output directly. The report groups work items by result:

```md
- 已成功处理仓库 (1)：
    - Awesome-AI
        - 已修正字段：workspace.xml: CopilotPersistence entry key, last_opened_file_path
- 无需处理仓库 (1)：
    - another-repo
- 处理失败仓库 (1)：
    - broken-repo
        - 失败原因：workspace.xml is not valid UTF-8
```
