---
task_id: G7-06-OI-ALL
project: oyster-infra
priority: 1
depends_on: []
modifies: ["src/event_bus/bus.py", "src/event_bus/rules.py"]
executor: glm
---
## 目标
建设跨项目统一事件总线，支撑所有集成

## 技术方案
1. 新增 `UnifiedEventBus` 类，基于 Redis Pub/Sub
2. 定义标准事件 Schema (event_type, source, payload, timestamp)
3. 支持事件路由规则：项目 -> 事件类型 -> 订阅者
4. 实现事件持久化 + 重试机制

## 约束
- 命名空间隔离项目事件
- 基础测试覆盖发布/订阅
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 事件延迟 < 100ms
- [ ] 支持多订阅者
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
