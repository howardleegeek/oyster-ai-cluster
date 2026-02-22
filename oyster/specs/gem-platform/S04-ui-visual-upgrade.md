---
task_id: S04-ui-visual-upgrade
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/index.html
  - lumina/components/GemCard.tsx
  - lumina/components/Navbar.tsx
  - lumina/App.tsx
executor: glm
---

## 目标
实施 Codex 专家建议的 UI 视觉升级，让界面达到社媒级别精致度。

## 改进内容

### 1. CSS 变量暗色主题升级 (index.html)
替换现有的暗色主题变量：
```css
[data-theme="dark"] {
  --color-bg-primary: #0a0c14;        /* 蓝黑色，更深 */
  --color-bg-card: #12131a;           /* 提升表面 */
  --color-bg-card-hover: #1a1c26;
  --color-bg-elevated: #1e2030;
  --color-border: rgba(255,255,255,0.06);
  --color-border-hover: rgba(255,255,255,0.12);
  --color-text-primary: #f0f2f5;      /* 清晰白，非灰白 */
  --color-text-secondary: #9ca3af;
  --color-text-muted: #6b7280;
}
```

### 2. GemCard 发光效果 (GemCard.tsx)
- 添加稀有度发光 shadow
- 悬浮时 scale + glow
- 稀有度标签添加发光效果

### 3. 按钮升级 (App.tsx, Navbar.tsx)
- 主按钮使用渐变 bg-gradient-to-r from-indigo-500 to-purple-600
- 添加发光 shadow
- 悬浮时上浮效果

### 4. Tailwind 配置增强
添加自定义 boxShadow 和动画：
- shadow-glow-indigo/purple/amber
- shimmer 动画
- glow-pulse 动画

## 验收标准
- [ ] 暗色主题更有层次感，不再灰蒙蒙
- [ ] Legendary 卡片有金色发光效果
- [ ] 按钮有渐变和悬浮动效
- [ ] 整体视觉更精致
