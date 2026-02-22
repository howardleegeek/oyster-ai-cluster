# AI OS — 个人 AI 工作流系统

> 这是一个个人 AI 操作系统，用于管理 AI 产出、任务追踪和长期记忆。

---

## 系统架构

```
infrastructure/
└── ai_os/
    ├── CONSTITUTION.md     # 宪法级规则
    ├── ROUTING_RULES.md    # 存储路由
    ├── AGENTS.md           # OpenCode 执行手册
    ├── identity/           # 身份定义
    ├── memory_global/      # 全局记忆
    ├── projects/           # 项目目录
    │   ├── Puffy/
    │   ├── Oyster/
    │   ├── Research/
    │   ├── Growth/
    │   └── Infra/
    ├── scripts/            # 自动化脚本
    └── logs/               # 运行日志
```

---

## 快速开始

### 1. 启动 AI 会话

```bash
# 在 infrastructure 仓库根目录
cd /Users/howardli/Downloads/infrastructure

# 启动 OpenCode 并指定项目
opencode
# 或
codex
```

### 2. 创建新产出

告诉 AI：

> "在 projects/Oyster 下写一份 BD outreach 邮件，保存到 outputs/bd/，更新 TASKS 和 DIALOGUE。"

AI 会自动：
1. 识别产出类型（bd）
2. 创建 `projects/Oyster/outputs/bd/YYYY-MM-DD_slug/index.md`
3. 更新 `projects/Oyster/TASKS.md`
4. 追加到 `projects/Oyster/DIALOGUE.md`

### 3. 追踪任务

- 查看 `projects/{project}/TASKS.md`
- 状态标记：`[ ]` 待办 / `[→]` 进行中 / `[✓]` 完成
- 截止日期：`@due(YYYY-MM-DD)`

---

## 脚本使用

### 晨报（每天早上）

```bash
python3 ai_os/scripts/morning_brief.py
```

输出：`ai_os/logs/daily/YYYY-MM-DD_morning.md`

包含：
- 所有项目的未完成任务
- 今日到期任务
- 本周到期任务

### 存储审计（每周）

```bash
python3 ai_os/scripts/storage_audit.py
```

输出：`ai_os/logs/weekly/YYYY-MM-DD_storage_audit.md`

包含：
- inbox 中超过 3 天未处理的文件
- 归档建议

---

## 核心规则

### 必须遵守

1. **所有产出写入 ai_os/ 目录**
2. **TASKS.md 是唯一任务数据源**
3. **DIALOGUE.md 是 append-only**
4. **一次只处理一个项目**

### 禁止

- ❌ 删除任何历史文件
- ❌ 在 ai_os/ 外创建输出
- ❌ 交付包含 TODO 的代码

---

## 项目说明

| 项目 | 用途 |
|------|------|
| Puffy | 主产品 |
| Oyster | Oyster Labs / 研究 |
| Research | 调研/实验 |
| Growth | 增长/营销 |
| Infra | 系统维护 |

---

## 更多信息

- [宪法规则](./CONSTITUTION.md)
- [路由规则](./ROUTING_RULES.md)
- [执行手册](./AGENTS.md)

---

## 版本

- **V3** — 2026-02-14
- 防重建保险丝已生效
- 脚本已就位
