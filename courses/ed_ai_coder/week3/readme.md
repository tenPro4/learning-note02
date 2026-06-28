# Multi-Agent Orchestrators

Gastown, Claude Agent teams and GSD

## Claude Agent Teams

## GSD

https://github.com/open-gsd/gsd-core

### 什么是 GSD Core

GSD Core 是一套上下文工程与规范驱动开发框架，能够引导 AI 编程智能体（Claude Code、Codex、Gemini CLI、Copilot、Cursor 等）按照严格的阶段循环推进工作。它解决了[上下文腐化](docs/zh-CN/explanation/context-engineering.md)问题——即随着 AI 填满上下文窗口而逐渐累积的质量下降——通过在全新上下文的子智能体中运行所有繁重的研究、规划和执行工作，同时保持主会话的精简。

---

### 工作原理

每个里程碑重复相同的五步循环，每次推进一个阶段：

1. **讨论（Discuss）** — 在规划任何内容之前，先捕获实现决策
2. **规划（Plan）** — 研究、分解，并验证计划能够适配全新的上下文窗口
3. **执行（Execute）** — 以并行波次运行计划；每个执行器以干净的 20 万 token 上下文启动
4. **验证（Verify）** — 检查已构建的内容；在宣告完成前诊断并修复问题
5. **交付（Ship）** — 创建 PR，归档阶段，对下一个阶段重复上述流程

---

### 快速开始

```bash
npx @opengsd/gsd-core@latest
```

安装程序会提示选择运行时（Claude Code、OpenCode、Gemini CLI、Kilo、Codex、Copilot、Cursor、Windsurf 等）以及是全局安装还是本地安装。跨运行时兼容性需要使用安装程序——请勿直接从 `agents/` 或 `commands/` 目录复制文件。

使用其他运行时或没有 Node.js？请参阅[在你的运行时上安装](docs/zh-CN/how-to/install-on-your-runtime.md)。

安装完成后，启动`claude code`然后先检查设置以满足你的需求。

```bash
/gsd:settings
```

接着只需要启动你的第一个项目：

```bash
/gsd-new-project
```

初次使用？请按照[你的第一个项目](docs/zh-CN/tutorials/your-first-project.md)进行引导式操作，从安装到完成第一个交付阶段。

---

### 文档

**教程** — 边做边学：
- [你的第一个项目](docs/zh-CN/tutorials/your-first-project.md)
- [接入现有代码库](docs/zh-CN/tutorials/onboarding-an-existing-codebase.md)

**操作指南** — 面向任务的实用方法：
- [在你的运行时上安装](docs/zh-CN/how-to/install-on-your-runtime.md)
- [规划一个阶段](docs/zh-CN/how-to/plan-a-phase.md)
- [验证与交付](docs/zh-CN/how-to/verify-and-ship.md)
- … [查看所有操作指南](docs/zh-CN/README.md#how-to-guides)

**参考文档** — 权威信息：
- [命令](docs/zh-CN/COMMANDS.md)
- [配置](docs/zh-CN/CONFIGURATION.md)
- [CLI 工具](docs/zh-CN/CLI-TOOLS.md)

**概念说明** — 设计理念与决策：
- [上下文工程](docs/zh-CN/explanation/context-engineering.md)
- [阶段循环](docs/zh-CN/explanation/the-phase-loop.md)
- [架构](docs/zh-CN/ARCHITECTURE.md)

完整索引：[docs/zh-CN/README.md](docs/zh-CN/README.md)。其他语言：[日本語](README.ja-JP.md) · [한국어](README.ko-KR.md) · [Português](README.pt-BR.md) · [English](README.md)。

---

### 为什么有效

大多数 AI 编程方案在规模化时都会失败，原因在于上下文膨胀会悄无声息地降低输出质量，各会话之间没有共享记忆，也没有任何机制来验证代码是否真正可用。GSD Core 解决了这三个问题：繁重的工作在全新的子智能体中运行，`STATE.md` 和 `CONTEXT.md` 等结构化工件能够跨越会话边界保持存续，验证步骤会检查已构建的内容并在宣告阶段完成前生成修复计划。完整的设计思路请参阅 [docs/zh-CN/explanation/context-engineering.md](docs/zh-CN/explanation/context-engineering.md)。

遇到问题？请参阅 [docs/zh-CN/how-to/recover-and-troubleshoot.md](docs/zh-CN/how-to/recover-and-troubleshoot.md)。

### 用后感想
非常吃token；整个流程分阶段在subagent之间**一个一个**地上下review生成的文档，确保所有的功能得以delivery，但这也导致它运作的时长提高很多。

> 注意，每个subagent不是同行进行的，而是一个subagent交付任务后，再让主agent进行安排下一个subagent推进执行。

总的来说，输出的结果品质和claude teams差别不大，但是claude agent teams的用时更短，token消耗而言也没gsd大。

> 可靠；慢。

## gastown
