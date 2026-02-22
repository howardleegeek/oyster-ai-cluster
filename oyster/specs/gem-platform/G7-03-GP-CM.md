---
task_id: G7-03-GP-CM
project: gem-platform
priority: 1
depends_on: []
modifies: ["src/services/nft_marketing.py", "src/api/nft_events.py"]
executor: glm
---
## 目标
NFT 上市/交易事件自动触发营销推广流程

## 技术方案
1. 在 GP 新增 `NFTMarketingTrigger` 监听 NFT 事件 (mint, list, sale, transfer)
2. 事件匹配 CM 营销模板，生成推广内容
3. 集成 OI 事件总线，发布 `nft.marketing.triggered` 事件
4. 支持自定义营销规则引擎

## 约束
- 复用现有 CM 内容生成逻辑
- 不改 GP 核心交易逻辑
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] NFT 上市事件 10s 内触发营销
- [ ] 支持自定义营销规则
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
