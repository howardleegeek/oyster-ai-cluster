---
task_id: S01-009
project: clawphones
priority: 1
depends_on: ["S01-008"]
modifies: ["ios/ClawPhonesTests"]
executor: glm
---

## 目标
iOS 测试：XCUITest 网络与错误处理

## 约束
- XCUITest
- 覆盖网络错误场景

## 具体改动
- 完善 ios/ClawPhonesTests/
  - 网络超时测试
  - 离线提示测试
  - 错误弹窗测试
  - 设置页面测试

## 验收标准
- [ ] 网络错误测试通过
- [ ] 设置功能测试通过
