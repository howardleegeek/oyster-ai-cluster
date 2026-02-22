---
task_id: S01-depin-assistant-bootstrap
project: depin-assistant
priority: 1
depends_on: []
modifies: ["backend/main.py", "backend/config.py"]
executor: glm
---
## 目标
Bootstrap depin-assistant project: AI驱动的Web3去中心化物理基础设施网络任务助手，自动管理节点运营与收益优化

## 约束
- 技术栈: Node.js + Ethers.js + Python
- 实现核心功能的骨架代码
- 写基础测试

## 验收标准
- [ ] 核心模块有基础实现
- [ ] pytest 能跑通
- [ ] 不留 TODO/FIXME

## 不要做
- 不留 placeholder
- 不做 UI 相关
