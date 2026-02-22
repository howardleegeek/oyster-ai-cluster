---
task_id: G7-08-CM-GP-BP
project: clawmarketing
priority: 1
depends_on: ["G7-01-CM-BP", "G7-03-GP-CM"]
modifies: ["src/services/omnichannel_engine.py", "src/models/campaign.py"]
executor: glm
---
## 目标
构建全渠道营销引擎，一次内容多平台分发

## 技术方案
1. 新增 `OmnichannelMarketingEngine` 类，编排 CM->BP->GP 流程
2. 扩展 `Campaign` 模型支持多渠道配置 (twitter, bluesky, website, nft)
3. 渠道状态追踪：pending -> published -> feedback
4. 统一 Dashboard 展示全渠道数据

## 约束
- 复用已集成的 CM-BP, GP-CM 模块
- 不新建超过2个文件
- 在现有代码库内修改
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 单次活动分发 < 5s
- [ ] 渠道成功率 > 95%
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
