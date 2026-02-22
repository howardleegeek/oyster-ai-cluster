---
task_id: S05-agentforge-workflow-visualization
project: agentforge
priority: 3
depends_on: ["S02-agentforge-workflow-engine"]
modifies: ["api/routes/visualization.py"]
executor: glm
---
## 目标
提供工作流可视化所需的数据结构API

## 技术方案
- 将工作流转换为前端图库所需格式
- 返回nodes和edges数据结构
- 支持层级和位置信息

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 返回符合前端渲染的数据格式
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
