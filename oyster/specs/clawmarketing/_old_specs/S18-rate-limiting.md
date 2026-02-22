---
task_id: S18-rate-limiting
project: clawmarketing
priority: 18
depends_on: [S17-quality-gate]
modifies: []
executor: local
---

## 目标
实现 Rate Limiting 限流

## 具体改动
1. 每日发推上限
2. 互动上限
3. 随机延迟

## 验收标准
- [ ] 不超过平台限制
