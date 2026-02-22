---
task_id: S04-create-persona
project: clawmarketing
priority: 4
depends_on: [S03-add-social-account]
modifies: []
executor: local
---

## 目标
用户可以创建 AI Persona

## 具体改动
1. 前端添加 Persona 创建页面
2. 设置人设名称、性格、风格
3. 调用 POST /api/v1/personas

## 验收标准
- [ ] 可以创建 Persona
- [ ] Persona 出现在列表中
