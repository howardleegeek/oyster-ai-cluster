---
task_id: S350-admin-dashboard-complete
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/AdminPanel.tsx
  - lumina/services/adminApi.ts
  - backend/app/api/admin.py
executor: glm
---

## 目标
实现完整的 Admin Dashboard 后台，用于运营团队日常操作

## 约束
- 使用现有前端框架和 API 风格
- 后端 API 返回完整数据
- 不改其他页面 UI

## 具体改动

### 1. Pack 管理
- 列出所有 Pack 类型
- 创建/编辑/删除 Pack
- 设置价格、库存、概率
- 设置 Buyback 比例 (85%/90%)
- 上架/下架 Pack
- 批量操作

### 2. 用户管理
- 列出所有用户
- 查看用户详情 (余额、持仓、交易历史)
- 冻结/解冻用户
- 设置用户等级 (VIP)
- 查看 KYC 状态

### 3. 订单管理
- 列出所有订单 (购买、开盒、交易)
- 筛选 (状态、日期、用户、类型)
- 查看订单详情
- 手动处理订单

### 4. Vault 库存管理
- 列出所有托管的卡片
- 卡片状态 (已入库/已锁定/已兑换/已发出)
- 物理位置记录
- 批量导入卡片

### 5. 财务
- 收入概览 (日/周/月)
- 手续费收入
- Buyback 支出
- Stripe 对账
- 导出报表

### 6. 营销活动
- 创建促销活动
- 设置 Buyback BOOST
- Referral 奖励配置
- Leaderboard 奖励配置

### 7. 系统配置
- 手续费比例 (2%)
- 版税比例 (1%)
- Stripe API 配置
- Solana RPC 配置
- 环境变量管理

### 8. 日志 & 审计
- 操作日志
- 异常日志
- 用户行为追踪

## 验收标准
- [ ] Admin 页面可访问 (需 admin 权限)
- [ ] Pack CRUD 完整
- [ ] 用户管理完整
- [ ] 订单查看完整
- [ ] Vault 库存可见
- [ ] 财务数据可导出
