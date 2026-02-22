---
task_id: S43-usage-analytics
project: shell-vibe-ide
priority: 3
estimated_minutes: 35
depends_on: ["S24-user-auth"]
modifies: ["web-ui/app/lib/analytics/posthog.ts", "web-ui/app/lib/analytics/events.ts", "web-ui/app/components/settings/analytics-settings.tsx"]
executor: glm
---

## 目标

添加产品使用分析，了解用户行为和产品健康度。

## 开源方案

- **PostHog**: github.com/PostHog/posthog (25k stars, MIT) — 产品分析平台，可自托管
- **Umami**: github.com/umami-software/umami (24k stars, MIT) — 隐私友好的网站分析
- **Plausible**: github.com/plausible/analytics (22k stars, AGPL-3.0)

## 步骤

1. 集成 PostHog (MIT, 可自托管):
   - 用 PostHog Cloud (免费 tier) 或自托管
   - `pnpm add posthog-js`
2. 追踪事件:
   - 项目创建 (chain, template)
   - Build/Test/Audit/Deploy (chain, success/fail)
   - Auto-repair 使用 (success rate)
   - 模板使用 (which templates are popular)
   - 功能使用 (哪些面板最常用)
3. 仪表板:
   - DAU/WAU/MAU
   - 功能使用率
   - 部署成功率
   - 最受欢迎的链/模板
4. 隐私:
   - 不追踪代码内容
   - 不追踪钱包地址
   - 用户可以 opt-out
   - GDPR 合规

## 验收标准

- [ ] PostHog 集成
- [ ] 关键事件追踪
- [ ] 用户可以 opt-out
- [ ] 仪表板显示基本指标

## 不要做

- 不要追踪敏感数据 (代码、钱包)
- 不要用 Google Analytics (隐私)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
