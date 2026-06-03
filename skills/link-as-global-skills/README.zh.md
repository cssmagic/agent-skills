[English](README.md) | 中文

# Link as Global Skills

## 我为什么需要这个 Skill？

作为一个 skill 开发者，你在编写 skill 时，最烦的往往不是写 `SKILL.md`，而是让本机的 agent 立刻读到你刚改完的版本。

这个 skill 会把你在本地开发的 skill 软链接到 `~/.agents/skills` 目录下。这样当你在仓库里持续修改 skill 时，本机的 agent 随时可以调用它的最新版本，无需反复复制、重装或同步。

因此，它非常适合正在编写、调试、维护 skill 的作者。（如果你只是想安装并使用某个公开的 skill，直接采用 Skills CLI 会更合适。）



## 它会做什么？

- 从你给定的起始目录向下查找一组本地 skill。
- 将这些 skill 目录软链接到 `~/.agents/skills`。
	- 已存在的软链接会被更新。
	- 已存在的普通文件或真实目录不会被覆盖。

结果很简单：你的本地 skills 仓库会成为本机的全局 skills 数据源，可被本地 agent 随时调用。



## 如何安装这个 Skill？

### 让 AI Agent 帮你安装

在 Codex、Claude Code、Cursor、OpenClaw 等支持 skill 的 AI agent 里，直接说：

```text
请帮我安装这个 skill：
https://github.com/cssmagic/agent-skills/tree/master/skills/link-as-global-skills
```

### 手动安装

运行以下命令：

```bash
npx skills add cssmagic/agent-skills -s link-as-global-skills -g
```



## 如何使用？

安装后，在 AI agent 中打开你的本地开发 skills 的仓库，然后说：

```text
调用 link-as-global-skills
```

如果你在 AI agent 中并没有指定工作目录，也可以在对话中指定：

```text
调用 link-as-global-skills
处理这个目录： /path/to/my-skills-repo
```

运行完成后，请告诉你的 AI agent 重新加载 skills 或运行 `/reload-skills` 这样的命令，它就能发现并调用你本地开发的 skill 了。



***

## 更多有用的 Skills

这个 skill 的作者还开源了不少有用的 skill，去看看吧！<br>
https://github.com/cssmagic/agent-skills/blob/master/README.zh.md#agent-skills
