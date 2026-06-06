[English](README.md) | 中文

# Fix IDEA Metadata

## 我为什么需要这个 Skill？

当你移动、复制或重命名一个本地 JetBrains IDE 项目后，`.idea` 元数据里可能还保留着旧的绝对路径。这可能会引发一些意外的结果。

这个 skill 可以在 `.idea` 目录中修复那些已经过时的绝对路径字段。



## 它会做什么？

- 从给定起始目录递归查找 `.idea` 目录，并跳过 `node_modules`。
- 如果某个项目里存在多个 `.iml` 文件，会在写入前停止。
- 修复 `workspace.xml` 中白名单字段，包括已知的 `PropertiesComponent`、Copilot 持久化和模块名取值。
- 在需要时，将唯一的 `.iml` 文件重命名为当前仓库目录名。
- 在适用时，更新 `.idea/modules.xml` 中对旧 `.iml` 文件名的引用。

最终结果是一套定向的元数据修复：保留无关 IDE 设置，并准确报告发生了哪些变化。



## 如何安装这个 Skill？

### 让 AI Agent 帮你安装

在 Codex、Claude Code、Cursor、OpenClaw 等支持 skill 的 AI agent 里，直接说：

```text
请帮我安装这个 skill：
https://github.com/cssmagic/agent-skills/tree/master/skills/fix-idea-metadata
```

### 手动安装

运行以下命令：

```bash
npx skills add cssmagic/agent-skills -s fix-idea-metadata -g
```



## 如何使用？

安装后，把需要扫描 JetBrains 项目的目录告诉你的 AI agent：

```text
调用 fix-idea-metadata
处理这个目录： /path/to/projects
```

这个 skill 会扫描每个 `.idea` 项目，只应用已支持的修复，并返回分组报告，说明哪些仓库已修改、无需修改，或因为预检和解析问题失败。



***

## 更多有用的 Skills

这个 skill 的作者还开源了不少有用的 skill，去看看吧！<br>
https://github.com/cssmagic/agent-skills/blob/master/README.zh.md#agent-skills
