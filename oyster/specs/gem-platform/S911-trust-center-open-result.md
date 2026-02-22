---
task_id: S911-trust-center-open-result
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/MyOpenings.tsx
  - backend/app/api/pack.py
executor: glm
---

## Week 1 - Trust Center: 开宝结果验证卡片

## 目标
开宝结果页展示可验证信息

## 功能
1. 开宝结果展示:
   - OpenTx / Proof / ResultHash
   - Odds Version / Pool ID
   - 一键复制按钮

2. 跳转区块浏览器链接

## 验收
- [ ] 验证信息完整
- [ ] 复制功能可用
