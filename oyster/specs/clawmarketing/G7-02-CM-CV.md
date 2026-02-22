---
task_id: G7-02-CM-CV
project: clawmarketing
priority: 2
depends_on: []
modifies: ["src/services/landing_page_optimizer.py", "src/models/metrics.py"]
executor: glm
---
## 目标
基于 clawvision AI 视觉分析结果，优化营销着陆页

## 技术方案
1. 新增 `LandingPageOptimizer` 服务，调用 CV API 获取视觉热度图
2. 扩展 `MarketingMetrics` 模型，新增 CV 字段：heat_map_data, visual_attention_score
3. 建立 A/B 测试闭环：CV 分析 -> CM 调整 -> BP 发布 -> CV 复测
4. 存储优化历史到 OI 数据湖

## 约束
- 不新建超过2个文件
- 基础测试覆盖分数计算逻辑
- 在现有代码库内修改
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] CV 响应时间 < 2s
- [ ] 优化建议准确率 > 80%
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
