---
task_id: S02-BRAND-TELOS-MODEL
project: clawmarketing
priority: 1
depends_on: [S01-LLM-ROUTER]
modifies:
  - backend/models/brand.py
executor: glm
---

## 目标
在 Brand model 中新增 TELOS JSONB 字段

## 具体改动
1. 在 backend/models/brand.py 中新增 telos 字段 (JSONB 类型)
2. telos 结构包含:
   - mission: 品牌使命 (一句话)
   - goals: 当前营销目标 (可量化列表)
   - voice: {tone, personality[], taboos[]}
   - strategy: {platforms[], frequency, content_mix}
   - challenges: 当前挑战列表
   - narratives: 核心叙事/话术列表

## 验收标准
- [ ] Brand model 有 telos 字段
- [ ] black backend/models/brand.py 检查通过

## 不要做
- 不动其他文件
