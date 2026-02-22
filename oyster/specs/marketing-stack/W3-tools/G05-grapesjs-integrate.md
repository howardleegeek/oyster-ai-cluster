---
task_id: G05-grapesjs-integrate
project: marketing-stack
priority: 3
estimated_minutes: 30
depends_on: []
modifies: ["oyster/products/clawmarketing/frontend/src/components/PageBuilder.tsx", "oyster/products/clawmarketing/frontend/package.json"]
executor: glm
---
## 目标
Integrate GrapesJS landing page builder into ClawMarketing frontend as React component

## 约束
- npm install grapesjs grapesjs-react
- Create PageBuilder.tsx wrapper component
- Props: initialContent, onSave, templates
- Store/load designs via localStorage initially
- Basic blocks: hero, features, pricing, CTA, testimonials
- Export HTML + CSS

## 验收标准
- [ ] PageBuilder.tsx renders GrapesJS editor
- [ ] Can drag-drop blocks to build page
- [ ] Save/load functionality works
- [ ] Export HTML includes styles
- [ ] Component integrates into ClawMarketing dashboard
- [ ] npm run build succeeds

## 不要做
- No backend API yet
- No template library (next spec)
- No asset upload (use URLs)
