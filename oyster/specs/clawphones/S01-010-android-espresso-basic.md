---
task_id: S01-010
project: clawphones
priority: 1
depends_on: []
modifies: ["android/clawphones-android/app/src/androidTest"]
executor: glm
---

## 目标
Android 测试：Espresso 基础功能测试

## 约束
- 使用 Espresso
- 在 Android Emulator 运行

## 具体改动
- 创建 android/clawphones-android/app/src/androidTest/
  - 登录/注册流程测试
  - 会话列表测试
  - 发送消息测试

## 验收标准
- [ ] Espresso 测试编译通过
- [ ] 基础功能测试通过
