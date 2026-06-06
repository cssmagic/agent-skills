[English](README.md) | 中文

# Bilingual README

## 我为什么需要这个 Skill？

开源项目经常需要一份面向全球读者的英文 README，也需要一份面向中文用户的中文 README，但两份文档长期保持一致很容易被忽略。

这个 skill 可以把单语言 README 转换成配套的 `README.md` 与 `README.zh.md`，也可以维护已有的双语 README，让它们在结构和事实上保持一致。它适合每一位国际化的开源项目维护者。



## 它会做什么？

- 将 `README.md` 保持为英文默认入口，将 `README.zh.md` 作为中文版本。
- 为两份文件添加标准语言切换器。
- 保持结构、示例、表格、代码围栏、链接、徽章、截图、关键可信声明或法律说明同步。
- 根据仓库上下文对齐已有英文和中文内容，而不是编造未支持的功能。

最终结果是一组自然、同步、描述同一个项目事实的双语 README。



## 如何安装这个 Skill？

### 让 AI Agent 帮你安装

在 Codex、Claude Code、Cursor、OpenClaw 等支持 skill 的 AI agent 里，直接说：

```text
请帮我安装这个 skill：
https://github.com/cssmagic/agent-skills/tree/master/skills/bilingual-readme
```

### 手动安装

运行以下命令：

```bash
npx skills add cssmagic/agent-skills -s bilingual-readme -g
```



## 如何使用？

安装后，在 AI agent 中打开你想翻译或同步 README 的项目，然后说：

```text
调用 bilingual-readme
把这个仓库的 README 转成英文和中文两个版本。
```

你也可以提供具体的仓库路径，或说明哪种语言应作为事实来源。运行完成后，请检查两份 README，确认项目专有表述、命令、链接和法律说明仍然准确。



***

## 更多有用的 Skills

这个 skill 的作者还开源了不少有用的 skill，去看看吧！<br>
https://github.com/cssmagic/agent-skills/blob/master/README.zh.md#agent-skills
