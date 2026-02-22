---
task_id: I-cp-1-analytics
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B04-posthog-deploy, B06-plausible-deploy]
modifies: ["oyster/products/clawphones/web/public/index.html"]
executor: glm
---
## 目标
Install PostHog + Plausible tracking snippets on ClawPhones landing page and verify events fire correctly

## 约束
- PostHog snippet with project API key
- Plausible snippet with domain clawphones.com
- Track events: page_view, order_click, customization_start
- Test in dev environment first

## 验收标准
- [ ] Both tracking scripts in index.html
- [ ] PostHog dashboard shows page views
- [ ] Plausible dashboard shows traffic
- [ ] Custom events fire on interactions
- [ ] No console errors

## 不要做
- No backend changes
- No cookie consent yet
- No e-commerce tracking
