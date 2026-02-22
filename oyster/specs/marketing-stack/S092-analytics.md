---
task_id: S092-analytics
project: marketing-stack
priority: 4
estimated_minutes: 15
depends_on: [B04-posthog-deploy, B06-plausible-deploy]
modifies: ["oyster/products/clawvision/web/public/index.html"]
executor: glm
---
## 目标
Install PostHog + Plausible tracking snippets on ClawVision landing page and verify events fire correctly

## 约束
- PostHog snippet with project API key
- Plausible snippet with domain clawvision.com
- Track events: page_view, upload_click, analysis_start
- Test in dev environment first

## 验收标准
- [ ] Both tracking scripts in index.html
- [ ] PostHog dashboard shows page views
- [ ] Plausible dashboard shows traffic
- [ ] Custom events fire on image interactions
- [ ] No console errors

## 不要做
- No backend changes
- No image upload tracking yet
- No API usage tracking
