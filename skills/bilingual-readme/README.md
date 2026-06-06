English | [中文](README.zh.md)

# Bilingual README

## Why Do I Need This Skill?

Open-source projects often need an English README for the global audience and a Chinese README for local users, but keeping two versions aligned is easy to neglect.

This skill turns a single-language README into a paired `README.md` and `README.zh.md`, or maintains an existing bilingual README pair so the two versions stay structurally and factually aligned. It is useful for every open-source maintainer working with an international audience.



## What Does It Do?

- Keeps `README.md` as the English default and `README.zh.md` as the Chinese version.
- Adds the standard language switcher to both files.
- Preserves matching structure, examples, tables, code fences, links, badges, screenshots, and important trust or legal statements.
- Reconciles existing English and Chinese content from repository context instead of inventing unsupported features.

The result is a bilingual README pair that reads naturally in both languages while describing the same project.



## How to Install This Skill?

### With an AI Agent

In Codex, Claude Code, Cursor, OpenClaw, or another AI agent that supports skills, just say:

```text
Please help me install this skill:
https://github.com/cssmagic/agent-skills/tree/master/skills/bilingual-readme
```

### Manually

Run:

```bash
npx skills add cssmagic/agent-skills -s bilingual-readme -g
```



## How to Use It?

After installation, open the project whose README you want to translate or synchronize in an AI agent, then say:

```text
Invoke bilingual-readme
Convert this repository's README into English and Chinese versions.
```

You can also provide a specific repository path or explain which language should be treated as the source of truth. After it finishes, review both README files to confirm that project-specific wording, commands, links, and legal statements remain accurate.



***

## More Useful Skills

The author of this skill has open-sourced several other useful skills. Take a look:<br>
https://github.com/cssmagic/agent-skills#readme
