English | [中文](README.zh.md)

# Fix IDEA Metadata

## Why Do I Need This Skill?

After moving, copying, or renaming a local JetBrains IDE project, `.idea` metadata can keep stale absolute paths. This may cause unexpected behavior.

This skill repairs outdated absolute path fields inside the `.idea` directory.



## What Does It Do?

- Recursively searches for `.idea` directories under a starting directory while skipping `node_modules`.
- Stops before writing if a project has more than one `.iml` file.
- Repairs whitelisted fields in `workspace.xml`, including known `PropertiesComponent`, Copilot persistence, and module-name values.
- Renames the unique `.iml` file to match the current repository directory when needed.
- Updates `.idea/modules.xml` references to the renamed `.iml` file when applicable.

The result is a targeted metadata repair that preserves unrelated IDE settings and reports exactly what changed.



## How to Install This Skill?

### With an AI Agent

In Codex, Claude Code, Cursor, OpenClaw, or another AI agent that supports skills, just say:

```text
Please help me install this skill:
https://github.com/cssmagic/agent-skills/tree/master/skills/fix-idea-metadata
```

### Manually

Run:

```bash
npx skills add cssmagic/agent-skills -s fix-idea-metadata -g
```



## How to Use It?

After installation, give your AI agent the directory where it should search for JetBrains projects:

```text
Invoke fix-idea-metadata
Process this directory: /path/to/projects
```

The skill scans each `.idea` project, applies only the supported repairs, and returns a grouped report showing repositories that were changed, unchanged, or failed preflight or parsing checks.



***

## More Useful Skills

The author of this skill has open-sourced several other useful skills. Take a look:<br>
https://github.com/cssmagic/agent-skills#readme
