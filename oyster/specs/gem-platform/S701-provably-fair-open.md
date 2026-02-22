---
task_id: S701-provably-fair-open
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/services/pack_engine.py
  - backend/app/api/pack.py
  - lumina/services/packApi.ts
  - lumina/components/PackOpening.tsx
executor: glm
---

## 目标
实现可验证随机开宝机制 (Provably Fair)

## 功能需求

### 1. 随机性证明
- 接入 VRF 或 Commit-Reveal 机制
- 返回 randomness_proof
- 返回 result_hash (可验证)

### 2. 开宝记录追溯
- 用户"My Openings"页面
- 每次开宝包含：
  - 时间
  - Pack ID
  - Drop ID
  - 随机性证明链接
  - 结果
  - 对应实物资产状态

### 3. API 更新
```python
# POST /api/packs/open 返回
{
  "opening_id": "...",
  "randomness_proof": "...",
  "result_hash": "...",
  "odds_version": "...",
  "revealed_items": [...]
}
```

### 4. 前端
- 开宝结果展示随机性信息
- My Openings 页面

## 约束
- 不改其他模块

## 验收
- [ ] 开宝返回 randomness_proof
- [ ] 可验证结果
- [ ] My Openings 页面可用
