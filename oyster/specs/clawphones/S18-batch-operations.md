---
task_id: S18-batch-operations
project: clawphones
priority: 1
depends_on: []
modifies:
  - server.js
executor: glm
---

## 目标
实现批量 ADB 命令执行功能

## 约束
- 不改移动端代码
- 使用现有 ADB 基础设施

## 具体改动
1. 实现批量执行 ADB 命令
2. 添加文件批量传输
3. 实现断点续传
4. 写集成测试

## 验收标准
- [ ] 批量命令执行成功
- [ ] 文件传输支持断点
- [ ] 测试通过

## 不要改
- server.js 已有功能
