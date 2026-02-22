---
task_id: S45-landing-page
project: shell-vibe-ide
priority: 2
estimated_minutes: 45
depends_on: ["S02-cyberpunk-theme"]
modifies: ["web-ui/app/pages/landing.tsx", "web-ui/app/components/landing/hero-section.tsx", "web-ui/app/components/landing/feature-showcase.tsx", "web-ui/app/components/landing/comparison-table.tsx", "web-ui/app/components/landing/pricing-section.tsx"]
executor: glm
---

## 目标

创建赛博朋克风格的产品 Landing Page，用于推广和获客。

## 开源方案

- **Astro**: github.com/withastro/astro (49k stars, MIT) — 静态站点生成
- 或直接在 Next.js (web-ui) 中创建 landing 页面

## 内容结构

1. **Hero Section**:
   - "Shell — Cursor for Web3"
   - "Describe it. Deploy it."
   - 赛博朋克动画背景 (粒子/网格/代码雨)
   - [Try Web App] [Download Desktop] 两个 CTA
   - 录屏 GIF/视频 (30秒 demo)

2. **Feature Showcase** (6 个):
   - AI Vibe Coding: 自然语言 → 合约
   - Dual Chain: SVM + EVM
   - Auto-Repair: AI 自动修复闭环
   - Security First: 内置审计
   - One-Click Deploy: 测试网/主网
   - Native Desktop: 不是浏览器 toy

3. **How It Works** (3 步):
   - Describe → Generate → Deploy
   - 带截图/动画

4. **Comparison Table**:
   - Shell vs Remix vs Cursor+Foundry vs ChainGPT

5. **Template Gallery Preview**:
   - 展示几个热门模板

6. **Pricing**:
   - Free / Pro / Team

7. **Footer**:
   - GitHub | Discord | Twitter
   - Built by Oyster Labs

## 设计要求

- 赛博朋克: 深黑底 + 霓虹绿/紫
- 粒子动画背景 (用 tsparticles 或 CSS)
- 流畅的滚动动画 (intersection observer)
- 移动端响应式
- 性能: Lighthouse 90+

## 验收标准

- [ ] Landing page 完整显示所有 section
- [ ] 赛博朋克动画背景
- [ ] CTA 按钮链接到 Web App 和下载页
- [ ] 移动端响应式
- [ ] 自动部署到 Vercel

## 不要做

- 不要用模板生成器 (手写)
- 不要加注册表单 (直接跳转 App)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
