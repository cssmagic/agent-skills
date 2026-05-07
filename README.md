English | [中文](README.zh.md)

# Agent Skills

A collection of skills for AI agents, including Cursor, Codex, OpenClaw, and Claude Code. Skills are packaged instructions, helper scripts, references, and optional agent metadata that extend an agent's task-specific capabilities.

Skills follow the [Agent Skills](https://agentskills.io/) format.



## Available Skills

### [`bilingual-readme`](skills/bilingual-readme/SKILL.md)

Create and maintain bilingual READMEs for GitHub open-source projects.

### [`link-as-global-skills`](skills/link-as-global-skills/SKILL.md)

Link locally developed skills into `~/.agents/skills` so local agents can discover them.

### [`markdown-guidelines`](skills/markdown-guidelines/SKILL.md)

My personal Markdown formatting guidelines for writing Agent Skills, READMEs, technical documentation, [Issue Blog](https://github.com/cssmagic/Awesome-Issue-Blogs), and similar content.

### [`sync-image-as-webp`](skills/sync-image-as-webp/SKILL.md)

Sync a source directory to a target directory, convert PNG images to lossless WebP, and preserve directory structure and timestamps.

### [`convert-png-to-webp`](skills/convert-png-to-webp/SKILL.md)

Convert PNG images to lossless WebP in place within a directory tree, preserve original timestamps, and delete the source PNG files after successful conversion. (Effectively a more aggressive version of [`sync-image-as-webp`](skills/sync-image-as-webp/SKILL.md).)



## Installation

```bash
npx skills add cssmagic/agent-skills
```

Follow the interactive CLI prompts to select the skills you want to install.



## Usage

### Explicit Invocation

Invoke a skill by name from an agent that supports Agent Skills. Some agents support specifying skills with `/`, so you can use:

```text
/bilingual-readme
Handle current repo.
```

Other agents support specifying skills with `$`:

```text
Run $bilingual-readme in this repo.
```

### Implicit Invocation

If your request matches a skill's capability, the agent can usually invoke that skill automatically. For example:

```text
Convert this repository’s README into bilingual versions.
```



## Skill Structure

Each skill directory may contain:

- `SKILL.md` - Instructions for the agent.
- `scripts/` - Optional helper scripts for automation.
- `references/` - Optional supporting documentation.
- `agents/` - Optional agent-specific metadata or default prompts.



***

## License

> Any code contributed to this project is considered authorized for commercial use by the project authors and their affiliated companies and distributed under this project's license.
>
> 任何贡献到本项目的代码，均视为授权本项目作者及其关联公司用于商业用途，并可按本项目协议进行分发。

MIT
