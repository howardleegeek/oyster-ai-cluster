---
task_id: S208-dark-mode
project: clawphones
priority: 2
depends_on: []
modifies: ["app/src/main/res/values/themes.xml", "app/src/main/java/com/clawphones/theme/ThemeManager.kt"]
executor: glm
---
## 目标
实现深色模式，支持系统跟随和手动切换

## 约束
- 在已有 Android 项目内修改
- 写单元测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 单元测试全绿
- [ ] 跟随系统深色模式
- [ ] 手动切换深色/浅色
- [ ] 主题状态持久化

## 不要做
- 不留 TODO/FIXME/placeholder
