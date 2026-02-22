---
task_id: S11-contentforge-content-generator
project: contentforge
priority: 1
depends_on: []
modifies: ["api/routes/generator.py", "services/generator.py"]
executor: glm
---
## 目标
实现AI内容生成API，支持批量生成社交媒体文案

## 技术方案
- 定义内容生成请求Schema
- 集成AI模型生成文案
- 支持模板变量替换

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] POST /generate 返回生成的内容
- [ ] 支持批量生成
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
