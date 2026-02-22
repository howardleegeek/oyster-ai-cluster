---
task_id: G7-01-CM-BP
project: clawmarketing
priority: 1
depends_on: []
modifies: ["src/services/social_sync.py", "src/api/webhooks.py"]
executor: glm
---
## 目标
实现 clawmarketing 内容自动同步发布到 Bluesky (bluesky-poster)

## 技术方案
1. 在 clawmarketing 新增 `SocialPoster` 类，封装 Bluesky AT Protocol API
2. 创建 webhook 端点 `/webhooks/bluesky/publish`，接收营销内容
3. 内容自动转换：markdown -> Bluesky 卡片格式，含图片Alt文本
4. 集成 OI 事件总线，发布 `content.published` 事件供 BP 消费

## 约束
- 复用现有 `bluesky-poster` 的 API client 配置
- 撰写基础单元测试覆盖发布逻辑
- 不修改 UI
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 内容发布后 5 秒内同步到 Bluesky
- [ ] 支持文字+图片组合
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
