---
task_id: S03-ai视觉营销平台-图像上传接口
project: ai视觉营销平台
priority: 1
depends_on: ["S01-ai视觉营销平台-bootstrap"]
modifies: ["backend/upload.py", "backend/models.py"]
executor: glm
---
## 目标
开发图像上传API，支持多文件上传并存储到云存储服务

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
