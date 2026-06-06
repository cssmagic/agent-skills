[English](README.md) | 中文

# Agent Skills

> “Skill” 是一组打包好的指令和脚本，用来扩展 AI agent 在特定任务上的能力，适用于 Cursor、Codex、OpenClaw、Claude Code 等工具。它们遵循 [Agent Skills](https://agentskills.io/) 开放标准。

魔法哥每天在用的 skill 都开源在这里，所有 skill 分类展示如下。



## 🤖 AI Agent 相关

- ### [`link-as-global-skills`](skills/link-as-global-skills/README.zh.md)

	作为一个 skill 开发者，你在编写 skill 时，最烦的往往不是写 `SKILL.md`，而是让本机的 agent 立刻读到你刚改完的版本。

	这个 skill 会把你在本地开发的 skill 软链接到 `~/.agents/skills` 目录下。这样当你在仓库里持续修改 skill 时，本机的 agent 随时可以调用它的最新版本，无需反复复制、重装或同步。

	因此，它非常适合正在编写、调试、维护 skill 的作者。



## 📖 文档与写作

- ### [`bilingual-readme`](skills/bilingual-readme/README.zh.md)

	开源项目经常需要一份面向全球读者的英文 README，也需要一份面向中文用户的中文 README，但两份文档长期保持一致很容易被忽略。

	这个 skill 可以把单语言 README 转换成配套的 `README.md` 与 `README.zh.md`，也可以维护已有的双语 README，让它们在结构和事实上保持一致。它适合每一位国际化的开源项目维护者。

- ### [`markdown-guidelines`](skills/markdown-guidelines/README.zh.md)

	作为一个开源实践者、技术作者和 AI 探索者，我几乎每天都在写 Markdown。这个 skill 汇总了我自己沉淀多年的 Markdown 风格偏好，它提供了良好的源码可读性。

	安装这个 skill 之后，agent 在帮你生成或修改任何 Markdown 文本时都会严格保持指定格式，再也无需手动修改。

	如果你有不同的风格偏好，也可以 fork 这个 skill，改成你喜欢的样子。它适合每一位 Markdown 用户。



## 🖼️ 图片处理和转换

- ### [`fix-svg-aspect-ratio`](skills/fix-svg-aspect-ratio/README.zh.md)

	有些 SVG 在一个工具里看起来正常，换到另一个环境就会被拉伸、压扁，或错误地填满容器。这通常是因为根 `<svg>` 属性没有清楚地保留图形的自然宽高比。

	这个 skill 提供了一个很小的脚本化修复步骤，尤其适合处理 Figma Desktop MCP 导出的 SVG 矢量资源。它适合经常处理 SVG 素材的网页设计师和开发者。

- ### [`convert-png-to-webp`](skills/convert-png-to-webp/README.zh.md)

	PNG 资源很容易悄悄占掉大量空间。当你已经确定想在同一棵目录树里用 WebP 替换它们时，手动转换、保留时间戳、再删除原文件既重复又容易出错。

	这个 skill 提供了一套谨慎的脚本化流程，用来原地把 PNG 转成无损 WebP。它适合需要减少图片素材的磁盘占用，且关心文件原始时间戳的场景。



## 💻 编程与开发

- ### [`fix-idea-metadata`](skills/fix-idea-metadata/README.zh.md)

	当你移动、复制或重命名一个本地 JetBrains IDE 项目后，`.idea` 元数据里可能还保留着旧的绝对路径。这可能会引发一些意外的结果。

	这个 skill 可以在 `.idea` 目录中修复那些已经过时的绝对路径字段。



***

## 使用方法

### 安装

```bash
npx skills add cssmagic/agent-skills
```

根据交互式命令行界面的提示，选择需要安装的 skill（↓↑：移动光标，空格：选择，回车：确认）。

### 显式调用

在支持 Agent Skills 的 agent 中按名称调用 skill。大多数 agent 都支持通过 `/` 字符来指定 skill，就可以这样用：

```text
/bilingual-readme
Handle current repo.
```

### 隐式调用

如果你发送给 agent 的任务匹配某个 skill 的能力范围，agent 通常可以自动调用该 skill 来完成任务。比如：

```text
Convert this repository’s README into bilingual versions.
```



***

## License

> Any code contributed to this project is considered authorized for commercial use by the project authors and their affiliated companies and distributed under this project's license.
>
> 任何贡献到本项目的代码，均视为授权本项目作者及其关联公司用于商业用途，并可按本项目协议进行分发。

MIT
