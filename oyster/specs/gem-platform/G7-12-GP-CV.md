---
task_id: G7-12-GP-CV
project: gem-platform
priority: 2
depends_on: ["G7-04-CV-GP"]
modifies: ["src/services/collection_analytics.py", "src/api/insights.py"]
executor: glm
---
## 目标
NFT 系列实时视觉分析看板

## 技术方案
1. 新增 `CollectionVisualAnalytics` 服务，聚合 CV 分析数据
2. 展示：mint 页面视觉热度、用户关注点、转化关联
3. API 端点 `/api/v1/collection/{id}/visual-insights`
4. 实时同步 CV 更新

## 约束
- 复用 CV 分析 API
- 基础测试覆盖数据聚合
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 看板加载 < 2s
- [ ] 支持时间范围筛选
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
