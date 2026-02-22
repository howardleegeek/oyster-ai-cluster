---
task_id: G7-14-BP-CV
project: bluesky-poster
priority: 3
depends_on: []
modifies: ["src/services/ai_content_gen.py", "src/api/generate.py"]
executor: glm
---
## 目标
基于 CV 视觉分析生成 Bluesky 帖子文案

## 技术方案
1. 新增 `AIContentGenerator` 类，调用 CV 图像描述 API
2. 自动生成图片 Alt + 描述文案 + hashtag
3. 支持风格模板：正式/幽默/简洁
4. 集成 BP 自动发布

## 约束
- 复用 CV 图像理解能力
- 基础测试覆盖生成逻辑
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 文案生成 < 2s
- [ ] 支持 3 种风格
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
