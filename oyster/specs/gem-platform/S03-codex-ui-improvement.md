---
task_id: S03-codex-ui-improvement
project: gem-platform
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
咨询 Codex 专家，获取 GEM Platform UI/UX 改进建议。

## 背景
GEM Platform 是一个 RWA（实物资产）gacha/盲盒平台，类似 Phygitals。当前问题：
1. UI 视觉效果不够精致，达不到社媒级别
2. 暗色主题已实现但缺乏视觉层次
3. 组件样式不统一
4. 焦点和动缺乏视觉效

## 部署地址
- Frontend: https://lumina-six-phi.vercel.app
- 后端: 使用 ngrok tunnel (不稳定)

## 当前页面
- / - 首页 + Pack 购买
- /marketplace - 市场
- /vault - 实物保险库
- /redemption - 赎回
- /trust - 信任中心

## 请 Codex 专家提供

### 1. 视觉层次改进
- 如何创造更好的视觉焦点
- 颜色对比度和层次
- 间距和网格系统

### 2. 组件设计
- 卡片设计最佳实践
- 按钮和交互元素样式
- 稀有度标签设计（Common/Rare/Epic/Legendary）

### 3. 动效和交互
- 有意义的微动效
- 加载状态设计
- 过渡效果

### 4. 暗色主题优化
- 暗色主题的视觉层次
- 如何避免"灰蒙蒙"的感觉
- 发光效果和对比度

### 5. 具体代码建议
- Tailwind 配置优化
- CSS 变量改进
- 组件重构建议

## 输出要求
1. 详细的 UI/UX 改进文档
2. 具体的设计系统建议
3. 可执行的代码改进方案
