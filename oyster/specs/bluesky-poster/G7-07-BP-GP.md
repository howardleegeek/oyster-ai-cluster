---
task_id: G7-07-BP-GP
project: bluesky-poster
priority: 2
depends_on: []
modifies: ["src/services/nft_showcase.py", "src/api/embed.py"]
executor: glm
---
## 目标
Bluesky 帖子自动展示 NFT 藏品卡片

## 技术方案
1. 新增 `NFTShowcasePoster` 类，调用 GP API 获取 NFT 详情
2. 生成 OpenGraph 卡片图片（含 NFT 预览图+元数据）
3. BP 发布时自动附加 NFT 卡片挂件
4. 支持绑定 Bluesky 帖子链接到 GP 交易页

## 约束
- 复用现有 BP 发布逻辑
- 基础测试覆盖卡片生成
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] NFT 卡片 3s 内生成
- [ ] 支持 mp4/gif 动图
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
