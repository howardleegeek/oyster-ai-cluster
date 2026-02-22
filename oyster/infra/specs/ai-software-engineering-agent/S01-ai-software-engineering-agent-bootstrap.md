---
task_id: S01-ai-software-engineering-agent-bootstrap
project: ai-software-engineering-agent
priority: 1
depends_on: []
modifies: ["backend/main.py", "backend/config.py"]
executor: glm
---
## 目标
Bootstrap ai-software-engineering-agent: AI software engineering agent

## 约束
- 实现核心功能骨架
- 写基础测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 核心模块有基础实现
- [ ] pytest 能跑通
