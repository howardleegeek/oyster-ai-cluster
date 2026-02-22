---
task_id: S01-004
project: clawphones
priority: 1
depends_on: []
modifies: ["proxy/tests/test_byzantine_network_partition.py"]
executor: glm
---

## 目标
拜占庭容错测试：网络分区与恢复

## 约束
- 模拟网络中断/延迟场景
- 验证请求重试与超时处理

## 具体改动
- 创建 proxy/tests/test_byzantine_network_partition.py
  - 模拟 LLM 提供商网络超时
  - 模拟中间网络延迟
  - 验证客户端超时处理
  - 验证重试机制正确工作

## 验收标准
- [ ] 网络超时测试通过
- [ ] 重试机制验证通过
