---
task_id: S901-buyback-component
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/BuybackPanel.tsx
  - lumina/services/buybackApi.ts
executor: glm
---

## 目标
实现回购报价组件

## 功能
1. 展示 FMV 参考价
2. 展示回购价 (85%-90%)
3. 倒计时窗口显示
4. 一键回购按钮

## 验收
- [ ] 回购组件显示价格
- [ ] 倒计时可用
