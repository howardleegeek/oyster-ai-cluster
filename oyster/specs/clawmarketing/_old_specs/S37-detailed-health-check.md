---
task_id: S37-detailed-health-check
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
增强Health Check端点，返回详细系统状态

##具体改动
1. 增强 /health 端点
2. 检查数据库连接
3. 返回系统信息 (Python版本, 内存, etc)
4. 返回各组件状态

##验收标准
- [ ] /health 返回详细状态
- [ ] 包含数据库状态
- [ ] 包含系统信息
