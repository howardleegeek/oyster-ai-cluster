---
task_id: S05-ai视觉营销平台-AI图像分析
project: ai视觉营销平台
priority: 2
depends_on: ["S01-ai视觉营销平台-bootstrap"]
modifies: ["backend/analysis.py", "backend/models.py"]
executor: glm
---
## 目标
集成AI模型进行图像内容分析，提取关键特征和标签

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
