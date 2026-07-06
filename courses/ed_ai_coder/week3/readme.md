# Week 3：Claude Code 进阶 — 扩展、编排与云端执行

## 目录

- [概述](#概述)
- [前置条件](#前置条件)
- [自定义斜杠命令 (Slash Commands)](#自定义斜杠命令-slash-commands)
- [Subagents（子智能体）](#subagents子智能体)
- [Hooks（生命周期钩子）](#hooks生命周期钩子)
- [远程执行：Sandbox 与 GitHub 集成](#远程执行sandbox-与-github-集成)
- [第三方云沙箱：Sprites](#第三方云沙箱sprites)
- [多 Agent 编排](#多-agent-编排)
- [常见问题](#常见问题)
- [待确认事项](#待确认事项)

---

## 概述

本模块覆盖 Claude Code 的**可编程扩展面**：自定义命令、隔离上下文的 Subagents、事件 Hooks、GitHub 自动化，以及 Claude Agent Teams、GSD、Gastown 等多 Agent 编排方案。

解决痛点：单会话上下文有限；需要并行、异构模型协作；需要在 PR/Issue 流程中自动触发 Agent。

---

## 前置条件

| 要求 | 说明 |
|------|------|
| Week 2 | 已安装 Claude Code，熟悉 `.claude` 目录与基础命令 |
| Git | 远程执行与 GitHub App 集成需要 |
| GitHub CLI | `/install-github-app` 可能提示安装 [`gh`](https://cli.github.com/) |
| 可选 | OpenAI Codex CLI（跨厂商 Subagent）；Node.js（GSD）；Sprites 账号 |

---

## 自定义斜杠命令 (Slash Commands)

### 机制

在 `.claude/commands/` 下放置 `*.md` 文件，文件名即命令名（不含扩展名）。

### 实现步骤

**1. 创建目录与文件**

```text
.claude/commands/doc-review.md
```

**2. 编写指令（支持 `$ARGUMENTS` 占位符）**

```markdown
---
description: 审查指定文档并输出问题清单
---

请审查文件 `$ARGUMENTS`，按以下维度输出：

1. 结构是否清晰
2. 技术细节是否可验证
3. 缺失的前置条件或示例

将结果追加到同目录下的 `REVIEW-NOTES.md`，使用 checkbox 列出待办。
```

**3. 在 Claude Code 中调用**

```bash
/doc-review PLAN.md
```

### 参数说明

| 占位符 | 含义 |
|--------|------|
| `$ARGUMENTS` | 命令行传入的剩余参数（如文件名、路径） |

### 最佳实践

- 在 frontmatter 写清 `description`，便于 `/help` 发现
- 单命令只做一件事；复杂流程拆多个命令或改用 Skill
- 明确输出路径，避免 Agent 猜测

---

## Subagents（子智能体）

### 概念

Subagent 在**独立上下文**中运行，完成后仅将**结果摘要**返回主 Agent。

```text
Data Flow: Subagent

  Main Claude (编排)
      │
      │ 委派任务 + 输入文件路径
      ▼
  Subagent (隔离上下文)
      │  内部推理、读文件、执行命令
      │  （不污染主会话 token）
      ▼
  返回：结论 / 文件路径 / 简短摘要
      │
      ▼
  Main Claude 继续编排
```

**优势**：

- 节省主会话上下文
- 可并行启动多个 Subagent
- 可绑定不同模型（内置 general-purpose、Explore、Plan 等）

### 方式一：交互式创建

```bash
claude

/agents
# 选择 Create new agent
```

内置 Agent 示例（名称可能随版本变化）：

| Agent | 典型模型 | 用途 |
|-------|----------|------|
| `general-purpose` | inherit | 通用子任务 |
| `Explore` | haiku | 快速代码库探索 |
| `Plan` | inherit | 规划 |
| `claude-code-guide` | haiku | Claude Code 本身帮助 |

### 方式二：文件定义（推荐、可版本控制）

路径：`.claude/agents/<name>.md`

**示例：项目内审查员**

```markdown
---
name: reviewer
description: 当用户要求全面审查规划或设计文档时使用
---

你是一名技术文档审查员。

1. 阅读 `planning/PLAN.md`
2. 将结构化反馈写入 `planning/REVIEW.md`
3. 反馈格式：严重问题 / 建议 / 可选改进
4. 不要修改 PLAN.md 原文
```

调用：在对话中 `@reviewer` 或通过 `/agents` 选择。

> 即使由 Claude 驱动，**reviewer 的上下文与主会话完全隔离**。

### 跨厂商 Subagent：委托 Codex CLI

**前置**：安装 [Codex CLI](https://developers.openai.com/codex/cli)

```bash
# 可选：单独激活 codex
codex
```

**`.claude/agents/codex-reviewer.md`**

```markdown
---
name: codex-reviewer
description: 使用 OpenAI Codex 对规划文档做独立审查
---

你负责 orchestrate 一次外部审查，**不要自己写审查内容**。

必须执行以下命令（仅执行，不替代其输出）：

```bash
codex exec "请审查 planning/PLAN.md，将反馈写入 planning/REVIEW.md。使用中文，按严重级别分类。"
```

执行完成后，向主 Agent 报告：命令是否成功、`REVIEW.md` 是否已生成。
```

```text
Data Flow: 跨厂商 Subagent

  Claude Main
      │
      ▼
  codex-reviewer subagent
      │
      ▼
  shell: codex exec "..."
      │
      ▼
  OpenAI Codex（独立上下文推理）
      │
      ▼
  planning/REVIEW.md  ← 仅文件结果回到 Claude
```

---

## Hooks（生命周期钩子）

### 概念

类似 React 生命周期：在 Agent **特定阶段**自动执行命令（如会话结束、工具调用前后）。

### 配置位置

`.claude/settings.json`（项目级）或用户级 settings。

### 示例：Stop 钩子在结束时触发 Codex

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "codex exec \"对本次 git diff 做简短总结，写入 .claude/last-session-summary.txt\""
          }
        ]
      }
    ]
  }
}
```

### 管理

```bash
/hooks
```

查看可用 hook 类型与当前配置。

### 注意事项

| 项 | 说明 |
|----|------|
| 执行环境 | 命令在本地 shell 运行，继承项目 cwd |
| 失败处理 | 钩子失败可能阻塞或警告，需保持命令幂等、快速 |
| 安全 | 勿在 Stop 钩子中执行不可逆操作 |

> 可用 hook 事件名以 `/hooks` 与[官方文档](https://code.claude.com/docs)为准（如 `PreToolUse`、`PostToolUse`、`Stop` 等）。

---

## 远程执行：Sandbox 与 GitHub 集成

### 本地 Sandbox 模式

```bash
claude
/sandbox
```

| 模式 | 说明 |
|------|------|
| **1. Sandbox BashTool, auto-allow** | 推荐：命令在沙箱内运行并自动批准 |
| 2. Sandbox BashTool, regular permissions | 沙箱内但仍逐项确认 |
| 3. No Sandbox | 无隔离，等同本机权限 |

### Claude Code on GitHub

**1. 网页授权**

访问 [claude.ai/code](https://claude.ai/code)，连接 GitHub。

> ⚠️ Web 版 Claude Code **不对 Free 计划开放**。

授权时可选择：所有仓库 / 仅选定仓库。

**2. 终端安装 GitHub App**

```bash
claude
/install-github-app
```

流程概要：

1. 若提示安装 `gh`，执行 `gh auth login`
2. 浏览器完成 Claude GitHub App 安装
3. 在目标仓库启用 Claude Code

**3. 自动化效果**

- 仓库中生成 GitHub Actions workflow
- 在 Issue/PR 中 `@claude` 可触发修复并开 PR

```text
Data Flow: GitHub 集成

  Issue: "@claude 修复登录 500 错误"
      │
      ▼
  GitHub App / Workflow 触发
      │
      ▼
  Claude Code（云端或 runner）
      │
      ▼
  自动创建 PR
```

---

## 第三方云沙箱：Sprites

**官网**：[sprites.dev](https://sprites.dev/)

**定位**：硬件隔离的持久 Linux 环境，适合运行「一坨」Agent 或用户上传的任意代码。

### 快速开始

```bash
# 安装 CLI（见官方文档）
sprite login
sprite create@my-dev-box

# Sprite 实例内通常预装 claude
claude
```

**适用场景**：不信任本机权限、需要长驻远程开发环境、多项目隔离。

---

## 多 Agent 编排

### 方案对比

| 方案 | 特点 | 速度 | Token | 可靠性 |
|------|------|------|-------|--------|
| **Claude Agent Teams** | 多 Claude 实例；Lead 分配任务；可并行 | 快 | 中 | 高 |
| **GSD Core** | 规范驱动五阶段循环；子 Agent 串行交接 | 慢 | 高 | 很高 |
| **Gastown** | （待补充） | — | — | — |

### Claude Agent Teams

**文档**：[Agent Teams](https://code.claude.com/docs/en/agent-teams)

**架构**：

```text
  Team Lead (主 Claude)
      ├── Teammate: Frontend
      ├── Teammate: Backend
      ├── Teammate: DB
      └── Teammate: Integration Tester
```

**启用**（实验功能）：`.claude/settings.json`

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "teammateMode": "in-process"
}
```

| 配置项 | 可选值 | 含义 |
|--------|--------|------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `"1"` | 开启 Agent Teams |
| `teammateMode` | `in-process` 等 | Teammate 运行方式，以官方文档为准 |

**操作技巧**：

- Prompt 示例：`Create an agent team to ...`（明确角色分工）
- `Shift + Tab` → 委派模式（Delegate mode）
- `Shift + ↑/↓` → 选择 teammate 对话
- 结束：`Ask the researcher teammate to shut down`

**示例 Prompt**：

```text
Create an Agent Team to complete the project as defined in PLAN.md.

Roles:
- Front-end engineer: UI components and routing
- Backend API engineer: REST API and auth
- Database engineer: schema and migrations
- LLM engineer: model integration
- Integration tester: Playwright E2E, report bugs back
- DevOps: Docker and deploy scripts

Each member writes unit tests for their area. Integration tester runs E2E when features are ready.
```

**Subagents vs Agent Teams**（官方对比图）：

![Subagents vs Agent Teams](https://mintcdn.com/claude-code/nsvRFSDNfpSU5nT7/images/subagents-vs-agent-teams-dark.png?w=1100&fit=max&auto=format&n=nsvRFSDN7&q=85&s=3653085214a9fc65d1f589044894a296)

| 维度 | Subagents | Agent Teams |
|------|-----------|-------------|
| 并行度 | 可并行，但常由主 Agent 串行调度 | Teammate 可独立协作 |
| 适用 | 单次任务外包（审查、探索） | 多模块、多层级长期并行 |
| 上下文 | 结果回传主会话 | 多会话协调 |

### GSD Core

**仓库**：[open-gsd/gsd-core](https://github.com/open-gsd/gsd-core)

#### 是什么

GSD（Get Shit Done）是一套**上下文工程 + 规范驱动开发**框架，引导 Claude Code、Codex、Gemini CLI、Copilot、Cursor 等按**阶段循环**推进，缓解**上下文腐化**（context rot）。

#### 五阶段循环

每个里程碑重复：

| 阶段 | 动作 |
|------|------|
| **Discuss** | 先捕获实现决策，再写代码 |
| **Plan** | 研究、分解；计划须能放进全新上下文 |
| **Execute** | 并行波次执行；每个执行器 ~200k 干净上下文 |
| **Verify** | 验证构建物；未通过则诊断修复 |
| **Ship** | 开 PR、归档阶段、进入下一阶段 |

```text
Data Flow: GSD 阶段循环

  Discuss → Plan → Execute → Verify → Ship
     ▲                                    │
     └──────────── 下一 Milestone ─────────┘

  繁重工作均在 Subagent 干净上下文中完成
  主会话仅保留 STATE.md / CONTEXT.md 等工件
```

#### 快速开始

```bash
npx @opengsd/gsd-core@latest
```

安装程序会交互选择：

- 运行时（Claude Code、OpenCode、Codex、Cursor 等）
- 全局 vs 项目本地安装

> ⚠️ 跨运行时兼容**必须走安装程序**；不要手动复制 `agents/`、`commands/` 目录。

安装后在 Claude Code 中：

```bash
/gsd:settings      # 检查配置
/gsd-new-project   # 启动首个项目
```

#### 为什么有效

| 问题 | GSD 对策 |
|------|----------|
| 上下文膨胀导致质量下降 | 子 Agent 干净上下文执行 |
| 会话间无记忆 | `STATE.md`、`CONTEXT.md` 等工件 |
| 未验证就宣称完成 | Verify 阶段强制检查 |

#### 实践体会（课程笔记）

| 维度 | 评价 |
|------|------|
| 品质 | 与 Claude Agent Teams 相近 |
| 耗时 | **明显更长**（子 Agent 串行 review 文档） |
| Token | **消耗更大** |
| 并行 | 子 Agent **非同行并行**；一个交付后主 Agent 再安排下一个 |
| 总结 | **可靠但慢** |

**文档索引**（仓库内 `docs/zh-CN/`）：

- 教程：[你的第一个项目](https://github.com/open-gsd/gsd-core/blob/main/docs/zh-CN/tutorials/your-first-project.md)
- 概念：[上下文工程](https://github.com/open-gsd/gsd-core/blob/main/docs/zh-CN/explanation/context-engineering.md)
- 排错：[recover-and-troubleshoot](https://github.com/open-gsd/gsd-core/blob/main/docs/zh-CN/how-to/recover-and-troubleshoot.md)

### Gastown

> 本节原文仅标题，内容待补充。若 Gastown 指特定多 Agent 编排工具，请提供仓库链接与使用场景。

---

## 常见问题

### 自定义命令不生效

- 确认文件在 `.claude/commands/` 且扩展名为 `.md`
- 重启 `claude` 或检查是否在正确项目根目录启动

### Subagent 似乎在用主会话上下文

文件定义的 agent 应隔离；若行为异常，检查是否误用普通 prompt 而非 `@agent名`。

### GitHub 集成后 workflow 未触发

- 检查 App 是否安装到目标仓库
- 检查计划是否含 Web 版 Claude Code
- 查看 Actions 日志与 `gh` 登录状态

### GSD 太慢怎么办

- 缩小 Phase 范围
- 对非关键路径改用 Agent Teams 并行
- 确保 `Verify` 标准可自动化，减少文档往返

---

## 待确认事项

- [ ] **Gastown** 官方仓库、与 GSD/Agent Teams 的定位差异
- [ ] Claude Code Hooks 完整事件列表与 `settings.json` schema（以当前版本官方文档为准）
- [ ] `teammateMode` 除 `in-process` 外可选值及适用场景
- [ ] Sprites 定价、与 Claude 官方 Sandbox 的对比是否纳入课程
- [ ] GitHub 集成生成的 workflow 文件名与触发条件（`@claude` 精确语法）
