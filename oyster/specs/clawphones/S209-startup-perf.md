---
task_id: S209-startup-perf
project: clawphones
priority: 2
depends_on: []
modifies: ["app/src/main/java/com/clawphones/app/MainApplication.kt"]
executor: glm
---
## 目标
优化启动性能，冷启动 < 2 秒

## 约束
- 在已有 Android 项目内修改
- 写性能测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 冷启动时间 < 2s
- [ ] 延迟加载非关键模块
- [ ] 移除不必要初始化
- [ ] 启动画面优化

## 不要做
- 不留 TODO/FIXME/placeholder
