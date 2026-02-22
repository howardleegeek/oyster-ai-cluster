---
task_id: S10-depin-assistant-node-storage
project: depin-assistant
priority: 3
depends_on: ["S06-depin-assistant-node-monitor"]
modifies: ["src/models/Node.js", "src/db/storage.js"]
executor: glm
---
## 目标
实现DePIN节点数据持久化存储

## 技术方案
- 使用JSON文件存储节点数据
- 定义增删改查接口
- 数据备份支持

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 节点数据可持久化保存
- [ ] 数据可正确读取和更新
- [ ] test 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
