---
task_id: S201-marketplace-list
project: gem-platform
priority: 2
depends_on: []
modifies: ["backend/app/routes/marketplace.py", "backend/app/services/listing.py"]
executor: glm
---
## 目标
实现 marketplace NFT 列表页 API，支持分页、筛选、排序

## 约束
- 在已有 Flask app 内修改
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_marketplace_list.py 全绿
- [ ] 支持分页 (page, per_page)
- [ ] 支持价格区间筛选
- [ ] 支持排序 (price_asc, price_desc, recent)

## 不要做
- 不留 TODO/FIXME/placeholder
