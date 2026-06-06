English | [中文](README.zh.md)

# Fix SVG Aspect Ratio

## Why Do I Need This Skill?

Some SVG files look fine in one tool but stretch, squash, or fill their container incorrectly elsewhere. This often happens when the root `<svg>` attributes do not clearly preserve the artwork's natural aspect ratio.

This skill provides a small, script-backed repair step, especially for vector SVG assets exported by Figma Desktop MCP. It is useful for web designers and developers who often work with SVG assets.



## What Does It Do?

- Processes one SVG file or all SVG files under a directory tree.
- Requires a valid root `viewBox`; unsupported files are reported rather than guessed.
- Sets `preserveAspectRatio="xMidYMid meet"`.
- Sets root `width` and `height` from the `viewBox`.
- Removes `display: block` from the root `style` attribute while preserving other style declarations.

The result is a safer SVG root shape that preserves aspect ratio while leaving internal vector content unchanged.



## How to Install This Skill?

### With an AI Agent

In Codex, Claude Code, Cursor, OpenClaw, or another AI agent that supports skills, just say:

```text
Please help me install this skill:
https://github.com/cssmagic/agent-skills/tree/master/skills/fix-svg-aspect-ratio
```

### Manually

Run:

```bash
npx skills add cssmagic/agent-skills -s fix-svg-aspect-ratio -g
```



## How to Use It?

After installation, give your AI agent the SVG file or directory you want to fix:

```text
Invoke fix-svg-aspect-ratio
Process this path: /path/to/svg-or-directory
```

The skill modifies supported SVG files in place and reports every file as fixed, already correct, unsupported, or failed.



***

## More Useful Skills

The author of this skill has open-sourced several other useful skills. Take a look:<br>
https://github.com/cssmagic/agent-skills#readme
