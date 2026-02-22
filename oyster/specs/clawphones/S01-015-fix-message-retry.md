---
task_id: S01-015
project: clawphones
priority: 1
depends_on: ["S01-013"]
modifies: ["proxy/server.py", "ios/ClawPhones"]
executor: glm
---

## 目标
修复已知问题：消息失败重试机制

## 约束
- 后端 + iOS 客户端
- 离线消息队列

## 具体改动
- 修改 proxy/server.py
  - 添加消息重试记录
  - 修改 ios/ClawPhones/
  - 添加自动重试逻辑

## 验收标准
- [ ] 失败消息自动重试测试通过
- [ ] 客户端正确处理重试响应
