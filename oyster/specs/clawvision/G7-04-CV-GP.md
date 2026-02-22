---
task_id: G7-04-CV-GP
project: clawvision
priority: 2
depends_on: []
modifies: ["src/services/nft_landing_generator.py", "src/api/generator.py"]
executor: glm
---
## 目标
NFT 系列 mint 前自动生成 AI 视觉着陆页

## 技术方案
1. 新增 `NFTLandingGenerator` 类，调用 CV 图像生成 + GP 系列元数据
2. API 端点 `/api/v1/nft/landing/generate`，接收 collection_address
3. 生成多尺寸 OG 图片 + 动态背景视频
4. 产物存储至 OI CDN，回传 URL 给 GP

## 约束
- 复用 GP 现有 collection API
- 基础测试覆盖生成流程
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 单系列生成 < 30s
- [ ] 支持 5 种尺寸 OG 图
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
