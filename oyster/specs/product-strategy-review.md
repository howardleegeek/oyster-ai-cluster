---
task_id: STRATEGY-001
project: product-strategy
priority: 1
depends_on: []
executor: glm
---

## 目标
Review MiniMax 生成的 5 产品战略规划，输出可执行的 Sprint 计划和 spec 拆分

## 背景
MiniMax 已生成 5 产品 3 个月迭代计划：
1. ClawMarketing - 自动化获客营销引擎
2. ClawPhones - 云控设备管理中台  
3. GEM Platform - 盲盒/Gem 交易平台
4. Oysterworld - 地图可视化世界
5. ClawVision - AI Vision 静态网站

## 约束
- 只输出计划不写代码
- 每个产品需要拆成具体的 atomic spec
- 优先拆商业化核心产品 (ClawMarketing, GEM Platform)
- 结合现有 specs 避免重复

## 具体改动
1. Review MiniMax 战略输出
2. 根据现有项目状态调整优先级
3. 拆成 Q1 可执行的 atomic specs
4. 输出到 specs/<product>/sprint-*.md

## 验收标准
- [ ] 每个产品有 2 个 Sprint 的 atomic specs
- [ ] specs 包含 depends_on 依赖关系
- [ ] 输出到对应产品目录

## 不要做
- 不写代码实现
- 不改动现有 spec 文件
