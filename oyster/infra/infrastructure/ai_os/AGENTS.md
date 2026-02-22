# AGENTS.md — OpenCode/Codex 执行手册

> ⚠️ **PRIORITY**: This file is superseded by `flight_rules.md`. If any conflict exists, follow `flight_rules.md`.

---

## 0. Flight Rules（最高优先级）

**必须遵守 `ai_os/flight_rules.md`**：
- flight_rules.md 是最高规则，高于本手册其他内容
- 若本手册与 flight_rules.md 冲突，以 flight_rules.md 为准

---

## 1. 懒加载原则

**不要自动读取大目录**：
- 除非明确需要，不要遍历整个项目目录
- 只在需要时读取特定文件
- 优先使用 `glob` + `grep` 做 targeted 搜索

**例外**：
- 首次启动需要读取 PROJECT.md 和 TASKS.md
- 需要了解项目上下文时读取 memory/

---

## 2. 输出流程

当需要创建新产出时，按以下步骤：

### Step 1: 识别产出类型

判断产出属于哪类：
- content → `outputs/content/`
- bd → `outputs/bd/`
- ops → `outputs/ops/`
- research → `outputs/research/`
- infra → `outputs/infra/`
- **byzantine-collider** → `outputs/byzantine-collider/`

### Step 2: 确定目标项目

确认项目名称（Puffy / Oyster / Research / Growth / Infra）

**Context-Aware 自动推断**：
- 在开始任务前，读取最近 20 条事件：`ai_os/events/YYYY-MM.ndjson`
- 如果存在 `intent.set` 事件，用该 intent 推断 artifact_type
- 如果存在 `context.browser` 事件，用 domain 推断项目（如 sanctum.so → Oyster BD）
- VS Code 扩展会上报 workspace path，可用于推断项目

### Step 3: 创建输出文件

路径格式：`outputs/{type}/YYYY-MM-DD_slug/`
- 创建目录
- 创建 `index.md`
- 如有多文件，在目录内组织

### Step 4: 更新 TASKS

在 `projects/{project}/TASKS.md` 中：
- 添加任务条目
- 标记状态（进行中/完成）
- 如有截止日期，写入 due 字段

### Step 5: 追加 DIALOGUE

在 `projects/{project}/DIALOGUE.md` 末尾追加：
- 日期和时间
- 任务概述
- 产出位置

### Step 6: 写入 NDJSON Event（强制）

**必须写入事件到 `ai_os/events/YYYY-MM.ndjson`**：
- 格式：每行一个 JSON 对象（NDJSON）
- 必须字段：ts, actor, project, type, summary, refs
- 事件类型：artifact.created, task.created, task.completed, brief.morning, audit.storage 等

**推荐方式（使用 emit_event.py）**：
```bash
# 方式 1: 使用 emit_event.py 脚本（推荐）
python3 ai_os/scripts/emit_event.py \
  --project Oyster \
  --type artifact.created \
  --summary "Drafted outreach email" \
  --ref artifact_path=ai_os/projects/Oyster/outputs/bd/2026-02-14_outreach/index.md \
  --artifact_type bd

# 方式 2: 手动追加（备选）
echo '{"ts":"2026-02-14T22:45:00-08:00","actor":"agent","project":"Oyster","type":"artifact.created","summary":"Drafted outreach email.","refs":{"artifact_path":"ai_os/projects/Oyster/outputs/bd/2026-02-14_outreach/index.md"},"artifact_type":"bd"}' >> ai_os/events/2026-02.ndjson
```

**Events are append-only**：永不修改历史事件行。

---

## 3. 时间意图捕获

对话中出现以下词汇时，**必须**更新 TASKS.md 的 due 字段：

| 词汇 | 解析 |
|------|------|
| 明天 | +1 day |
| 后天 | +2 days |
| 这周 | 本周五 |
| 下周 | 下周一 |
| 月末 | 当月最后一天 |
| X号 | 具体日期 |

**示例**：
```
- [ ] 完成 BD outreach @due(2026-02-16)
```

---

## 4. 项目隔离规则

**默认**：一次会话只处理一个项目

**跨项目条件**：
- 显式要求跨项目协作
- 明确的依赖关系（必须先完成 A 才能做 B）

