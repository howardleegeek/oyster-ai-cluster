---
task_id: I-or-1-analytics
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B04-posthog-deploy, B06-plausible-deploy]
modifies: ["oyster/products/oyster-republic/web/public/index.html"]
executor: glm
---
## 目标
Install PostHog + Plausible tracking snippets on OysterRepublic landing page and verify events fire correctly

## 约束
- PostHog snippet with project API key
- Plausible snippet with domain oysterrepublic.com
- Track events: page_view, signup_click, explore_click
- Test in dev environment first

## 验收标准
- [ ] Both tracking scripts in index.html
- [ ] PostHog dashboard shows page views
- [ ] Plausible dashboard shows traffic
- [ ] Custom events fire on interactions
- [ ] No console errors

## 不要做
- No backend changes
- No Web3 wallet tracking yet
- No on-chain analytics
