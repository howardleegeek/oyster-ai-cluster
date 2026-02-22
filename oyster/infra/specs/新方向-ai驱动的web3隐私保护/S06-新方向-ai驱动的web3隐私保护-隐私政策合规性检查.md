---
task_id: S06-新方向-ai驱动的web3隐私保护-隐私政策合规性检查
project: 新方向-ai驱动的web3隐私保护
priority: 3
depends_on: ["S01-新方向-ai驱动的web3隐私保护-bootstrap"]
modifies: ["backend/compliance.py"]
executor: glm
---
## 目标
开发自动化的隐私政策合规性检查功能，确保数据处理符合相关法规

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
