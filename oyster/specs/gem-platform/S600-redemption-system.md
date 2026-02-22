---
task_id: S600-redemption-system
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/redemption.py (NEW FILE)
  - lumina/services/redemptionApi.ts (NEW FILE)
  - lumina/components/RedemptionPanel.tsx (NEW FILE)
executor: glm
---

## 目标
实现 NFT 到实物卡片的兑换系统 (Redemption)

## 约束
- 如果文件已存在，直接更新
- 使用现有后端框架 (FastAPI)
- 不改其他页面 UI

## 功能需求

### 后端
1. **创建兑换请求** - POST /api/redemption
   - 用户选择 NFT
   - 填写收货地址
   - 支付鉴定费 (可选)

2. **兑换流程状态**
   - pending: 待处理
   - verified: 已鉴定
   - shipping: 发货中
   - delivered: 已送达

3. **物流追踪** - GET /api/redemption/{id}/tracking
   - 快递单号
   - 物流进度

4. **管理员**
   - 批准/拒绝兑换
   - 更新物流信息

### 前端 (RedemptionPanel.tsx)
1. 用户选择 NFT 发起兑换
2. 填写收货地址
3. 查看兑换状态和物流

## 约束
- 使用现有后端框架 (FastAPI)
- 不改其他页面 UI

## 验收
- [ ] POST /api/redemption 可创建请求
- [ ] GET /api/redemption 可查看列表
- [ ] 物流追踪可用
- [ ] 前端可发起兑换
