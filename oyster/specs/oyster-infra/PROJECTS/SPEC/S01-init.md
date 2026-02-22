---
task_id: S01-init
project: oyster-infra
priority: 1
depends_on: []
modifies: ["README.md"]
executor: glm
---

## 目标
初始化 oyster-infra 项目

## 约束
- 不改动生产代码

## 具体改动
- 创建 README.md

##验收标准
- [ ] README 存在
