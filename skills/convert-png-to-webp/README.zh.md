[English](README.md) | 中文

# Convert PNG to WebP

## 我为什么需要这个 Skill？

PNG 资源很容易悄悄占掉大量空间。当你已经确定想在同一棵目录树里用 WebP 替换它们时，手动转换、保留时间戳、再删除原文件既重复又容易出错。

这个 skill 提供了一套谨慎的脚本化流程，用来原地把 PNG 转成无损 WebP。它适合需要减少图片素材的磁盘占用，且关心文件原始时间戳的场景。



## 它会做什么？

- 在一棵目录树中查找 PNG 文件，并且不区分扩展名大小写。
- 将每个 PNG 转成同目录、同 basename 的 `.webp` 文件，采用无损 WebP。
- 保留修改时间，并在 macOS 上保留创建时间。
- 写入前拒绝不安全的运行，包括已存在的目标 WebP、目标路径冲突和软链接 PNG。
- 只有在 WebP 替换文件完成后，才删除对应的源 PNG。

最终结果是一棵原地转换后的 WebP 素材目录，源 PNG 只会在成功替换后被移除。



## 如何安装这个 Skill？

### 让 AI Agent 帮你安装

在 Codex、Claude Code、Cursor、OpenClaw 等支持 skill 的 AI agent 里，直接说：

```text
请帮我安装这个 skill：
https://github.com/cssmagic/agent-skills/tree/master/skills/convert-png-to-webp
```

### 手动安装

运行以下命令：

```bash
npx skills add cssmagic/agent-skills -s convert-png-to-webp -g
```



## 如何使用？

安装后，把需要处理的目录告诉你的 AI agent：

```text
调用 convert-png-to-webp
处理这个目录： /path/to/image-directory
```

这个 skill 会检查前置条件，并且不会覆盖已存在的目标 WebP，除非你明确允许覆盖。运行完成后，agent 应该报告找到、转换、删除了多少 PNG，以及时间戳是否已同步。



***

## 更多有用的 Skills

这个 skill 的作者还开源了不少有用的 skill，去看看吧！<br>
https://github.com/cssmagic/agent-skills/blob/master/README.zh.md#agent-skills
