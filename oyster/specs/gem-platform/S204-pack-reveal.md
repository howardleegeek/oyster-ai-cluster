---
task_id: S204-pack-reveal
project: gem-platform
priority: 2
depends_on: ["S200-purchase-flow"]
modifies: ["backend/app/routes/pack.py", "backend/app/services/reveal.py"]
executor: glm
---
## 目标
实现 pack 开箱数据接口，返回 NFT 随机结果和动画种子

## 约束
- 在已有 Flask app 内修改
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_pack_reveal.py 全绿
- [ ] 开箱结果基于加密随机数种子
- [ ] 返回 NFT 元数据供前端动画
- [ ] 开箱后 NFT 绑定到用户

## 不要做
- 不留 TODO/FIXME/placeholder
