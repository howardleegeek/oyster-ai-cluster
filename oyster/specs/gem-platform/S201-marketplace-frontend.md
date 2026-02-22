---
task_id: S201-marketplace-frontend
project: gem-platform
priority: 1
depends_on: ["S200-marketplace-backend"]
modifies:
  - lumina/src/pages/Marketplace.tsx
  - lumina/src/components/MarketOrder.tsx
executor: glm
---

## 目标
实现市场交易前端页面

## 约束
- 使用现有组件库
- 不改后端 API 合约
- 应用 frontend-design skill 规范

## 具体改动
1. 创建 Marketplace 页面
2. 实现挂单表单组件
3. 实现订单簿展示
4. 实现撤单功能
5. 写 Vitest 测试

## 验收标准
- [ ] 页面加载无 JS 错误
- [ ] 挂单表单提交成功
- [ ] 订单簿数据正确展示
- [ ] vitest run 通过

## 不要做
- 不改 API 合约
- 不加新依赖
