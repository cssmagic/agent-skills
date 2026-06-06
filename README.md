English | [中文](README.zh.md)

# Agent Skills

> “Skills” are packaged instructions and scripts that extend AI agents in task-specific ways, and they work with tools such as Cursor, Codex, OpenClaw, and Claude Code. They follow the [Agent Skills](https://agentskills.io/) open standard.

The skills I use every day are open-sourced here. They are grouped below.



## 🤖 AI Agent

- ### [`link-as-global-skills`](skills/link-as-global-skills/)

	As a skill developer, the annoying part is often not writing `SKILL.md`, but making your local agent immediately see the version you just changed.

	This skill symlinks the skills you are developing locally into `~/.agents/skills`. Then, as you keep editing skills in your repository, your local agent can call their latest versions without repeated copying, reinstalling, or syncing.

	So, it is ideal for authors who are writing, debugging, or maintaining skills.



## 📖 Documentation and Writing

- ### [`bilingual-readme`](skills/bilingual-readme/)

	Open-source projects often need an English README for the global audience and a Chinese README for local users, but keeping two versions aligned is easy to neglect.

	This skill turns a single-language README into a paired `README.md` and `README.zh.md`, or maintains an existing bilingual README pair so the two versions stay structurally and factually aligned. It is useful for every open-source maintainer working with an international audience.

- ### [`markdown-guidelines`](skills/markdown-guidelines/)

	As an open-source practitioner, technical writer, and AI explorer, I write Markdown almost every day. This skill collects the Markdown style preferences I have refined over many years, with a focus on readable source text.

	After installing this skill, an agent will keep the specified formatting whenever it generates or edits Markdown, so you no longer need to clean it up by hand.

	If you prefer a different style, you can also fork this skill and make it your own. It is useful for every Markdown user.



## 🖼️ Image Processing and Conversion

- ### [`fix-svg-aspect-ratio`](skills/fix-svg-aspect-ratio/)

	Some SVG files look fine in one tool but stretch, squash, or fill their container incorrectly elsewhere. This often happens when the root `<svg>` attributes do not clearly preserve the artwork's natural aspect ratio.

	This skill provides a small, script-backed repair step, especially for vector SVG assets exported by Figma Desktop MCP. It is useful for web designers and developers who often work with SVG assets.

- ### [`convert-png-to-webp`](skills/convert-png-to-webp/)

	PNG assets can quietly take up a lot of space. When you already know you want WebP replacements in the same directory tree, manually converting files, preserving timestamps, and deleting originals is repetitive and easy to get wrong.

	This skill provides a cautious, script-backed workflow for converting PNG files to lossless WebP in place. It is useful when you need to reduce image asset disk usage while preserving original file timestamps.



## 💻 Programming and Development

- ### [`fix-idea-metadata`](skills/fix-idea-metadata/)

	After moving, copying, or renaming a local JetBrains IDE project, `.idea` metadata can keep stale absolute paths. This may cause unexpected behavior.

	This skill repairs outdated absolute path fields inside the `.idea` directory.



***

## Usage

### Installation

```bash
npx skills add cssmagic/agent-skills
```

Follow the interactive CLI prompts to select the skills you want to install (↓↑: move cursor, space: select, enter: confirm).

### Explicit Invocation

After installation, invoke a skill by name from an agent that supports Agent Skills. Most agents support specifying skills with `/`, so you can use:

```text
/bilingual-readme
Handle current repo.
```

### Implicit Invocation

If your request matches a skill's capability, the agent can usually invoke that skill automatically. For example:

```text
Convert this repository’s README into bilingual versions.
```



***

## License

> Any code contributed to this project is considered authorized for commercial use by the project authors and their affiliated companies and distributed under this project's license.
>
> 任何贡献到本项目的代码，均视为授权本项目作者及其关联公司用于商业用途，并可按本项目协议进行分发。

MIT
