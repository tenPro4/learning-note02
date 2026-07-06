# Week 1：Vibe Coding 基础与 Agent 上下文工程

## 目录

- [概述](#概述)
- [前置条件](#前置条件)
- [核心概念](#核心概念)
- [AI 编程工具全景](#ai-编程工具全景)
- [AGENTS.md：项目级 Agent 指令](#agentsmd项目级-agent-指令)
- [工作流演进（2025 → 2026）](#工作流演进2025--2026)
- [模型选型参考](#模型选型参考)
- [OpenRouter：统一模型网关](#openrouter统一模型网关)
- [成功 Vibe Coding 的五项原则](#成功-vibe-coding-的五项原则)
- [进阶与注意事项](#进阶与注意事项)
- [待确认事项](#待确认事项)

---

## 概述

**Vibe Coding**（氛围编程）指开发者借助 AI Agent 以自然语言驱动编码、调试与交付的开发范式。本模块聚焦三件事：

1. 选对工具与模型
2. 用 `AGENTS.md`（及同类文件）把项目规范注入 Agent 上下文
3. 建立可验证、可迭代的协作工作流

核心痛点：Agent 默认不了解你的项目约定；没有结构化指令时，输出风格漂移、过度防御性编码、上下文浪费。

---

## 前置条件

| 类别 | 要求 |
|------|------|
| 环境 | 现代终端（bash/zsh/PowerShell）、Git、Node.js（部分 CLI 工具） |
| 账号 | 至少一个 AI 编程产品订阅或 API Key（见工具表） |
| 可选 | [uv](https://docs.astral.sh/uv/) 作为 Python 包/运行管理器（若项目使用 Python） |

---

## 核心概念

| 术语 | 含义 |
|------|------|
| **Agent** | 能读代码、改文件、执行命令、调用工具的 LLM 驱动编程助手 |
| **AGENTS.md** | 项目级 Markdown 指令文件，在会话启动时被注入上下文 |
| **Context Window** | 模型单次可处理的 token 上限；工具/MCP/长对话会快速占满 |
| **Vibe Coding** | 以目标与验收标准驱动，而非逐行微操代码 |

各工具对「项目指令文件」的命名约定：

| 工具 | 指令文件名 |
|------|-----------|
| Cursor、Codex、GitHub Copilot | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| Antigravity (Google) | `GEMINI.md` |

文件可放在**仓库根目录**或**任意子目录**；子目录内的文件通常对该路径下的工作生效（具体行为因工具而异）。

---

## AI 编程工具全景

| 工具 | 形态 | 计费模式 | 链接 |
|------|------|----------|------|
| **Cursor** | 独立 IDE（VS Code 分支） | 订阅制 | [cursor.com](https://cursor.com/) |
| **GitHub Copilot** | VS Code / JetBrains 插件 | 订阅制 | [Marketplace](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat) |
| **OpenAI Codex** | VS 插件 / CLI | 按量计费 | [openai.com/codex](https://openai.com/codex/) |
| **Claude Code** | CLI / 插件 | 订阅制 | [code.claude.com](https://code.claude.com/) |
| **Antigravity** | 独立应用（Google） | — | [antigravity.google](https://antigravity.google/) |

> **选型建议**：IDE 深度集成选 Cursor/Copilot；终端/自动化/CI 集成选 Claude Code/Codex CLI；多模型实验可配合 OpenRouter（见下文）。

---

## AGENTS.md：项目级 Agent 指令

### 作用

`AGENTS.md` 是一份**自然语言规范**，在 Agent 启动或进入相关目录时被加载，用于约束：

- 项目目标与成功标准
- 代码风格与架构约定
- 工具链命令（如 `uv run` 而非 `python3`）
- 禁止事项（过度防御、无用注释等）

### 推荐结构模板

```markdown
# Project Summary

一句话说明项目是什么、解决什么问题。

## Goals

- 目标 1
- 目标 2

## Success Criteria

- [ ] 可运行的验收条件（测试通过、API 响应格式等）

## Code Standards

1. **简单优先** — 不过度抽象，不提前优化
2. **注释克制** — 仅解释非显而易见的业务/技术决策
3. **文档精简** — README 短而准，不用 emoji 堆砌
4. **异常处理** — 避免过度防御；非必要不用 `isinstance`；只在边界处捕获异常
5. **Python 工具链** — 使用 uv；始终 `uv run <cmd>`，配合 `pyproject.toml`；禁止裸 `python3 script.py`

## Commands

| 任务 | 命令 |
|------|------|
| 安装依赖 | `uv sync` |
| 运行测试 | `uv run pytest` |
| 启动服务 | `uv run uvicorn app.main:app --reload` |
```

### 维护策略

- **投入时间编写**：2025 年起，高质量 `AGENTS.md` 是区分业余与专业 Vibe Coding 的关键
- **配套补充文件**：复杂领域可拆分为 `docs/architecture.md`、`docs/api-conventions.md`，在 `AGENTS.md` 中引用
- **持续修剪**：随项目演进重写；上下文腐化时考虑 `/compact` 或新会话 + 精简后的 `AGENTS.md`
- **定期重置上下文**：长会话后质量下降是常态，不要恋战

### 2026 心态转变

| 2025 | 2026 |
|------|------|
| 微观管理、逐步审批 | **YOLO** — 给目标，让 Agent 跑 |
| 频繁手动 reset | **Ralph Loops** — 循环直到达标 |
| 单 Agent 串行 | **多 Agent / Swarm / 编排** |

> 转变不等于放弃验证：信任执行，但用测试、CI、Review 做「Trust but verify」。

---

## 工作流演进（2025 → 2026）

### 2025 典型模式

1. **Micro-manage** — 逐步批准每一步；频繁 reset 上下文
2. **Plan → Execute → Review → Test** — 结构化四步，人工卡点
3. **SDD（Spec-Driven Development）** — 先写规格再实现；Trust but verify

### 2026 典型模式

1. **YOLO** — `--dangerously-skip-permissions` 等模式，全权限自动执行
2. **Ralph Loops** — 插件驱动：同一目标循环 N 次直至满足验收
3. **Multi-Agent** — 主 Agent 编排；子 Agent 并行研究/实现/测试

```text
Data Flow (2026 多 Agent 简图)

  用户目标
      │
      ▼
  Lead Agent ──委派──► Subagent A (研究)
      │                      │
      ├──委派──► Subagent B (实现)──► 仅返回结果摘要
      │                      │
      └──汇总──► 验证 / PR / 交付
```

---

## 模型选型参考

实时 benchmark 与定价对比：[Artificial Analysis](https://artificialanalysis.ai/)

选型维度：

- **推理 vs 速度**：复杂架构用 Opus/推理模型；批量重构可用 Sonnet/Haiku
- **上下文长度**：长代码库优先选大窗口模型
- **工具调用能力**：Agent 场景需强 function calling / computer use 支持
- **成本**：订阅制 IDE vs 按 token 计费的 API

---

## OpenRouter：统一模型网关

**官网**：[openrouter.ai](https://openrouter.ai/)

### 解决的问题

传统方式调用 OpenAI、Anthropic、Google 等模型需分别注册、分别管理 API Key、分别适配 SDK。OpenRouter 作为**中间层**，用**单一账号 + 单一 API** 路由到多家前沿模型。

### 基本用法概念

```python
# 概念示例：OpenAI 兼容接口，仅换 base_url 与 model 名
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

response = client.chat.completions.create(
  model="anthropic/claude-sonnet-4",  # 格式：provider/model-id
  messages=[{"role": "user", "content": "Hello"}],
)
```

### 配置项说明

| 配置 | 说明 |
|------|------|
| `OPENROUTER_API_KEY` | 在 OpenRouter 控制台创建 |
| `model` | 格式为 `provider/model-name`，见模型列表页 |
| 免费模型 | 可用，但需在 Settings 中显式开启；**数据可能用于训练** |

> ⚠️ **隐私警告**：使用免费模型且开启训练选项时，提示词与代码会进入训练管线。商业/敏感代码库请使用付费模型并阅读数据政策。

---

## 成功 Vibe Coding 的五项原则

1. **投资 AGENTS.md** — 简洁写明：规格（spec）、风格（style）、成功标准（success）
2. **从简单开始** — 最小可运行切片，再扩展
3. **增量迭代** — 小步提交；持续跑测试；对照 Success Criteria 验收
4. **不偷懒** — 质疑 Agent 输出；要求证据（测试日志、diff 说明）
5. **优雅处理挫败感** — 上下文腐化就换会话；规范不清就改 `AGENTS.md`，而非反复纠偏

---

## 进阶与注意事项

### AGENTS.md 反模式

- 复制整本风格指南（占满上下文）
- 前后矛盾的规则（「要快」又「要 100% 测试覆盖」）
- 只写禁止项、不写推荐命令与目录结构

### 上下文管理

- 工具/MCP/Skills 越多，有效编码上下文越少
- 长会话后优先：新会话 + 精简规范 + 明确当前任务文件列表

### 与 Week 2/3 的衔接

- Week 2：Claude Code CLI、MCP、Skills、Plugins 详解
- Week 3：自定义命令、Subagents、Hooks、GitHub 集成、多 Agent 编排

---

## 待确认事项

- [ ] 本课程默认主推工具是 Cursor 还是 Claude Code？（影响示例命令统一性）
- [ ] 学员 Python 版本与 uv 是否为硬性要求？
- [ ] Antigravity / GEMINI.md 是否有官方 AGENTS 等价物文档链接需补充？
