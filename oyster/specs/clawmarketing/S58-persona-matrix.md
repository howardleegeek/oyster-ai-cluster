---
task_id: S58-persona-matrix
project: clawmarketing
priority: 1
depends_on: [S57-campaign-crud]
modifies:
  - frontend/src/pages/Personas.tsx
---

## 目标
Personas 页面连接 /api/v2/personas/

## 具体改动
1. 获取 persona 列表
2. 创建新 persona
3. 编辑 persona
4. 删除 persona

## 验收标准
- [ ] 显示所有 personas
- [ ] 可创建/编辑/删除
