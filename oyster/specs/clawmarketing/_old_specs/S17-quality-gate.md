---
task_id: S17-quality-gate
project: clawmarketing
priority: 17
depends_on: [S16-analytics-dashboard]
modifies: []
executor: local
---

## 目标
实现 Quality Gate 质量检查

## 具体改动
1. 内容质量检查
2. 敏感词过滤
3. 格式验证

## 验收标准
- [ ] 可以过滤低质量内容
