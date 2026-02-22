---
task_id: S02-cyberpunk-theme
project: shell-vibe-ide
priority: 1
estimated_minutes: 45
depends_on: ["S01-fork-bolt-diy"]
modifies: ["web-ui/app/**/*.css", "web-ui/app/**/*.tsx"]
executor: glm
---

## 目标

把 bolt.diy UI 改成赛博朋克风格：暗黑底 + 霓虹绿/紫点缀。

## 设计规范

### 颜色
- Background: `#0a0a0f` (深黑)
- Surface: `#12121a` (面板背景)
- Primary accent: `#00ff88` (霓虹绿，Solana 风)
- Secondary accent: `#b84dff` (电紫)
- Text: `#c0c0c0` (浅灰)
- Text bright: `#e0e0e0`
- Border: `rgba(0, 255, 136, 0.15)` (微弱绿光)
- Error: `#ff4444`
- Warning: `#ffaa00`
- Success: `#00ff88`

### 字体
- Code: JetBrains Mono (从 Google Fonts 或 CDN 引入)
- UI: Inter

### 效果
- Active 元素: `box-shadow: 0 0 10px rgba(0, 255, 136, 0.3)` (绿光辉)
- Hover: border-color 变 `#00ff88`
- 按钮: 透明底 + 1px neon 边框 + hover 发光
- 输入框: 暗底 + 底部 1px accent 线
- 滚动条: 窄, accent 色

### Logo/品牌
- 标题改为 "Shell" (不是 bolt.diy)
- 副标题: "Web3 Vibe Coding"
- favicon 暂时不改

## 步骤

1. 找到 bolt.diy 的主 CSS 文件 (通常是 globals.css 或 tailwind config)
2. 覆盖 CSS 变量 / tailwind 颜色配置为上述赛博朋克色
3. 引入 JetBrains Mono 字体
4. 更新页面标题和品牌文字为 "Shell"
5. 加入微妙的 neon glow 效果

## 约束

- 只改 CSS/样式和品牌文字
- 不要改功能逻辑
- 不要改组件结构
- 保持响应式布局

## 验收标准

- [ ] 背景色为深黑 (#0a0a0f 或接近)
- [ ] 主色调为霓虹绿 (#00ff88)
- [ ] 代码字体为 JetBrains Mono
- [ ] 标题显示 "Shell"
- [ ] 按钮有 neon 发光 hover 效果
- [ ] `pnpm dev` 正常运行无报错

## 不要做

- 不要改功能代码
- 不要改组件布局结构
- 不要加新依赖 (字体用 CDN)
- 不要碰 desktop/ 和 runner/
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
