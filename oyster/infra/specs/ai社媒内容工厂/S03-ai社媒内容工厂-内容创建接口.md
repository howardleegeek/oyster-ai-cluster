---
task_id: S03-ai社媒内容工厂-内容创建接口
project: ai社媒内容工厂
priority: 1
depends_on: ["S01-ai社媒内容工厂-bootstrap"]
modifies: ["backend/content.py", "backend/main.py", "tests/test_content.py"]
executor: glm
---
## 目标
开发API接口，允许用户创建、编辑和删除社媒内容，包括文本、图片和视频。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
