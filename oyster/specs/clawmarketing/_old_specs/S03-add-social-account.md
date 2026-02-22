---
task_id: S03-add-social-account
project: clawmarketing
priority: 3
depends_on: [S02-create-brand]
modifies: []
executor: local
---

## 目标
用户可以添加社交账号

## 具体改动
1. 前端添加社交账号页面
2. 支持 Twitter, Discord, Instagram, LinkedIn
3. 调用 POST /api/v1/accounts 创建账号

## 验收标准
- [ ] 可以添加 Twitter 账号
- [ ] 账号出现在列表中
