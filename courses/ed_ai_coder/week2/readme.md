# Week 2：Vibe Engineer — CLI 工具与 Claude Code 深度实践

## 目录

- [概述](#概述)
- [前置条件](#前置条件)
- [核心概念](#核心概念)
- [CLI 工具对比](#cli-工具对比)
- [Claude Code 快速上手](#claude-code-快速上手)
- [常用命令与快捷键](#常用命令与快捷键)
- [权限与 settings.local.json](#权限与-settingslocaljson)
- [会话管理](#会话管理)
- [Checkpoint 与回滚](#checkpoint-与回滚)
- [YOLO 模式与 Ralph Loops](#yolo-模式与-ralph-loops)
- [MCP、Skills 与 Plugins](#mcpskills-与-plugins)
- [选型决策矩阵](#选型决策矩阵)
- [常见问题](#常见问题)
- [待确认事项](#待确认事项)

---

## 概述

本模块面向**终端优先**的 AI 编程工作流：安装与配置 Claude Code、OpenCode、Amp 等 CLI Agent，并深入 Claude Code 的会话、权限、MCP/Skills/Plugins 扩展体系。

解决痛点：IDE 插件难以脚本化；需要在 CI、远程沙箱、多项目中复用同一套 Agent 能力。

---

## 前置条件

| 要求 | 说明 |
|------|------|
| 操作系统 | macOS / Linux / Windows（WSL 推荐） |
| 网络 | 可访问 Anthropic、OpenCode 等安装脚本 |
| 账号 | Claude Code 需有效订阅；OpenCode 可接免费或自备 API Key |
| 可选 | Node.js（部分 Plugin）；Docker（部分 MCP Server） |

---

## 核心概念

### `.claude` 项目目录

在运行 `claude` 的目录下会自动创建 `.claude/`，用于存放**项目级**配置：

```text
.claude/
├── settings.json          # 项目级设置（hooks、env、teammateMode 等）
├── settings.local.json    # 本机权限白名单（通常 gitignore）
├── skills/                # 项目级 Skills
├── commands/              # 自定义斜杠命令（Week 3）
├── agents/                # 自定义 Subagent 定义（Week 3）
└── ...                    # MCP 配置、插件状态等
```

也可在用户主目录配置**全局** Skills（对所有项目生效）。

### Claude Code 命令前缀

交互模式下以 `/` 开头的为**内置或扩展斜杠命令**（如 `/context`、`/compact`）。

---

## CLI 工具对比

| 工具 | 定位 | 安装 | 计费 |
|------|------|------|------|
| **Claude Code** | Anthropic 官方终端 Agent | 见下文 | 订阅 + 用量限制 |
| **OpenCode** | 开源 AI 编程 Agent | `curl -fsSL https://opencode.ai/install \| bash` | 内置免费模型或自备 Key |
| **Amp** | 第三方 Agent 产品 | [ampcode.com](https://ampcode.com/) | 见其定价页 |

### OpenCode 要点

- 启动：`opencode`
- `/models` — 查看可用模型
- `/connect` — 连接 Anthropic、Google、OpenAI、**本地 Ollama** 等

适合：希望**自托管模型**或**避免单一厂商锁定**的场景。

### Amp

- 商业产品，具体能力与 Claude Code 差异需对照官方文档（本笔记待扩充）。

---

## Claude Code 快速上手

### 安装

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### 首次启动

```bash
claude
```

首次使用建议顺序：

```bash
/login          # 登录 Anthropic 账号
/init           # 在当前项目根目录生成 CLAUDE.md（类似 AGENTS.md）
/context        # 查看上下文占用、MCP/Plugin/Skill 列表
/status         # 会话与用量（含周限额）
```

指定模型启动：

```bash
claude --model sonnet    # 或 opus、haiku 等，以 /model 列表为准
```

---

## 常用命令与快捷键

| 命令 | 作用 | 注意事项 |
|------|------|----------|
| `/login` | 登录 | 首次必做 |
| `/init` | 生成 `CLAUDE.md` | 生成后应人工精简 |
| `/context` | 上下文概览 | 含 MCP 工具列表占用 |
| `/compact` | 压缩历史为摘要 | ⚠️ 可能丢失细节，慎用 |
| `/status` | 用量与限额 | 关注 session/week 配额 |
| `/model` | 切换模型 | 复杂任务换强模型 |
| `/clear` | 清空对话 | 不保留摘要 |
| `/stats` | 历史使用统计 | — |

---

## 权限与 settings.local.json

Claude Code 执行 Bash 等操作前会请求许可。用户批准后，规则可写入 `.claude/settings.local.json`，下次**自动放行**。

### 文件路径

`.claude/settings.local.json`（建议加入 `.gitignore`，避免个人路径泄露）

### 示例

```json
{
  "permissions": {
    "allow": [
      "BASH(docker run:*)",
      "BASH(npm run test:*)",
      "BASH(uv run pytest:*)"
    ]
  }
}
```

### 匹配规则说明

| 字段 | 含义 |
|------|------|
| `BASH(docker run:*)` | 允许以 `docker run` 开头的任意命令 |
| `BASH(npm run test:*)` | 允许 `npm run test` 及子命令 |

> **安全提示**：过宽的白名单（如 `BASH(*)`）等同于关闭沙箱。仅放行已验证安全的命令模式。

---

## 会话管理

每次执行 `claude` 默认开启**新会话**。

### 恢复上次会话

```bash
claude --continue
```

### 命名会话

在 Claude Code 内：

```bash
/rename review_docs
```

退出后按名称恢复：

```bash
claude -r review_docs
# 或列出所有会话选择
claude --resume
```

```text
Data Flow: 命名会话

  Session "review_docs"
      │
      ├─ 对话历史（持久化）
      ├─ 已修改文件状态
      └─ claude -r review_docs → 恢复同一上下文
```

---

## Checkpoint 与回滚

```bash
/rewind
```

展示可回滚的检查点列表，将工作区与对话状态撤销到选定时间点。

**适用场景**：Agent 连续改错、需要回到「上一次正确状态」。

**限制**：不能替代 Git；重大里程碑仍应 `git commit`。

---

## YOLO 模式与 Ralph Loops

### YOLO（跳过权限确认）

```bash
claude --dangerously-skip-permissions
```

| 优点 | 风险 |
|------|------|
| 无人值守、自动化流畅 | 可执行任意 Shell；仅限可信环境与隔离沙箱 |

> ⚠️ 切勿在含生产密钥的本机主环境默认开启。

### Ralph Loops 插件

循环执行同一目标直至完成或达到最大迭代次数。

```bash
# 安装官方插件
/plugin install ralph-loop@claude-plugins-official

/context    # 确认插件已加载

/ralph-loop:ralph-loop "实现用户登录 API 并通过 pytest" --max-iterations 10
```

**Data Flow**：

```text
  目标 Prompt
      │
      ▼
  ┌─► 执行一轮 ──未达标──┐
  │         │            │
  │         ▼            │
  │     检查验收标准      │
  │         │            │
  └─────────┴── 达标 ───► 结束
            │
      达到 max-iterations → 强制结束
```

### 移除 MCP

```bash
claude mcp remove <mcp_name>
```

---

## MCP、Skills 与 Plugins

### 三者关系

| 类型 | 本质 | 上下文成本 | 分享方式 |
|------|------|------------|----------|
| **MCP** | 标准化工具协议（Server 暴露 Tools） | 高（工具 schema 常驻） | 需运行 Server |
| **Skills** | Markdown 指令 + 可选脚本 | 低（按需加载） | 复制文件夹即可 |
| **Plugins** | MCP + Skills 等的打包 | 中 | Claude Code 插件市场 |

### MCP 架构

```text
  Claude Code (MCP Host)
        │
        │  MCP Client
        ▼
  MCP Server ──► 外部 API / DB / 文件系统 / ...
```

**传输方式**：

| 模式 | 说明 |
|------|------|
| Local (stdio) | 本机子进程，最常见 |
| Remote | SSE（遗留）、**Streamable HTTP**（推荐方向） |

**发现 MCP Server 的资源**：

- [MCP Registry](https://registry.modelcontextprotocol.io/)（活跃度一般）
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)（官方示例）
- [mcp.so](https://mcp.so/)（社区市场）
- [glama.ai/mcp/servers](https://glama.ai/mcp/servers)

> **反模式**：挂载过多 MCP → 上下文被 tool schema 挤占 → 编码质量下降。

### Skills

MCP 之后引入；以 **Markdown 工作流** 为主，而非远程 Tool。

**目录结构**：

```text
.claude/skills/my-great-skill/
├── SKILL.md              # 元数据 + 触发说明 + 主指令
├── reference.md          # 可选：被 SKILL.md 引用的补充文档
└── scripts/
    └── run_check.py      # 可选：可执行脚本
```

**SKILL.md 概念结构**：

```markdown
---
name: api-review
description: 当用户要求审查 REST API 设计或提到 OpenAPI 时使用
---

# API Review Skill

## 工作流
1. 读取 `openapi.yaml`
2. 对照 checklist 输出问题清单
...
```

**关键特性**：

- Skill 正文**默认不进上下文**，仅在触发时加载 → 省 token
- 可放在**用户目录**（全局）或 **`.claude/skills`**（项目级）
- **需显式触发**：要在对话中说明「使用 xxx skill」，否则可能不被调用

**资源**：

- [anthropics/skills](https://github.com/anthropics/skills)
- [skills.sh](https://www.skills.sh/)

### Plugins

- **最易用**：一条 `/plugin install` 命令
- **仅 Claude Code**
- 可能包含超出需求的工具 → 注意 `/context` 体积

```bash
claude
/plugin
# 浏览、安装、管理插件
```

官方合集：[claude-plugins-official](https://github.com/anthropics/claude-plugins-official)

---

## 选型决策矩阵

| 需求 | 推荐 |
|------|------|
| 调用 GitHub、数据库、SaaS API | MCP |
| 团队内复用审查/发布 checklist | Skills |
| 快速体验官方打包能力（Ralph Loop 等） | Plugins |
| 上下文紧张、规则型任务 | Skills > MCP |
| 生态最广、工具最多 | MCP |

---

## 常见问题

### `/compact` 后 Agent「失忆」

正常现象。重要决策应写入 `CLAUDE.md`、Issue 或 `docs/`，而非仅依赖对话历史。

### MCP 安装后 `/context` 暴涨

移除不用的 Server：`claude mcp remove <name>`；或改用 Skill 封装窄接口。

### 权限反复弹出

检查 `settings.local.json` 的 `allow` 模式是否与真实命令一致（参数、路径差异会导致不匹配）。

### OpenCode vs Claude Code

OpenCode 开源、多提供商；Claude Code 与 Anthropic 模型、Plugin 生态绑定更深。可按任务分工具链。

---

## 待确认事项

- [ ] Amp 与 Claude Code 的功能对照表是否需单独一节？
- [ ] Ralph Loop 插件最新安装源是否仍为 `claude-plugins-official`？
- [ ] Streamable HTTP MCP 的项目级配置 JSON 示例需从官方文档摘录
