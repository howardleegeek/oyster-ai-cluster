---
task_id: S01-008
project: clawphones
priority: 1
depends_on: []
modifies: ["ios/ClawPhonesTests"]
executor: glm
---

## 目标
iOS 测试：XCUITest 基础功能测试

## 约束
- 使用 XCUITest
- 在 iOS Simulator 运行

## 具体改动
- 创建 ios/ClawPhonesTests/
  - 登录/注册流程测试
  - 会话列表测试
  - 发送消息测试

## 验收标准
- [ ] XCUITest 编译通过
- [ ] 基础功能测试通过
