---
task_id: S01-agentforge-bootstrap
project: agentforge
priority: 1
depends_on: []
modifies: ["backend/main.py", "backend/config.py"]
executor: glm
---
## 目标
Bootstrap agentforge project: 面向开发者的低代码多Agent编排平台，支持可视化工作流设计与一键部署

## 约束
- 技术栈: Python FastAPI + React
- 实现核心功能的骨架代码
- 写基础测试

## 验收标准
- [ ] 核心模块有基础实现
- [ ] pytest 能跑通
- [ ] 不留 TODO/FIXME

## 不要做
- 不留 placeholder
- 不做 UI 相关
