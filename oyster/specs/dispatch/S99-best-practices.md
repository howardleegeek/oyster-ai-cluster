---
task_id: S99-best-practices-spec
project: dispatch
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
添加 Best Practices 到 dispatch 系统

## 具体改动

### 1. 更新 Spec 模板 - 加「执行计划」段
```yaml
# 新增字段
execution_plan:
  - milestone: "第一步"
    depends_on: []
    files: ["file1.py"]
  - milestone: "第二步"
    depends_on: ["S01-xxx"]
    files: ["file2.py"]

### 2. 强制测试
task-wrapper.sh 结尾:
- 检查 TODO/FIXME
- 运行测试命令
- 测试失败 = status = failed

### 3. 冲突检测
dispatch.py:
- 检查两个 running 任务的 modifies 是否有交集
- 有交集 → 串行不并行

### 4. Collect 验证
collect 后自动:
- npm run build
- npm run test
- 失败 → 告警

## 验收标准
- [ ] Spec 模板包含执行计划
- [ ] task-wrapper 检测 TODO
- [ ] dispatch 检测冲突
- [ ] collect 后验证 build
