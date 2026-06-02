---
name: fix-idea-metadata
description: "Use when a local JetBrains IDE project was moved or renamed and its `.idea` metadata may still contain stale absolute project paths."
license: MIT
metadata:
  author: cssmagic
---

# Fix IDEA Metadata

## Purpose

Fix known `.idea` metadata fields that can keep stale paths after a local repository is moved, copied, or renamed.

This skill is intentionally script-backed. It should only repair fields that are known to contain movable local project paths.



## Required Input

Each run needs one starting working directory.

If the starting directory is missing from the user's request and the conversation context does not clearly provide it, ask the user for the path before running commands.

Normalize `~` and relative paths to an absolute path before reporting or running the script.



## Fixes Applied

Search recursively under the starting directory for `.idea` directories. Skip `node_modules` directories while searching. Treat each `.idea` parent directory as one work item.

Before writing any file, run preflight checks for every work item. If any `.idea` directory contains more than one `.iml` file, stop the whole run and report the affected project. Multiple module files are ambiguous and should not be guessed.

For each valid work item, inspect `.idea/workspace.xml` and fix only these known fields:

- `PropertiesComponent` data containing `last_opened_file_path`
- `PropertiesComponent` data containing `ts.external.directory.path`
- `CopilotPersistence > persistenceIdMap > entry@key`
- `workspace.xml` XML elements with a `module name` attribute

When a known field contains an absolute path whose project directory name matches the current work item or the unique `.iml` stem, but whose root path differs from the current work item path, replace only that stale project-root prefix with the current work item path.

If an absolute path already equals the current work item path or is already under it, treat it as valid and do not rewrite it. This avoids corrupting paths when a parent directory and the project directory share the same name.

Preserve trailing subpaths and unrelated values. For Copilot persistence entries, preserve the existing entry `value`.

For `<module name="...">`, only replace the value when it exactly equals the unique `.iml` stem and that stem differs from the current repository directory name. If the value is empty or different from the `.iml` stem, leave it unchanged.

If the `.idea` directory contains exactly one `.iml` file and its filename does not match the current repository directory name, rename it to `{current-repository-name}.iml`. If the old and new `.iml` names differ only by letter case, rename through a temporary intermediate filename first so case-insensitive file systems still apply the intended spelling. If `.idea/modules.xml` references the old `.iml` filename, update that reference to the new filename.



## Do Not Fix

Do not rewrite:

- `$PROJECT_DIR$`, `$MODULE_DIR$`, or `$USER_HOME$` paths
- remote deployment paths such as `/opt/...`
- IDE installation paths such as `/Applications/PyCharm.app/...`
- arbitrary absolute paths whose project directory name does not match the current work item
- `workspace.xml` paths outside the known field whitelist
- `.idea` files other than `workspace.xml`, `modules.xml`, and the unique `.iml` file



## Workflow

Set the starting directory from the user's provided path:

```bash
start_dir="/absolute/path/to/start-directory"
```

Run the bundled script from this skill directory:

```bash
python3 scripts/fix_idea_metadata.py "$start_dir"
```

The script scans work items deterministically, writes text-file changes in place only when content changes, and uses a same-directory temporary file followed by atomic replacement.



## Reporting

The script outputs an English report grouped by result. In the final response to the user, summarize or translate that report using the user's language preference:

```md
- Successfully Processed Repositories (1):
	- `{repo_name}`. Fixed files and fields:
		- `old-name.iml`: renamed to `{repo_name}.iml`
		- `modules.xml`: module fileurl/filepath
		- `workspace.xml`: CopilotPersistence entry key
		- `workspace.xml`: last_opened_file_path
		- `workspace.xml`: module name
		- `workspace.xml`: ts.external.directory.path
- Repositories Requiring No Changes (1):
	- `{repo_name}`
- Failed Repositories (1):
	- `{repo_name}`. Reason: `workspace.xml` is not valid UTF-8
```
