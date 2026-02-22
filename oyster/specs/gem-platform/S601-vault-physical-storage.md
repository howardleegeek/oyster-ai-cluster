---
task_id: S601-vault-physical-storage
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/vault.py (EXTEND EXISTING)
  - lumina/services/vaultApi.ts (EXTEND EXISTING)
  - lumina/components/VaultPanel.tsx (NEW FILE)
executor: glm
---

## 目标
扩展现有的 Vault 系统，添加物理存储功能

## 约束
- 文件已存在，需要扩展功能
- 使用现有后端框架
- 不改其他页面 UI

## 现有文件
- backend/app/api/vault.py - 已存在，需扩展
- lumina/services/vaultApi.ts - 已存在，需扩展

## 功能需求

### 后端 (扩展 vault.py)
1. **卡片入库** - POST /api/vault/checkin
   - 录入卡片信息 (名称、稀有度、状态)
   - 拍照存档
   - 生成存储位置

2. **库存管理** - GET /api/vault/items
   - 按状态筛选 (stored/reserved/shipped)
   - 按稀有度筛选
   - 搜索

3. **存储位置** - 每个卡片有唯一位置
   - 货架号
   - 盒子号
   - 位置坐标

4. **状态管理**
   - stored: 已入库
   - reserved: 预留中
   - shipping: 发货中
   - shipped: 已发出

5. **管理员**
   - 批量导入
   - 库存统计
   - 位置调整

### 前端 (VaultPanel.tsx)
1. 查看自己托管的卡片
2. 卡片状态展示
3. 存储位置展示

## 约束
- 使用现有后端框架
- 不改其他页面 UI

## 验收
- [ ] 卡片可入库
- [ ] 库存列表可查看
- [ ] 状态更新可用
- [ ] 前端可查看托管卡片
