---
task_id: S077-analytics
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B04-posthog-deploy, B06-plausible-deploy]
modifies: ["oyster/products/clawglasses/web/public/index.html"]
executor: glm
---
## 目标
Install PostHog + Plausible tracking snippets on ClawGlasses landing page and verify events fire correctly

## 约束
- PostHog snippet with project API key
- Plausible snippet with domain clawglasses.com
- Track events: page_view, customize_click, order_start
- Test in dev environment first

## 验收标准
- [ ] Both tracking scripts in index.html
- [ ] PostHog dashboard shows page views
- [ ] Plausible dashboard shows traffic
- [ ] Custom events fire on interactions
- [ ] No console errors

## 不要做
- No backend changes
- No prescription tracking
- No virtual try-on analytics yet
