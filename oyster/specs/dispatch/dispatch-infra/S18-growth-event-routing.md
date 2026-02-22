---
task_id: S18-growth-event-routing
project: dispatch-infra
priority: 1
depends_on: ["S13-ai-os-integration"]
modifies:
  - infrastructure/ai_os/config/aios_integration.yaml
executor: glm
---

# Growth Event Routing: 商业杠杆闭环

## 目标
把 BD/Growth 行为也变成事件流 + 产物 + 任务，接入 S13 契约+配置+适配器体系

## 背景
S13 已实现契约+配置+适配器。现在要把商业行为（也纳入事件BD/Growth）流，实现可追踪、可复盘。

## 具体改动

### 更新 aios_integration.yaml

```yaml
version: 1

paths:
  aios_root: "../infrastructure/ai_os"
  events_dir: "events"
  projects_dir: "projects"
  config_dir: "config"

defaults:
  project: "Infra"
  outputs_buckets: ["ops", "infra", "bd", "content", "research", "growth", "misc"]
  timezone: "America/Los_Angeles"

routing:
  rules:
    # === 原有 Infra ===
    - match:
        spec_prefix: "S10"
      route:
        project: "Infra"
        event_type: "guardian.check"
        bucket: "ops"

    - match:
        spec_prefix: "S12"
      route:
        project: "Infra"
        event_type: "audit.code"
        bucket: "infra"

    - match:
        spec_prefix: "S11"
      route:
        project: "Infra"
        event_type: "schedule.predict"
        bucket: "ops"

    # === 新增 BD 事件 ===
    - match:
        event_type: "bd.outreach.sent"
      route:
        project: "Growth"
        event_type: "bd.outreach.sent"
        bucket: "bd"

    - match:
        event_type: "bd.followup.sent"
      route:
        project: "Growth"
        event_type: "bd.followup.sent"
        bucket: "bd"

    - match:
        event_type: "bd.meeting.scheduled"
      route:
        project: "Growth"
        event_type: "bd.meeting.scheduled"
        bucket: "bd"

    - match:
        event_type: "bd.deal.won"
      route:
        project: "Growth"
        event_type: "bd.deal.won"
        bucket: "bd"

    - match:
        event_type: "bd.deal.lost"
      route:
        project: "Growth"
        event_type: "bd.deal.lost"
        bucket: "bd"

    # === 新增 Growth/营销 事件 ===
    - match:
        event_type: "growth.campaign.launched"
      route:
        project: "Growth"
        event_type: "growth.campaign.launched"
        bucket: "growth"

    - match:
        event_type: "growth.campaign.metrics"
      route:
        project: "Growth"
        event_type: "growth.campaign.metrics"
        bucket: "growth"

    - match:
        event_type: "content.published"
      route:
        project: "Growth"
        event_type: "content.published"
        bucket: "content"

    - match:
        event_type: "conversion.*"
      route:
        project: "Growth"
        event_type: "conversion.tracked"
        bucket: "growth"

tasks:
  enable: true
  create_on:
    - condition: "event_type contains 'won'"
      priority: "P0"
    - condition: "event_type contains 'lost'"
      priority: "P1"
    - condition: "event_type contains 'failed'"
      priority: "P1"
  idempotency_key:
    template: "{event_type}:{ref_id}:{date}"

dialogue:
  enable: true
  append_per_batch: true
```

### Growth 事件类型

| 事件 | 描述 | bucket |
|------|------|--------|
| bd.outreach.sent | 发送 outreach | bd |
| bd.followup.sent | 发送 follow-up | bd |
| bd.meeting.scheduled | 预约会议 | bd |
| bd.deal.won | 成交 | bd |
| bd.deal.lost | 丢单 | bd |
| growth.campaign.launched | 营销活动上线 | growth |
| growth.campaign.metrics | 营销数据更新 | growth |
| content.published | 内容发布 | content |
| conversion.won | 转化成功 | growth |
| conversion.lost | 转化失败 | growth |

## 验收标准

- [ ] 配置文件中包含所有 BD/Growth 路由规则
- [ ] 事件能正确路由到对应 project 和 bucket
- [ ] 成交/丢单自动创建 P0/P1 任务

## 不要做

- ❌ 不写死路径
- ❌ 不修改 S13 适配器逻辑
