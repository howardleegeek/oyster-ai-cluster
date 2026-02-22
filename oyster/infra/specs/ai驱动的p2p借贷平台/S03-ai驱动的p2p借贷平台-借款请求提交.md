---
task_id: S03-ai驱动的p2p借贷平台-借款请求提交
project: ai驱动的p2p借贷平台
priority: 1
depends_on: ["S01-ai驱动的p2p借贷平台-bootstrap"]
modifies: ["backend/loan_request.py", "backend/database.py", "tests/test_loan_request.py"]
executor: glm
---
## 目标
开发借款请求提交接口，包括借款金额、期限、利率等信息的接收与存储。

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
