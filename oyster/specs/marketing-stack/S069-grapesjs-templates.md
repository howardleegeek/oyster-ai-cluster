---
task_id: S069-grapesjs-templates
project: marketing-stack
priority: 3
estimated_minutes: 25
depends_on: [S068-grapesjs-integrate]
modifies: ["oyster/products/clawmarketing/frontend/src/templates/grapesjs/"]
executor: glm
---
## 目标
Create GrapesJS template library: product landing page, waitlist/signup page, product launch page with analytics auto-inject

## 约束
- 3 templates: ProductLanding, WaitlistSignup, ProductLaunch
- Each has: hero, features, pricing, CTA sections
- Auto-inject Plausible tracking script
- Auto-inject PostHog initialization
- Templates as JSON (GrapesJS format)
- Responsive mobile/desktop

## 验收标准
- [ ] 3 template JSON files in templates/grapesjs/
- [ ] Each template loads in PageBuilder
- [ ] Analytics scripts auto-injected on export
- [ ] Templates are mobile responsive
- [ ] Documentation for customizing templates
- [ ] Test export includes tracking code

## 不要做
- No actual deployment yet
- No custom domain setup
- No A/B testing variants
