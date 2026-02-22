---
task_id: C06-multi-model
project: clawcontrol
priority: 1
depends_on: []
modifies:
  - pipeline/clawcontrol/services/endgame.py
---

## 目标
支持多模型路由，根据任务类型自动选择最佳模型

## 约束
- 支持 GLM/Claude/GPT/Codex
- 根据任务类型选择
- 可配置

## 具体改动
1. 添加模型路由逻辑
2. 根据 mode 选择模型
3. 支持自定义模型优先级

## 验收标准
- [ ] fix 任务用 Claude
- [ ] refactor 任务用 GPT
- [ ] research 任务用 GLM-Flash
