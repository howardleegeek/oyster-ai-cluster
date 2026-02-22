---
task_id: S801-fix-purchase-button
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/PackStoreView.tsx
  - lumina/App.tsx
executor: glm
---

## 目标
修复 Pack Purchase 按钮无法点击的问题

## 问题
点击 Purchase 按钮无反应

## 排查
1. 检查按钮的 onClick 处理函数
2. 检查是否缺少钱包连接检查
3. 检查 API 调用链

## 验收
- [ ] Purchase 按钮可正常点击
- [ ] 点击后能触发购买流程
