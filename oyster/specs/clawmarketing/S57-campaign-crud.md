---
task_id: S57-campaign-crud
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/Campaigns.tsx
---

## 目标
Campaigns 页面连接真实 API

## 具体改动
1. 获取 /api/v2/campaigns/ 数据
2. 实现创建战役表单 → POST /api/v2/campaigns/
3. 实现编辑战役
4. 实现删除战役

## 验收标准
- [ ] 战役列表显示真实数据
- [ ] 可以创建新战役
- [ ] 可以编辑战役

## 验证
```bash
curl -s http://localhost:8001/api/v2/campaigns/
```
