# 代码工程 SOP 专家团（QwenWork 版）

把"聊完就散"的开发协作变成**先规划、可验收、能连跑**的团队级工程流程。13 个角色（4 常驻 + 9 按需）由主理人按需求信号调度，9 个技能覆盖需求、架构、设计、栈约定、质量清单、交付契约与发版，四道硬闸门由一个零依赖 Python CLI 执行，**退出码是唯一判据**。

本仓库是 [code-sop-team-zcode](https://github.com/wangqiqi/code-sop-team-zcode) 的 QwenWork 移植版，两者并列维护、流程语义一致，差异见文末「版本与移植说明」。

> **免责声明**：本套件是工程流程工具，不替代专业判断。架构取舍、安全结论与发版决定仍需由负责人复核后使用。

## 它解决什么问题

- **"看着差不多就标完成"** → 每个任务的验收必须是一条能跑的的命令，描述性验收直接判 FAIL
- **"边聊边写，越写越散"** → 没有 `PLAN_APPROVED` 就不许写业务代码
- **"改了三版还在打补丁"** → 同一任务连续失败 2 次触发补丁循环闸，强制立 SPIKE 定位根因
- **"发版全靠感觉"** → 出口闸要求任务全绿 + `VERIFY` 退出码 0 才能打版

四条规则都由 CLI 落地，不靠模型自觉。

## 团队阵容

### 常驻核心（每场必到）

| 角色 | 职责 |
|------|------|
| 主理人（Team Lead） | 开场问询、路线判定、派单、收口汇报 |
| 产品经理 | 需求澄清、验收标准可执行化、范围谈判 |
| 架构师 | 分层与边界、依赖方向、ADR、技术债 |
| 交付工程师 | 任务拆分、验收命令、交付七维 |

### 按需专家（需求信号触发，平时不打扰）

`UX 设计师` · `冲刺规划师` · `技术探针` · `代码审查员` · `QA 工程师` · `安全工程师` · `数据工程师` · `发布工程师` · `工程管家`

在 QwenWork 里，角色是 `skills/sop-team/references/roles/*.md` 的手册；`task` 子任务可用时按手册派单，不可用时进单会话代行模式并**显式标注**，不冒充独立成员的结论。

## 工作流程与四道硬闸门

```
开场问询 → 规划（PLAN_APPROVED）→ 逐任务执行 → 验收留证 → 审查/走查 → 出口闸 → 发版
```

| 闸门 | 命令 | 判据 |
|------|------|------|
| 规划闸 | `gate-check` | 无真实日期的 `PLAN_APPROVED` → 禁止写业务代码 |
| 验收闸 | `task-verify` | 验收命令非 0 → FAIL；`manual:` 必须 `--evidence` 留证（否则 rc=3） |
| 出口闸 | `verify` | 任务非全绿或 `VERIFY` 非 0 → FAIL；残项需 `--force` 且明确接受 |
| 补丁循环闸 | `followup` | 同任务连续失败 2 次 → `FOLLOWUP-GATE`，必须立 `SPIKE-*` |

退出码：`0` 通过 · `1` BLOCK/FAIL · `2` 参数/环境错 · `3` 等待人工证据。**任何非 0 都不得继续编码、标完成或提交。**

## 安装

### 方式 1 · 上传套件（推荐）

1. 下载 [`dist/code-sop-team-2.4.0.zip`](dist/code-sop-team-2.4.0.zip)
2. 客户端左侧「扩展」→「专家套件」→ 右上「+ 添加」→「上传套件」
3. 选择刚才的 ZIP → 安装
4. 新任务里输入 `/`，选中套件内的技能（如 `/sop-team`）即可开始

### 方式 2 · 目录直装（零 UI）

把仓库里的 `code-sop-team/` 整个目录复制到：

```
%USERPROFILE%\.qwenworkcn\plugins-custom\code-sop-team\
```

macOS / Linux 对应 `~/.qwenworkcn/plugins-custom/code-sop-team/`，重启客户端生效。

### 验证安装

新建任务输入 `/sop-team`，主理人应先做**环境自检**（找 Python 解释器与 `sop_gate.py`），再发开场卡。手动验证闸门：

```powershell
python skills\sop-team\scripts\preflight.ps1 -Root <你的代码目录>
python bin\sop_gate.py doctor --root <你的代码目录>
```

### 卸载

客户端「专家套件」卡片右侧菜单移除；直装则删除 `plugins-custom\code-sop-team`。技能不会改动你的业务仓库，状态只写在项目根的 `.qwenwork/sop/`（`init` 会自动加进 `.gitignore`）。

## 快速指令

| 指令 | 用途 |
|------|------|
| `/sop-team` + 需求描述 | 主理人接管：开场问询 → 规划 → 你确认 → 执行 → 收口发版 |
| `/sop-team` + "review 一下" | 只走代码审查，按 Blocker/High 分级给结论 |
| `/sop-gate` | 手动跑闸门，如 `task-verify TASK-002`、`verify`、`doctor` |
| `/product-spec` | 需求说不清时先把目标、验收标准与 Out of scope 冻结 |
| `/architecture-design` | 分层、边界、依赖方向、要不要重构 |
| `/ux-design` | 页面结构、交互流程、六态、视觉 token |
| `/quality-checklists` | 安全 / API / 测试 / 性能 / 补丁循环专项检查 |
| `/delivery-contracts` | 交付七维验收、测试报告、使用说明书 |
| `/release-ops` | Git 纪律、发版四选一、semver、脚手架 |

## 技能清单

| 技能 | 作用与内置方法 |
|------|----------------|
| `sop-team` | 主理人编排：**第 0 步环境自检**、5 张开场卡、路由表、Phase 0–5、Workflow 0/A–J、12 份角色手册按需派单、异常兜底矩阵 |
| `sop-gate` | 四道闸执行器：`init` `gate-check` `plan-check` `task-verify` `verify` `next-task` `followup` `approve` `set` `doctor` + 可选 git pre-commit；fail-closed、原子锁、超时杀进程树 |
| `product-spec` | 需求澄清四问、用户故事、**验收标准可执行化**、MoSCoW、范围谈判 |
| `architecture-design` | 边界划分、依赖方向、ADR、技术债记账、数据层（schema/迁移/索引/备份/一致性） |
| `ux-design` | 信息架构、交互流程、**六态设计**、视觉 token、可用性走查 |
| `stack-conventions` | TS/JS/ESLint、React/Vue/Svelte/Next、Python/Go/Java、Rust/C/C++ 的编码约定与各栈完成判据 |
| `quality-checklists` | 安全清单、API 契约、测试分层、调试循环、**补丁循环拦截**、性能手册、重构协议 |
| `delivery-contracts` | 交付七维验收、测试报告契约、使用说明书契约 |
| `release-ops` | Git 纪律、发版四选一 + semver、部署、脚手架、长程三层规划 |

## 第 0 步环境自检

QwenWork 安装包不自带 Python 解释器，套件开工前先自检，避免在缺解释器/缺脚本的机器上白跑一轮：

1. **开场即查**：跑 `skills/sop-team/scripts/preflight.ps1`（或 `preflight.sh`），它按 **PATH → `~/.qwenworkcn/bin/.runtime-preparation.json` → 其他受管 Python → 常见安装位置** 找一个 3.8+ 解释器，用 `-V` 验真并跳过 Windows Store 占位 `python3.exe`
2. **目录确定后**：同一脚本加 `-Root <代码目录>`，内部跑 `doctor` 并只摘 FAIL / WARN
3. **结论入汇报**：解释器 · 脚本 · 钩子 · 是否降级

四条路都找不到时不会静默放行：显式声明「软约束降级模式」，流程与角色手册照常，但硬拦截不生效，且不得声称全流程闭环。

## 状态与运行要求

- 状态目录：`<项目根>/.qwenwork/sop/`（`plan.md`、`evidence.json`、`followup.json`）
- 项目根探测：`--root` > `SOP_PROJECT_ROOT` > 向上找 `.git` > 当前目录
- 运行时：任意 Python 3.8+（纯标准库）
- 回归自测：`python tests/test_sop_gate.py`（43 个用例，零依赖）。改过闸门脚本后必须全绿

## 常见用法

- 我要开发一个功能，先冻结目标、拆任务，等我确认再执行
- 帮我审查当前改动能不能合并，按严重度列出 Blocker 和 High
- 这两个技术方案帮我对比一下，给出明确推荐和任务拆分建议
- 这 bug 我已经修了三次还没好，帮我判断该不该换个思路
- 这个接口谁都能传 userId，帮我看看安全上有没有洞
- 我要加个字段还要写迁移，怎么保证能回滚
- 按清单发个版，先跑 verify，绿了再打 tag

## 连接器（可选增强）

| 你想做的事 | 不连也能做 | 连上后更顺 |
|-----------|-----------|-----------|
| 代码审查 | 贴 diff 或本地读文件 | 直接读 PR diff 并把结论发回 PR |
| 任务规划 | TASK 落在 `plan.md` | 同步成 Jira / Linear issue 并回写状态 |
| 交付归档 | 本地文件 | 发布成钉钉文档 / Notion 页面 |

> 所有技能在没有连接器时均可正常使用。配置方式见 `code-sop-team/CONNECTORS.md`。

## 上架公开市场

当前企业后台只开放「企业市场 / 专属市场」的自助上传与上架审批；官方公开市场由平台运营，第三方内容需通过千问办公开放平台 / ISV 渠道提交审核。`dist/` 里的 ZIP 就是提交物：清单含 `.qwenwork-plugin/plugin.json` 与根目录 `plugin.json`，`name` 为 `code-sop-team`。

## 版本与移植说明

- 版本：`2.4.0`（与 zcode 版语义对齐，逐条对应四道闸门）
- 13 个 ZCode subagent → `skills/sop-team/references/roles/` 角色手册，通过 `task` 派单
- 插件元数据：`.zcode-plugin/plugin.json` → `.qwenwork-plugin/plugin.json`
- 状态目录：`.zcode/sop/` → `.qwenwork/sop/`；CLI 常量、git 钩子与 43 个回归用例同步更新
- 开场问询改用 `question` 工具逐张发卡；卡片不可用时降级为正文逐项询问
- 头像（`avatars/`）保留为素材
- 新增第 0 步环境自检，把"缺 Python"从静默放行改成显式降级声明

## 致谢

流程设计来自 Code Engineering SOP Team（ZCode 版）的实践沉淀；感谢所有在真实交付里被这些闸门拦下来过的人——正是那些拦截让这套流程值得存在。