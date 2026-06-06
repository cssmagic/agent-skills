[English](README.md) | 中文

# Sync Image As WebP

## 我为什么需要这个 Skill？

发布或整理图片资源时，你可能想得到一个与源目录结构一致的目标目录，但其中的 PNG 都变成无损 WebP。手动做这件事很繁琐，因为流程需要保留目录结构、复制非 PNG 文件、保留时间戳，还要避免意外覆盖。

这个 skill 为 agent 提供了一套谨慎的同步流程，用来生成这样的目标目录。它适合需要一份 WebP 版本素材目录，同时保持源目录不被改动的场景。



## 它会做什么？

- 将源目录同步到目标目录，并保留相对路径。
- 将 PNG 文件转换为同名 `.webp` 文件，采用无损 WebP。
- 原样复制非 PNG 文件。
- 在需要时创建空目标目录。
- 保留修改时间，并在 macOS 可用时保留创建时间。
- 校验预期文件、时间戳、目录差异，以及仅存在于源或目标中的项目。

最终结果是一份独立的目标目录：结构与源目录一致，PNG 资源已转换成 WebP，而原始源目录保持不变。



## 如何安装这个 Skill？

### 让 AI Agent 帮你安装

在 Codex、Claude Code、Cursor、OpenClaw 等支持 skill 的 AI agent 里，直接说：

```text
请帮我安装这个 skill：
https://github.com/cssmagic/agent-skills/tree/master/skills/sync-image-as-webp
```

### 手动安装

运行以下命令：

```bash
npx skills add cssmagic/agent-skills -s sync-image-as-webp -g
```



## 如何使用？

安装后，把源目录和目标目录都告诉你的 AI agent：

```text
调用 sync-image-as-webp
源目录： /path/to/source-images
目标目录： /path/to/target-images
```

这个 skill 会在写入前拒绝不安全映射，包括目标路径冲突、已存在的目标映射文件（除非你明确允许覆盖），以及目标目录位于源目录内部。运行完成后，agent 应该报告转换、复制、时间戳和校验结果。



***

## 更多有用的 Skills

这个 skill 的作者还开源了不少有用的 skill，去看看吧！<br>
https://github.com/cssmagic/agent-skills/blob/master/README.zh.md#agent-skills
