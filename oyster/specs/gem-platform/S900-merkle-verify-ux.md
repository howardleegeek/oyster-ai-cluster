---
task_id: S900-merkle-verify-ux
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/MyOpenings.tsx
  - lumina/services/packApi.ts
executor: glm
---

## 目标
实现 Merkle Root 验证 UX - 一键验证开包公平性

## 功能
1. 开包结果展示 Pool ID / Odds Version / Merkle Root
2. "一键验证"按钮，引导用户验证
3. 显示验证步骤

## 验收
- [ ] 开包记录显示 Merkle Root
- [ ] 验证按钮可用
