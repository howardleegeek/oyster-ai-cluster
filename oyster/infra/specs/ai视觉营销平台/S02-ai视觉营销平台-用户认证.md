---
task_id: S02-ai视觉营销平台-用户认证
project: ai视觉营销平台
priority: 1
depends_on: ["S01-ai视觉营销平台-bootstrap"]
modifies: ["backend/auth.py", "backend/main.py"]
executor: glm
---
## 目标
实现用户注册、登录和认证功能，包括JWT token生成与验证

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
