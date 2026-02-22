---
task_id: S14-contentforge-template-manager
project: contentforge
priority: 2
depends_on: ["S11-contentforge-content-generator"]
modifies: ["services/template.py", "api/routes/template.py"]
executor: glm
---
## 目标
实现内容模板管理

## 技术方案
- 定义模板模型和存储
- 提供CRUD操作接口
- 支持变量占位符解析

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 可创建和查询模板
- [ ] 模板可被内容生成调用
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
