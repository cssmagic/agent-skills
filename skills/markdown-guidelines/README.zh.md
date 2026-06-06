[English](README.md) | 中文

# Markdown Guidelines

## 我为什么需要这个 Skill？

作为一个开源实践者、技术作者和 AI 探索者，我几乎每天都在写 Markdown。这个 skill 汇总了我自己沉淀多年的 Markdown 风格偏好，它提供了良好的源码可读性。

安装这个 skill 之后，agent 在帮你生成或修改任何 Markdown 文本时都会严格保持指定格式，再也无需手动修改。

如果你有不同的风格偏好，也可以 fork 这个 skill，改成你喜欢的样子。它适合每一位 Markdown 用户。



## 它会做什么？

- 在 Markdown 正文中使用 tab 字符缩进。
- 在 YAML frontmatter 中使用两个空格缩进。
- 使用 `- list item` 作为无序列表格式。
- 使用 `***` 作为水平分隔线。
- 使用 HTML 注释编写 Markdown 正文注释。
- 使用 `<br>` 表示有意换行。
- 按仓库约定处理二级标题和水平分隔线前的空行。

最终结果是符合作者偏好格式的 Markdown，可在 skill 和文档之间保持一致。



## 如何安装这个 Skill？

### 让 AI Agent 帮你安装

在 Codex、Claude Code、Cursor、OpenClaw 等支持 skill 的 AI agent 里，直接说：

```text
请帮我安装这个 skill：
https://github.com/cssmagic/agent-skills/tree/master/skills/markdown-guidelines
```

### 手动安装

运行以下命令：

```bash
npx skills add cssmagic/agent-skills -s markdown-guidelines -g
```



## 如何使用？

安装后，让你的 AI agent 在编写、编辑或 review Markdown 时调用这个 skill：

```text
调用 markdown-guidelines
检查这个 SKILL.md 的格式一致性。
```

这个 skill 最适合在 agent 已经能看到目标 Markdown 文件或仓库上下文时使用。运行完成后，被编辑或 review 的 Markdown 应该符合这套个人格式规则。



***

## 更多有用的 Skills

这个 skill 的作者还开源了不少有用的 skill，去看看吧！<br>
https://github.com/cssmagic/agent-skills/blob/master/README.zh.md#agent-skills
