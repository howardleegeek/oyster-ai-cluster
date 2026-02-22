---
task_id: CLAW-01-cluster-test
project: clawcontrol
priority: 1
depends_on: []
modifies:
  - pipeline/clawcontrol/
---

## 目标
让集群真正执行 ClawControl 任务，测试端到端流程

## 约束
- 使用现有 140 slots 集群
- 复用现有 dispatch.py
- 不修改核心调度逻辑

## 具体改动
1. 创建一个测试任务
2. 通过 dispatch 分发到集群
3. 执行 agent 写代码
4. 运行测试验证
5. 返回结果

## 验收标准
- [ ] 任务成功分发到节点
- [ ] Agent 执行完成
- [ ] 测试通过
- [ ] 结果返回

## 验证命令
```bash
cd ~/Downloads/dispatch
python3 dispatch.py start clawcontrol
```
