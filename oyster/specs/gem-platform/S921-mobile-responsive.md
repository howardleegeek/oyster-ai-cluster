---
task_id: S921-mobile-responsive
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/App.tsx
  - lumina/components/*.tsx
---

## 目标
Fix mobile responsiveness issues across all pages

## 约束
- 不改变桌面版布局
- 不添加新依赖

## 具体改动
1. Add responsive classes to Navbar (hamburger menu for mobile)
2. Fix grid layouts on Marketplace, Vault pages
3. Ensure touch-friendly buttons on mobile (min 44px tap targets)

## 验收标准
- [ ] Mobile view works without horizontal scroll
- [ ] All buttons are tappable (44px+)
