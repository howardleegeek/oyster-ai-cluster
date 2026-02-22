---
task_id: S097-analytics
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B04-posthog-deploy, B06-plausible-deploy]
modifies: ["oyster/products/gem-platform/frontend/public/index.html"]
executor: glm
---
## 目标
Install PostHog + Plausible tracking snippets on GEM Platform landing page and verify events fire correctly

## 约束
- PostHog snippet with project API key
- Plausible snippet with domain gem-platform.com
- Track events: page_view, agent_create, workflow_start
- Test in dev environment first

## 验收标准
- [ ] Both tracking scripts in index.html
- [ ] PostHog dashboard shows page views
- [ ] Plausible dashboard shows traffic
- [ ] Custom events fire on agent interactions
- [ ] No console errors

## 不要做
- No backend changes
- No agent execution tracking yet
- No user session recording
