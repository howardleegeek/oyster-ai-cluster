---
task_id: S05-ai社媒内容工厂-内容推荐
project: ai社媒内容工厂
priority: 2
depends_on: ["S01-ai社媒内容工厂-bootstrap"]
modifies: ["backend/recommend.py", "backend/main.py", "tests/test_recommend.py"]
executor: glm
---
## 目标
实现基于用户兴趣和互动历史的内容推荐算法。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
