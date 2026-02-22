---
task_id: S06-ai视觉营销平台-前端数据接口
project: ai视觉营销平台
priority: 1
depends_on: ["S01-ai视觉营销平台-bootstrap"]
modifies: ["backend/main.py", "backend/endpoints.py"]
executor: glm
---
## 目标
开发与前端交互的API接口，返回图像分析结果和用户数据

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
