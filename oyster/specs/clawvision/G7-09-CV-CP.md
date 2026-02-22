---
task_id: G7-09-CV-CP
project: clawvision
priority: 2
depends_on: []
modifies: ["src/services/mobile_optimizer.py", "src/api/adaptation.py"]
executor: glm
---
## 目标
移动端着陆页自适应优化

## 技术方案
1. 新增 `MobileLandingAdapter` 服务，分析 CV 热力图
2. 输出移动端布局建议：按钮位置、图片尺寸、排版
3. API 端点 `/api/v1/landing/mobile/optimize`
4. 集成 CP 实时预览功能

## 约束
- 复用 CV 现有分析引擎
- 基础测试覆盖适配逻辑
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 适配建议生成 < 3s
- [ ] 支持主流移动分辨率
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
