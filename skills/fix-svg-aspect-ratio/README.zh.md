[English](README.md) | 中文

# Fix SVG Aspect Ratio

## 我为什么需要这个 Skill？

有些 SVG 在一个工具里看起来正常，换到另一个环境就会被拉伸、压扁，或错误地填满容器。这通常是因为根 `<svg>` 属性没有清楚地保留图形的自然宽高比。

这个 skill 提供了一个很小的脚本化修复步骤，尤其适合处理 Figma Desktop MCP 导出的 SVG 矢量资源。它适合经常处理 SVG 素材的网页设计师和开发者。



## 它会做什么？

- 处理单个 SVG 文件，或递归处理目录树中的所有 SVG 文件。
- 要求根元素存在有效 `viewBox`；不支持的文件会被报告出来，而不是靠猜测处理。
- 设置 `preserveAspectRatio="xMidYMid meet"`。
- 根据 `viewBox` 设置根元素的 `width` 和 `height`。
- 从根 `style` 属性中移除 `display: block`，同时保留其他样式声明。

最终结果是一个更稳妥的 SVG 根属性形态，能够保留宽高比，并且不改动内部矢量内容。



## 如何安装这个 Skill？

### 让 AI Agent 帮你安装

在 Codex、Claude Code、Cursor、OpenClaw 等支持 skill 的 AI agent 里，直接说：

```text
请帮我安装这个 skill：
https://github.com/cssmagic/agent-skills/tree/master/skills/fix-svg-aspect-ratio
```

### 手动安装

运行以下命令：

```bash
npx skills add cssmagic/agent-skills -s fix-svg-aspect-ratio -g
```



## 如何使用？

安装后，把需要修复的 SVG 文件或目录告诉你的 AI agent：

```text
调用 fix-svg-aspect-ratio
处理这个路径： /path/to/svg-or-directory
```

这个 skill 会原地修改受支持的 SVG 文件，并报告每个文件是已修复、已经正确、不支持，还是处理失败。



***

## 更多有用的 Skills

这个 skill 的作者还开源了不少有用的 skill，去看看吧！<br>
https://github.com/cssmagic/agent-skills/blob/master/README.zh.md#agent-skills
