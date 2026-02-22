---
task_id: S802-add-vault-navbar
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/Navbar.tsx
  - lumina/App.tsx
executor: glm
---

## 目标
在导航栏添加 Vault 页面入口

## 问题
导航栏缺少 Vault 入口

## 需求
1. 在 Navbar 添加 Vault 按钮
2. 在 App.tsx 添加 Vault 页面路由/视图
3. 使用已有的 VaultPanel.tsx 组件

## 验收
- [ ] 导航栏有 Vault 按钮
- [ ] 点击可进入 Vault 页面
