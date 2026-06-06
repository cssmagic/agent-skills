English | [中文](README.zh.md)

# Link as Global Skills

## Why Do I Need This Skill?

As a skill developer, the annoying part is often not writing `SKILL.md`, but making your local agent immediately see the version you just changed.

This skill symlinks the skills you are developing locally into `~/.agents/skills`. Then, as you keep editing skills in your repository, your local agent can call their latest versions without repeated copying, reinstalling, or syncing.

So, it is ideal for authors who are writing, debugging, or maintaining skills.



## What Does It Do?

- Searches from your given start directory for a set of local skills.
- Symlinks those skill directories into `~/.agents/skills`. If it finds existing targets with the same names:
	- Existing symlinks will be updated.
	- Existing regular files or real directories won't be overwritten.

The result is simple: your local skills repository becomes the global skills source for this machine, ready for local agents to call at any time.



## How to Install This Skill?

### With an AI Agent

In Codex, Claude Code, Cursor, OpenClaw, or another AI agent that supports skills, just say:

```text
Please help me install this skill:
https://github.com/cssmagic/agent-skills/tree/master/skills/link-as-global-skills
```

### Manually

Run:

```bash
npx skills add cssmagic/agent-skills -s link-as-global-skills -g
```



## How to Use It?

After installation, open your local skills development repository in an AI agent, then say:

```text
Invoke link-as-global-skills
```

If you have not specified a working directory in the AI agent, you can provide one in the conversation:

```text
Invoke link-as-global-skills
Process this directory: /path/to/my-skills-repo
```

After it finishes, tell your AI agent to reload skills or run a command like `/reload-skills`, and it should be able to discover and call the skill you are developing locally.



***

## More Useful Skills

The author of this skill has open-sourced several other useful skills. Take a look:<br>
https://github.com/cssmagic/agent-skills#readme
