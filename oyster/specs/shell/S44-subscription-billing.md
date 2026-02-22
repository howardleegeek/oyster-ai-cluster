---
task_id: S44-subscription-billing
project: shell-vibe-ide
priority: 3
estimated_minutes: 45
depends_on: ["S24-user-auth"]
modifies: ["web-ui/app/components/billing/subscription-page.tsx", "web-ui/app/components/billing/pricing-table.tsx", "web-ui/app/lib/billing/stripe-client.ts", "web-ui/app/lib/billing/feature-gates.ts", "web-ui/app/hooks/useSubscription.ts"]
executor: glm
---

## 目标

实现订阅付费系统：免费 tier + Pro 付费。

## 开源方案

- **Stripe**: 行业标准支付 (not open source but SDK is)
- **Lemon Squeezy**: 开发者友好的支付平台
- **Crypto 支付**: 用 USDC/SOL 直接支付 (Web3 原生)

## 定价模型

### Free Tier
- 无限本地构建/测试
- 3 个项目
- 社区模板
- 基础 AI (有限 tokens/月)
- 测试网部署

### Pro ($19/月 或 0.1 SOL/月)
- 无限项目
- 无限 AI tokens
- 主网部署
- 高级安全审计
- 团队协作
- 优先 AI 模型
- 社区模板发布
- EVM Bench 高级功能

### Team ($49/月)
- 所有 Pro 功能
- 5 个成员
- 管理员面板
- 审计日志
- 共享项目/模板

## 步骤

1. Stripe 集成:
   - `pnpm add @stripe/stripe-js`
   - 创建 Subscription checkout
   - Webhook 处理
2. Crypto 支付 (可选):
   - USDC on Solana 支付
   - 用钱包直接付费
   - 使用 Solana Pay 标准
3. 功能门控:
   - `useSubscription()` hook
   - Free tier 限制检查
   - 超限提示 "Upgrade to Pro"
4. 计费页面:
   - 当前计划
   - 使用量统计
   - 升级/降级
   - 发票历史

## 验收标准

- [ ] Stripe checkout 工作
- [ ] 免费 tier 限制生效
- [ ] Pro 功能解锁
- [ ] 计费页面
- [ ] Crypto 支付 (可选)

## 不要做

- 不要自己实现支付 (用 Stripe)
- 不要存储支付信息
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
