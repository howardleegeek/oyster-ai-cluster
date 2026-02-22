---
task_id: F11-cm-seo-widget
project: marketing-stack
priority: 2
estimated_minutes: 20
depends_on: [B12]
modifies: ["clawmarketing/frontend/src/components/SEOWidget.tsx"]
executor: glm
---
## 目标
Add SEO rank widget to ClawMarketing frontend - show keyword rankings from SerpBear

## 约束
- Create SEOWidget.tsx component
- Fetch rankings from SerpBear API
- Display top keywords with rank and change
- Color-code: green (up), red (down), gray (unchanged)
- Show top 10 keywords by importance

## 验收标准
- [ ] SEOWidget.tsx component created
- [ ] Fetches rankings from SerpBear API
- [ ] Displays top 10 keywords with ranks
- [ ] Color-coded rank changes
- [ ] Shows rank change delta
- [ ] Component renders in dashboard

## 不要做
- Don't build keyword research features
- Don't add SERP feature tracking
- Don't implement competitor rank comparison
