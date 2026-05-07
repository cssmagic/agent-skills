[English](README.md) | 中文

# Agent Skills

这是一个面向 AI agent 的 skill 集合，适用于 Cursor、Codex、OpenClaw、Claude Code 等工具。Skill 是一组打包好的说明、辅助脚本、参考资料和可选的 agent 元数据，用来扩展 agent 在特定任务上的能力。

这些 skill 遵循 [Agent Skills](https://agentskills.io/) 格式。



## 可用 Skills

### [`bilingual-readme`](skills/bilingual-readme/SKILL.md)

为 GitHub 开源项目创建和维护双语 README。

### [`link-as-global-skills`](skills/link-as-global-skills/SKILL.md)

将本地开发中的 skill 链接到 `~/.agents/skills`，方便本机的 agent 发现。

### [`markdown-guidelines`](skills/markdown-guidelines/SKILL.md)

我个人的 Markdown 格式规范，适用于 Agent Skills、README、技术文档、[Issue Blog](https://github.com/cssmagic/Awesome-Issue-Blogs) 等场景的编写。

### [`sync-image-as-webp`](skills/sync-image-as-webp/SKILL.md)

将源目录同步到目标目录，将其中的 PNG 图片转换为无损 WebP，并保留目录结构和时间戳。

### [`convert-png-to-webp`](skills/convert-png-to-webp/SKILL.md)

在目录树中原地将 PNG 图片转换为无损 WebP，保留原始时间戳，并在转换成功后删除源 PNG 文件。（相当于 [`sync-image-as-webp`](skills/sync-image-as-webp/SKILL.md) 的激进版本。）



## 安装

```bash
npx skills add cssmagic/agent-skills
```

根据交互式命令行界面的提示，选择需要安装的 skill。



## 使用方法

### 显式调用

在支持 Agent Skills 的 agent 中按名称调用 skill。有些 agent 支持通过 `/` 字符来指定 skill，就可以这样用：

```text
/bilingual-readme
Handle current repo.
```

还有一些 agent 支持通过 `$` 字符来指定 skill：

```text
Run $bilingual-readme in this repo.
```

### 隐式调用

如果你发送给 agent 的任务匹配某个 skill 的能力范围，agent 通常可以自动调用该 skill 来完成任务。比如：

```text
Convert this repository’s README into bilingual versions.
```



## Skill 结构

每个 skill 目录可以包含：

- `SKILL.md` - 给 agent 的说明。
- `scripts/` - 可选的自动化辅助脚本。
- `references/` - 可选的参考文档。
- `agents/` - 可选的 agent 专用元数据或默认提示词。



***

## License

> Any code contributed to this project is considered authorized for commercial use by the project authors and their affiliated companies and distributed under this project's license.
>
> 任何贡献到本项目的代码，均视为授权本项目作者及其关联公司用于商业用途，并可按本项目协议进行分发。

MIT
