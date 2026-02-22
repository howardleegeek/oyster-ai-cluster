---
task_id: S500-frontend-design-phygitals-style
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/App.tsx
  - lumina/components/
executor: glm
---

## 目标
基于 Phygitals 风格设计 GEM Platform 高端前端 UI

## 参考
- Phygitals: https://www.phygitals.com
- 风格: 高端、简洁、专业、收藏品市场
- 配色: 深色主题 + 霓虹点缀

## 现有 Infra
- lumina-source-code/ - 包含完整 UI 组件
- gem-platform/lumina/ - 当前前端代码

## 任务

### 1. 分析 Phygitals 设计特点
阅读 https://www.phygitals.com 和 https://www.phygitals.com/marketplace
总结:
- 配色方案
- 布局结构
- 字体选择
- 动画效果

### 2. 检查现有组件
分析以下组件:
- ~/Downloads/lumina-source-code/pages/admin/AdminDashboard.tsx
- ~/Downloads/lumina-source-code/components/Marketplace.tsx
- ~/Downloads/lumina-source-code/pages/LeaderboardPage.tsx

### 3. 设计建议
输出一个设计文档到 ~/Downloads/gem-platform/FRONTEND_DESIGN.md，包含:
- 配色方案 (Hex 颜色)
- 字体建议
- 页面结构
- 组件优先级

### 4. 实现核心页面
基于设计文档，更新以下文件:
- lumina/App.tsx - 主页面结构
- lumina/components/Navbar.tsx - 导航栏
- 创建 lumina/pages/HomePage.tsx - 首页
- 创建 lumina/pages/PackStorePage.tsx - Pack 商店
- 创建 lumina/pages/MarketplacePage.tsx - 市场

## 约束
- 使用现有 React + TypeScript + Tailwind CSS
- 不使用新的 npm 包
- 保持响应式设计
- 深色主题优先
