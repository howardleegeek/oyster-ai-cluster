---
task_id: S02-create-brand
project: clawmarketing
priority: 2
depends_on: [S01-fix-login]
modifies: []
executor: local
---

## 目标
用户可以创建品牌

## 具体改动
1. 前端添加品牌创建功能
2. 调用 POST /api/v1/brands 创建品牌
3. 验证品牌创建成功

## 验收标准
- [ ] 可以创建品牌
- [ ] 品牌出现在列表中