**跨项目执行方式**：
1. 先完成主项目的任务
2. 再切换到下一个项目
3. 在对话中明确标注切换

---

## 5. 质量门禁

### 代码产出

- **必须可运行**：运行测试验证
- **禁止 TODO/FIXME**：交付即完成
- **依赖明确**：requirements.txt / package.json 必须更新

### UI 产出

- **必须自测**：改动后运行测试
- **必须验证**：无 JS 错误、无 console error

### 文档产出

- **必须有验证方式**：说明如何验证内容正确性
- **必须关联任务**：写入 TASKS

---

## 6. 禁止事项

### 禁止

- ❌ 修改或删除历史 DIALOGUE
- ❌ 在 `ai_os/` 根目录创建输出
- ❌ 同时处理超过 2 个项目
- ❌ 交付包含 placeholder 的代码

### 强制

- ✅ 每次产出必须更新 TASKS
- ✅ 每次会话结束必须追加 DIALOGUE
- ✅ 遇到不确定必须问用户

---

## 7. 引用规范

对话中引用信息时：

```
- 引用 TASKS：使用 "TASKS.md 第 X 条"
- 引用记忆：使用 "memory/{project}/memory/semantic/{file}"
- 引用产出：使用 "outputs/{type}/YYYY-MM-DD_slug/"
```

---

## 8. 脚本使用

### 事件发射器（任何产物/任务变更必须用）

```bash
python3 ai_os/scripts/emit_event.py \
  --project Oyster \
  --type artifact.created \
  --summary "Created BD outreach email" \
  --ref artifact_path=ai_os/projects/Oyster/outputs/bd/2026-02-14_outreach/index.md \
  --artifact_type bd
```
输出：追加到 `ai_os/events/YYYY-MM.ndjson`

### 晨报脚本

```bash
python3 ai_os/scripts/morning_brief.py
```
输出：`ai_os/logs/daily/YYYY-MM-DD_morning.md` + 自动写 event

### 存储审计

```bash
python3 ai_os/scripts/storage_audit.py
```
输出：`ai_os/logs/weekly/YYYY-MM-DD_storage_audit.md` + 自动写 event

### 周复盘

```bash
python3 ai_os/scripts/weekly_review.py
```
输出：`ai_os/logs/weekly/YYYY-MM-DD_weekly_review.md` + 自动写 event

---

## 9. 初始化检查

首次启动时，Agent 应：

1. ✅ 确认 `CONSTITUTION.md` 存在
2. ✅ 确认 `ROUTING_RULES.md` 存在
3. ✅ 读取目标项目的 `PROJECT.md` 和 `TASKS.md`
4. ✅ 如无 `TASKS.md`，创建空白模板

---

## 10. 错误处理

| 错误 | 处理方式 |
|------|----------|
| 找不到项目目录 | 创建它 + PROJECT.md |
| 找不到 TASKS | 创建空白模板 |
| 权限问题 | 报告用户 |
| 路径冲突 | 使用 slug 区分 |

---

## 11. 工作区边界

**严格限定工作范围**：
- **默认只写 ai_os/ 目录**：所有 AI 产出必须写入 `infrastructure/ai_os/`
- **禁止写入仓库根目录**：`infrastructure/` 根目录的文件（capabilities.py, docker-compose.yml, .env.example, .sops.yaml）除非用户明确要求，否则一律不修改
- **外部路径一律拒绝**：用户若指定 ai_os/ 以外的路径，AI 必须拒绝并给出 ai_os 内替代路径

**例外**：
- 用户明确要求修改根目录文件
- 执行脚本需要调用根目录组件（但必须先写影响分析）

---

## 12. 防重建硬约束

**System skeleton already exists**:
- 目录结构已存在，**永不重建**
- 只允许增量编辑现有文件

**No duplicate templates**:
- 模板变更必须 in-place（原地修改）
- 禁止复制模板到新位置

---

## 13. 影响分析前置

若用户要求修改仓库根目录文件，必须先输出：
1. **影响分析**：哪些文件受影响
2. **变更计划**：具体改什么
3. **等待确认**：等用户明确同意后才能执行
