---
task_id: S01-gem-frontend-review
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/MarketplaceUpdates.tsx
  - lumina/components/RedemptionPanel.tsx
  - lumina/components/MyOpenings.tsx
  - lumina/components/GemCard.tsx
  - lumina/components/ReferralPanel.tsx
  - lumina/components/Leaderboard.tsx
  - lumina/components/DashboardUpdates.tsx
  - lumina/components/DropDetailsView.tsx
  - lumina/components/ActionModals.tsx
  - lumina/components/WalletPanel.tsx
  - lumina/components/OrderPanel.tsx
executor: glm
---

## 目标
对 GEM Platform 前端进行全面视觉走查并重构代码，统一使用 CSS 变量系统。

## 问题诊断
当前有 **407 处** hardcoded 的 zinc 颜色值需要替换：
- `text-zinc-xxx` → `text-content-*`
- `bg-zinc-xxx` → `bg-surface-*`  
- `border-zinc-xxx` → `border-*`
- `bg-[#0a0a0a]` → `bg-surface-card`
- `bg-[#121212]` → `bg-surface-elevated`
- `text-white` → `text-content-primary`

## 约束
- 使用 Codex 专家模式重构代码
- 只改 UI 样式，不改功能逻辑
- 使用已有的 CSS 变量（--color-bg-primary, --color-bg-card 等）
- 保持响应式设计

## 具体改动

### 替换规则
```
bg-[#0a0a0a] → bg-surface-card
bg-[#121212] → bg-surface-elevated
bg-[#1a1a1a] → bg-surface-cardHover
bg-[#050505] → bg-surface-primary
text-white → text-content-primary
text-zinc-400 → text-content-muted
text-zinc-500 → text-content-secondary
border-zinc-800 → border-border
border-zinc-700 → border-border-hover
```

### 需要重构的文件（按优先级）

**P0 - 关键页面:**
1. `MarketplaceUpdates.tsx` - Marketplace 页面
2. `RedemptionPanel.tsx` - Redemption 页面  
3. `MyOpenings.tsx` - My Openings 页面
4. `GemCard.tsx` - 宝石卡片组件

**P1 - 主要页面:**
5. `ReferralPanel.tsx` - 推荐页面
6. `Leaderboard.tsx` - 排行榜页面
7. `DashboardUpdates.tsx` - Dashboard 页面
8. `DropDetailsView.tsx` - Trust Center

**P2 - 其他组件:**
9. `ActionModals.tsx` - 弹窗组件
10. `WalletPanel.tsx` - 钱包面板
11. `OrderPanel.tsx` - 订单面板
12. `App.tsx` - 主应用（清理剩余 hardcode）

## 验收标准
- [ ] 所有页面在暗色主题下视觉统一
- [ ] 所有页面在亮色主题下视觉统一  
- [ ] 主题切换无样式闪烁
- [ ] 无 console 错误
- [ ] grep 搜索 "text-zinc-|bg-zinc-|border-zinc-" 结果为 0（或极少）

## 验证命令
```bash
# 部署后检查
cd lumina && npx vercel --prod --yes

# 验证无 hardcode 颜色
grep -r "text-zinc-\|bg-zinc-\|border-zinc-\|bg-\[#0\|bg-\[#1" components/ --include="*.tsx" | wc -l
```
