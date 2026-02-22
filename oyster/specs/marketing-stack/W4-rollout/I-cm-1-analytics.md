---
task_id: I-cm-1-analytics
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B04-posthog-deploy, B06-plausible-deploy]
modifies: ["oyster/products/clawmarketing/frontend/public/index.html"]
executor: glm
---
## 目标
Install PostHog + Plausible tracking snippets on ClawMarketing landing page and verify events fire correctly

## 约束
- PostHog snippet with project API key from ~/.oyster-keys/
- Plausible snippet with domain clawmarketing.com
- Track events: page_view, signup_click, demo_request
- Test in dev environment first

## 验收标准
- [ ] Both tracking scripts in index.html
- [ ] PostHog dashboard shows page views
- [ ] Plausible dashboard shows traffic
- [ ] Custom events fire on button clicks
- [ ] No console errors from tracking scripts

## 不要做
- No backend changes
- No cookie consent yet
- No custom event properties
