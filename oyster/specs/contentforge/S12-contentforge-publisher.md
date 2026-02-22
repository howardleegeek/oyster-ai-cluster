---
task_id: S12-contentforge-publisher
project: contentforge
priority: 1
depends_on: ["S11-contentforge-content-generator"]
modifies: ["services/publisher.py", "api/routes/publish.py"]
executor: glm
---
## 目标
实现多平台内容发布接口

## 技术方案
- 定义支持的平台枚举
- 封装各平台API调用
- 实现统一的发布接口

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 支持Twitter/Discord等平台发布
- [ ] 返回发布结果和平台ID
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
