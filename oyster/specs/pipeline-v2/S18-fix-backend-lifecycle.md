---
task_id: S18-fix-backend-lifecycle
project: pipeline-v2
priority: 1
depends_on: []
modifies: ["dispatch/pipeline/layers/L3_build.py", "dispatch/pipeline/layers/L4_test.py"]
executor: glm
---

## 目标
修复 pipeline 生命周期：L3 构建后保持后端运行，L4 测试前确保后端启动

## 约束
- 不修改其他层
- 所有函数用 kwargs
- 保持向后兼容

## 具体改动

### 问题分析
当前 L3 build 测试完后杀掉后端进程，导致 L4 测试时后端已停止，所有 API 返回 000。

### 修复方案

1. **L3_build.py**: 添加 `--keep-running` 选项，测试后不杀后端进程
2. **L4_test.py**: 测试前先检查后端是否运行，没有则启动

### 预期结果
- L3 完成后后端保持运行
- L4 能正确测试 API（不再全是 000）
- Pipeline 能完整跑完 L1→L6

## 验收标准
- [ ] L3 构建测试后不杀后端
- [ ] L4 测试前确保后端运行
- [ ] 完整 pipeline 能跑通
