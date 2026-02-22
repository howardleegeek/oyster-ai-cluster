# CONSTITUTION.md — AI OS 宪法级规则

> 本文件是 AI OS 系统的最高规则，任何子模块不得与之冲突。

---

## 1. 工作区边界

**所有 AI 产出必须写入 `ai_os/` 目录**：
- 根路径：`infrastructure/ai_os/`
- 禁止写入 `infrastructure/` 根目录或任何其他目录（除非明确被要求）
- 任何新项目/模块的边界都必须在 `ai_os/projects/` 内定义

---

## 2. 任务唯一数据源

- **TASKS.md 是任务的唯一真实来源**
- AI 不得在对话中口头描述"任务状态"，必须引用 TASKS.md 中的条目
- 所有任务状态变更必须更新 TASKS.md

---

## 3. 对话追加式

- **DIALOGUE*.md 文件是 append-only（只追加）**
- 禁止修改或删除历史对话记录
- 每次会话结束后，AI 必须将对话摘要追加到对应项目的 DIALOGUE.md

---

## 4. 数据不删除

- **禁止删除任何已创建的文件**
- 归档使用移动到 `archive/` 子目录，而非删除
- 日志文件永久保留

---

## 5. 存储路由

所有产出必须按类型路由到固定路径：

| 类型 | 路径规则 |
|------|----------|
| content | `projects/{project}/outputs/content/` |
| bd | `projects/{project}/outputs/bd/` |
| ops | `projects/{project}/outputs/ops/` |
| research | `projects/{project}/outputs/research/` |
| infra | `projects/{project}/outputs/infra/` |
| inbox | `projects/{project}/inbox/` |

详见 `ROUTING_RULES.md`

---

## 6. 记忆三层

AI 记忆按生命周期分层：

| 层级 | 位置 | 生命周期 |
|------|------|----------|
| 工作记忆 | TASKS.md | 当前会话 |
| 项目记忆 | `projects/{project}/memory/` | 项目周期 |
| 全局记忆 | `memory_global/` | 长期 |

---

## 7. 质量门禁

- **代码必须可运行**：禁止交付 "TODO" / "FIXME" / placeholder
- **输出必须可验证**：spec 必须包含验证命令
- **UI 改动必须自测**：前端改动必须跑通测试

---

## 8. 并发纪律

- **一次只处理一个项目**：除非明确要求跨项目协作
- **任务不串行则并行**：独立任务应并行执行
- **依赖链必须显式**：spec 中 `depends_on` 只写硬依赖

---

## 9. 防重建保险丝

### System is pre-existing

- **不得重建骨架**：目录结构一旦创建，禁止重新生成
- **禁止重复造模板**：模板只允许在 `templates/` 维护
- 只允许：增量更新现有文件、新增具体产物

### No duplicate templates

- 任何通用模板必须在 `ai_os/templates/` 集中维护
- 其他位置只能引用，不得复制

---

## 10. 执行入口

- **README.md** 是系统入口，描述运行方式
- **AGENTS.md** 是 OpenCode/Codex 执行手册
- **ROUTING_RULES.md** 是存储路由的完整规则
