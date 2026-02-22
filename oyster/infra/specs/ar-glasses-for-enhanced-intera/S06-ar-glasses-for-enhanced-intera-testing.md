---
task_id: S06-ar-glasses-for-enhanced-intera-testing
project: ar-glasses-for-enhanced-intera
priority: 3
depends_on: ["S01-ar-glasses-for-enhanced-intera-bootstrap"]
modifies: ["tests/test_interaction.py", "tests/test_auth.py"]
executor: glm
---
## 目标
编写单元测试以验证AR眼镜交互功能的正确性

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
