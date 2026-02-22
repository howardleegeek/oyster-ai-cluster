---
task_id: S107-analytics
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B04-posthog-deploy, B06-plausible-deploy]
modifies: ["oyster/products/getpuffy/web/public/index.html"]
executor: glm
---
## 目标
Install PostHog + Plausible tracking snippets on getPuffy landing page and verify events fire correctly

## 约束
- PostHog snippet with project API key
- Plausible snippet with domain getpuffy.com
- Track events: page_view, product_view, add_to_cart
- Test in dev environment first

## 验收标准
- [ ] Both tracking scripts in index.html
- [ ] PostHog dashboard shows page views
- [ ] Plausible dashboard shows traffic
- [ ] E-commerce events fire correctly
- [ ] No console errors

## 不要做
- No backend changes
- No checkout tracking yet
- No revenue tracking
