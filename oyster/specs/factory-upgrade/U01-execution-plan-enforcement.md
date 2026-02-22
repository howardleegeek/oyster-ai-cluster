---
task_id: U01
title: "Spec 模板强制执行计划段"
depends_on: []
modifies: ["specs/clawmarketing/SHARED_CONTEXT.md"]
executor: glm
---

## 目标
所有 spec 模板新增「执行计划」必填段，agent 必须先输出计划再写代码。

## 学到的
文章要求：先输出执行计划 → 再输出代码。包含里程碑拆分、模块边界、数据模型、API 列表、风险清单。
我们的问题：S01-S18 直接写代码，三节点产出合并后 79 个 test fail。

## 改动

### Spec 模板新增必填段

```yaml
---
task_id: S01-xxx
project: <project>
priority: 1
depends_on: []
modifies: ["path/to/file.py"]
executor: glm
verify: "./run.sh test"
---

## 执行计划（agent 必须先输出这段，确认后再写代码）
1. 读取 SHARED_CONTEXT.md 确认接口契约
2. 列出要改的文件和具体行号
3. 列出风险点（至少 3 条）
4. 确认不会碰 modifies 之外的文件

## 目标
[一句话]

## 契约引用
[从 SHARED_CONTEXT 复制相关接口的请求/响应 JSON 示例]

## 具体改动
[每个文件要改什么]

## 风险清单
- 风险1: xxx → 缓解: xxx
- 风险2: xxx → 缓解: xxx
- 风险3: xxx → 缓解: xxx

## 验收标准
- [ ] verify 命令通过
- [ ] 无 TODO/FIXME/placeholder
- [ ] 不碰 modifies 之外的文件

## 不要做
- [不碰的文件/模块]
```

## 验收标准
- [ ] SHARED_CONTEXT.md 更新了模板
- [ ] 新 spec 按此模板生成时 agent 能遵循
