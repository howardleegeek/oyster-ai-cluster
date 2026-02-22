---
task_id: C07-cost-tracker
project: clawcontrol
priority: 1
depends_on: []
modifies:
  - pipeline/clawcontrol/services/cost.py
---

## 目标
添加成本追踪功能

## 具体改动
1. 追踪每个任务/attempt的token消耗
2. 成本统计面板
3. ROI计算
