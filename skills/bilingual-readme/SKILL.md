---
name: bilingual-readme
description: Create and maintain English-first bilingual READMEs for GitHub projects. Use when converting a single-language README to a paired `README.md` and `README.zh.md`, adding a Chinese README beside an English default README, translating a Chinese README into the default English README, or keeping existing English and Chinese README files structurally synchronized.
license: MIT
metadata:
  author: cssmagic
---

# Bilingual README

## Overview

Use this workflow to make open-source project READMEs bilingual while keeping English as the default public entry point. The expected output is `README.md` in English plus `README.zh.md` in Chinese, with a compact language switcher at the top of both files.




## Target Shape

Use these conventions unless the user or repository already has a stronger local convention:

- Keep `README.md` as the English default.
- Put the Chinese version in `README.zh.md`.
- Start `README.md` with:

```markdown
English | [中文](README.zh.md)
```

- Start `README.zh.md` with:

```markdown
[English](README.md) | 中文
```

- Keep the project title, logo, badges, screenshots, code examples, CLI commands, API names, package names, URLs, and license identifier consistent across both files.
- Preserve Markdown structure across languages: headings, section order, tables, lists, blockquotes, code fences, HTML snippets, and horizontal rules should correspond one-to-one unless a section is language-specific by nature.
- Keep key trust or legal statements bilingual in both files when the original README already does so, such as contribution authorization, commercial-use notices, or license-related blockquotes.



## Workflow

1. Inspect the repository context.

	- Read existing `README.md`, `README.zh.md`, package metadata, docs links, CLI help, or examples needed to avoid mistranslating product behavior.
	- Determine whether the source README is English-only, Chinese-only, or already bilingual.

2. Establish the canonical content.

	- Treat the most complete and current README as the source of truth.
	- If both language files exist but diverge, preserve unique factual content from both and reconcile contradictions from code or project metadata before translating.
	- Do not invent features, installation methods, examples, roadmap items, or compatibility claims.

3. Produce or update `README.md`.

	- Write natural, idiomatic English for the default README.
	- If the original is Chinese, translate meaning rather than preserving Chinese syntax.
	- Keep the opening summary crisp and accessible to global open-source users.

4. Produce or update `README.zh.md`.

	- Write natural Simplified Chinese.
	- Prefer common developer phrasing over literal translation.
	- Leave technical identifiers in English where developers expect them: package names, commands, option names, API symbols, filenames, environment variables, issue labels, and protocol names.

5. Synchronize structure and formatting.

	- Add or fix the language switcher in both files.
	- Match heading hierarchy and section ordering.
	- Keep examples and tables semantically equivalent; translate table headers and prose cells, but keep literal command flags and values unchanged.
	- Preserve relative links where possible. When a link points to another local Markdown document, check whether a localized counterpart exists before changing it.

6. Validate the result.

	- Diff both README files and scan for accidental deletions.
	- Check that the language switcher links are correct.
	- Check that every code fence still has its closing fence.
	- Check that Markdown tables still have matching columns.
	- If the repository has Markdown linting or documentation tests, run the relevant checks.



## Translation Guidelines

- Translate intent, not word order.
- Keep project and product names unchanged unless the existing Chinese README already uses a stable Chinese name.
- Do not translate GitHub-specific terms awkwardly when the community commonly uses English, such as issue, pull request, fork, release, tag, and token. Use Chinese explanations around them when needed.
- Keep command output, config keys, JSON fields, YAML keys, environment variables, and code comments unchanged unless they are clearly explanatory prose meant for readers.
- Keep examples realistic and identical across languages unless the language itself affects the example.
- Preserve admonitions, blockquotes, and legal statements carefully. Do not weaken requirements or guarantees during translation.
- Prefer concise section titles. Examples: `Installation` maps to `安装`, `Usage` maps to `使用方法`, `Documentation` maps to `文档`, and `License` usually stays `License`.



## Handling Existing Patterns

- If the repository already uses another language selector style, keep it if it is clear and symmetrical.
- If the existing README embeds both English and Chinese in the tagline or legal footer, preserve that bilingual snippet in both language files when it improves clarity or avoids changing legal meaning.
- If badges, images, or HTML are aligned or sized manually, copy those blocks exactly unless the target language requires adjacent alt text or captions to change.
- If a section exists only because of ecosystem convention, such as npm installation, Cargo usage, or GitHub Actions status, keep the convention familiar to that ecosystem in both languages.
- If the README has generated sections, identify the generator and avoid hand-editing generated output unless the user asks for it.
