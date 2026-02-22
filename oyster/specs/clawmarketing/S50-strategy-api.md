---
task_id: S50-strategy-api
project: clawmarketing
priority: 2
depends_on: [S49-campaign-crud]
modifies:
  - backend/routers/strategy.py
  - backend/main.py
  - frontend/src/pages/Home.tsx
executor: glm
---

## 目标
创建 Strategy API - 自然语言解析营销策略

## 背景
v2 PRD: LLM对话自动解析Brand/Campaign/Persona设置

## API端点
- POST /api/v2/strategy/parse - 解析自然语言为结构化策略
- POST /api/v2/strategy/apply - 应用策略创建Brand/Campaign/Persona

## 具体改动

### backend/routers/strategy.py
- POST /api/v2/strategy/parse
  - 输入: natural_language (str)
  - 输出: parsed_strategy (object with brand, campaign, persona)
  - 使用 LLM 解析用户意图

- POST /api/v2/strategy/apply
  - 输入: parsed_strategy (from parse)
  - 输出: created brand_id, campaign_id, persona_ids
  - 调用现有的 Brand/Campaign/Persona 创建逻辑

### frontend/src/pages/Home.tsx
- 更新 LLM 对话逻辑
- 当用户描述营销目标时，自动调用 strategy/parse
- 用户确认后调用 strategy/apply

## 验收标准
- [ ] /api/v2/strategy/parse 返回结构化策略
- [ ] /api/v2/strategy/apply 创建Brand/Campaign/Persona
- [ ] Home 页面 LLM 对话可触发自动创建
