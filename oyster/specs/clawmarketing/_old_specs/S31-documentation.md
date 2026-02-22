---
task_id: S31-documentation
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
API文档 - OpenAPI自动生成，使用示例

##具体改动
1. 创建 docs/openapi.json - 完整OpenAPI spec
2. 创建 docs/API.md - API使用文档
3. 创建 docs/EXAMPLES.md - 使用示例
4. 配置 FastAPI 自动生成docs

##验收标准
- [ ] /docs 可访问
- [ ] /openapi.json 可访问
- [ ] 有使用示例
