---
name: markdown-guidelines
description: "Use when writing, editing, or reviewing Markdown documents, including Agent Skills (`SKILL.md` files), that must follow strict house formatting rules."
license: MIT
metadata:
  author: cssmagic
---

# Markdown Guidelines

## Rules

- Use tab characters for indentation in the Markdown body. In frontmatter (YAML metadata), always use 2 spaces for indentation.
- Use `- list item` syntax for unordered lists.
- Use `***` syntax for a horizontal rule.
- Use HTML comments (`<!-- comment -->`) to write comments in the Markdown body.
- Use `<br>` when you need a line break; do not use two trailing spaces for line breaks.
- Blank lines:
	- Insert three blank lines before every second-level heading (`##`), except when the heading immediately follows a first-level heading (`#`) or a horizontal rule (`***`); in those cases, insert one blank line instead.
	- When a horizontal rule precedes a second-level heading, insert three blank lines before the horizontal rule.



## Example

```md
# First-Level Heading

## Second-Level Heading

- List item 1
- List item 2
	- List item 2-1
	- List item 2-2



***

## Another Second-Level Heading

Paragraph text.

<!-- This is a comment -->

Line 1 of a poem,<br>
Line 2 of a poem,<br>
Line 3 of a poem.
```
