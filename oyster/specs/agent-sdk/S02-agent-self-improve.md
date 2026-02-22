---
task_id: S02-agent-self-improve
project: agent-sdk
priority: 2
depends_on: ["S01-agent-sdk-v1"]
modifies:
  - agent-sdk/src/agent_sdk/
executor: glm
---

## 目标
让 Agent 能够自我进化：自动去 GitHub 搜索好工具，评估并集成到 Infra

## 约束
- 安全第一：所有外部代码引入需要 review
- 先搜索评估，再决定是否集成

## 具体改动

### 1. 新增模块
```
agent-sdk/src/agent_sdk/
├── self_improve/
│   ├── __init__.py
│   ├── github_scanner.py   # 扫描 GitHub 找好工具
│   ├── evaluator.py        # 评估工具价值
│   ├── integrator.py       # 集成工具到 Infra
│   └── evolution_log.py    # 进化记录
```

### 2. GitHub Scanner
- 搜索特定领域的开源项目 (如: "mcp server", "browser automation", "ai agents")
- 按 stars 排序，取 top 10
- 提取关键信息: README, stars, tech stack, license

### 3. Evaluator
- 评估维度:
  - Stars > 1000 (流行度)
  - License (MIT/Apache 可商用)
  - 最近更新 (半年内)
  - 代码质量 (有测试、有 CI)
- 输出评估报告

### 4. Integrator
- 如果评估通过，生成集成方案
- 写对接代码
- 标记需要 human review

### 5. 进化循环
```
1. Agent 收到 "改进 Infra" 任务
        ↓
2. GitHub Scanner 搜索相关工具
        ↓
3. Evaluator 评估 top 10
        ↓
4. Integrator 生成集成方案
        ↓
5. Human Review (安全边界)
        ↓
6. 通过 → 集成到 Infra
   失败 → 记录教训，下次改进
```

## 验收标准
- [ ] 能搜索 GitHub 并返回结果
- [ ] 能评估工具价值
- [ ] 能生成集成方案
- [ ] 进化记录持久化

## 测试命令
```bash
cd ~/Downloads/agent-sdk
python3 -m pytest tests/test_self_improve.py -v
```
