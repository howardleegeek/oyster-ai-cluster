---
task_id: S39-openapi-docs
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
完善OpenAPI文档

##具体改动
1. 配置 FastAPI 自动生成完整 OpenAPI
2. 添加 response_model 到所有端点
3. 添加 docstring 文档
4. 配置 /docs 和 /redoc

##验收标准
- [ ] /docs 可访问
- [ ] /openapi.json 完整
- [ ] 所有端点有文档
