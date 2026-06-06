English | [中文](README.zh.md)

# Markdown Guidelines

## Why Do I Need This Skill?

As an open-source practitioner, technical writer, and AI explorer, I write Markdown almost every day. This skill collects the Markdown style preferences I have refined over many years, with a focus on readable source text.

After installing this skill, an agent will keep the specified formatting whenever it generates or edits Markdown, so you no longer need to clean it up by hand.

If you prefer a different style, you can also fork this skill and make it your own. It is useful for every Markdown user.



## What Does It Do?

- Uses tab characters for indentation in the Markdown body.
- Keeps YAML frontmatter indented with two spaces.
- Uses `- list item` for unordered lists.
- Uses `***` for horizontal rules.
- Uses HTML comments for Markdown body comments.
- Uses `<br>` for intentional line breaks.
- Applies the repository's blank-line convention before second-level headings and horizontal rules.

The result is Markdown that matches the author's preferred formatting style across skills and documentation.



## How to Install This Skill?

### With an AI Agent

In Codex, Claude Code, Cursor, OpenClaw, or another AI agent that supports skills, just say:

```text
Please help me install this skill:
https://github.com/cssmagic/agent-skills/tree/master/skills/markdown-guidelines
```

### Manually

Run:

```bash
npx skills add cssmagic/agent-skills -s markdown-guidelines -g
```



## How to Use It?

After installation, ask your AI agent to write, edit, or review Markdown while invoking this skill:

```text
Invoke markdown-guidelines
Review this SKILL.md for formatting consistency.
```

The skill works best when the agent has the Markdown file or repository context in front of it. After it finishes, the edited or reviewed Markdown should follow the house formatting rules.



***

## More Useful Skills

The author of this skill has open-sourced several other useful skills. Take a look:<br>
https://github.com/cssmagic/agent-skills#readme
