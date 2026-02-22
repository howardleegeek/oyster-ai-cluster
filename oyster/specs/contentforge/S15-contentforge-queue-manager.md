---
task_id: S15-contentforge-queue-manager
project: contentforge
priority: 3
depends_on: ["S12-contentforge-publisher"]
modifies: ["services/queue.py", "models/queue.py"]
executor: glm
---
## 目标
实现发布队列管理服务

## 技术方案
- 定义发布任务队列模型
- 实现先进先出调度
- 支持定时发布和重试

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 任务进入队列并按序发布
- [ ] 支持定时发布设置
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
