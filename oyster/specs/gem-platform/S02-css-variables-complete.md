---
task_id: S02-css-variables-complete
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/ActionModals.tsx
  - lumina/components/WalletPanel.tsx
  - lumina/components/OrderPanel.tsx
  - lumina/components/AdminPanel.tsx
  - lumina/components/GemCard.tsx
  - lumina/components/DropDetailsView.tsx
executor: glm
---

## 目标
完成 GEM Platform 前端 CSS 变量重构，替换所有剩余的 hardcoded 颜色。

## 替换规则
```
bg-[#0a0a0a] → bg-surface-card
bg-[#121212] → bg-surface-elevated
bg-[#1a1a1a] → bg-surface-cardHover
bg-[#050505] → bg-surface-primary
bg-[#0f0f0f] → bg-surface-card
text-white → text-content-primary
text-zinc-400 → text-content-muted
text-zinc-500 → text-content-secondary
text-zinc-300 → text-content-secondary
text-zinc-600 → text-content-muted
border-zinc-800 → border-border
border-zinc-700 → border-border-hover
border-zinc-600 → border-border-hover
```

## 具体文件

### 1. ActionModals.tsx
替换所有 text-zinc-*, bg-zinc-*, border-zinc-* 为 CSS 变量类

### 2. WalletPanel.tsx
替换所有 hardcode 颜色

### 3. OrderPanel.tsx
替换所有 hardcode 颜色

### 4. AdminPanel.tsx  
替换所有 hardcode 颜色

### 5. GemCard.tsx
保留稀有度颜色(blue/purple/yellow等)，替换背景/边框颜色

### 6. DropDetailsView.tsx (Trust Center)
替换所有 hardcode 颜色

## 验收标准
- [ ] grep 搜索 "text-zinc-|bg-zinc-|border-zinc-" 结果 < 50
- [ ] 所有页面主题切换正常
- [ ] 无 console 错误
