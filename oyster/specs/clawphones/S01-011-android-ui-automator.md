---
task_id: S01-011
project: clawphones
priority: 1
depends_on: ["S01-010"]
modifies: ["android/clawphones-android/app/src/androidTest"]
executor: glm
---

## 目标
Android 测试：UI Automator 网络与设置

## 约束
- 使用 UI Automator
- 覆盖系统设置交互

## 具体改动
- 完善 android/clawphones-android/app/src/androidTest/
  - 网络超时测试
  - 离线提示测试
  - 设置页面测试
  - Dashboard 交互测试

## 验收标准
- [ ] 网络错误测试通过
- [ ] 设置功能测试通过
