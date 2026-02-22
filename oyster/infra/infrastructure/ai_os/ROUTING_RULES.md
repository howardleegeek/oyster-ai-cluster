# ROUTING_RULES.md — 存储路由规则

> 所有 AI 产出必须按此规则路由到固定路径。

---

## 1. 产出类型分类

| 类型 | 说明 | 示例 |
|------|------|------|
| content | 营销/内容产出 | 博客、邮件、社交帖 |
| bd | 商务拓展 | outreach、partnership、follow-up |
| ops | 运营/流程 | SOPs、自动化脚本 |
| research | 研究/调研 | 竞品分析、技术调研 |
| infra | 基础设施 | Terraform、配置、部署 |

---

## 2. 项目目录结构

每个项目 (`projects/{project}/`) 必须包含：

```
{project}/
├── PROJECT.md           # 项目定义（目标、边界、关键联系人）
├── TASKS.md             # 任务清单（唯一数据源）
├── DIALOGUE.md          # 对话历史（append-only）
├── memory/
│   ├── episodic/       # 事件记忆（已发生的事情）
│   ├── semantic/       # 语义记忆（知识/概念）
│   └── rules/          # 项目特定规则
├── outputs/
│   ├── content/
│   ├── bd/
│   ├── ops/
│   ├── research/
│   └── infra/
├── inbox/               # 待处理文件
└── archive/             # 归档（永不删除）
```

---

## 3. 命名规则

### 输出文件

- 格式：`YYYY-MM-DD_slug.md`
- 示例：`2026-02-14_sanctum_outreach.md`

### 对话日志

- 格式：`DIALOGUE_YYYY-MM-DD.md`
- 示例：`DIALOGUE_2026-02-14.md`

### 任务标记

- 待办：`[ ] 任务描述`
- 进行中：`[→] 任务描述`
- 完成：`[✓] 任务描述`

---

## 4. 跨项目路由

当任务涉及多个项目时：

1. **主项目优先**：哪个项目是主要受益者，就归属哪个
2. **其他项目标注**：在 TASKS.md 中用 `@{project}` 标注关联项目
3. **不重复创建**：已存在的产出不重复生成，只引用

---

## 5. 时间意图捕获

对话中出现以下时间词时，必须写入 TASKS.md 的 due 字段：

| 时间词 | 解析 |
|--------|------|
| 明天 | +1 day |
| 后天 | +2 days |
| 周一/周二... | 下周对应日期 |
| 月末 | 当月最后一天 |
| 具体日期 | 直接写入 |

---

## 6. 快速路由表

```
projects/Puffy/outputs/content/
projects/Puffy/outputs/bd/
projects/Puffy/outputs/ops/
projects/Puffy/outputs/research/
projects/Puffy/outputs/infra/

projects/Oyster/outputs/content/
projects/Oyster/outputs/bd/
... (同上)

projects/Research/outputs/research/
projects/Infra/outputs/infra/
```

---

## 7. 禁止事项

- 禁止在 `ai_os/` 根目录创建输出文件
- 禁止在 `memory_global/` 直接创建内容
- 禁止跨项目修改（除非显式要求）
