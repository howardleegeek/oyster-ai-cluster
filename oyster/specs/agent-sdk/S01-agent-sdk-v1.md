---
task_id: S01-agent-sdk-v1
project: agent-sdk
priority: 1
depends_on: []
modifies:
  - agent-sdk/
executor: glm
---

## 目标
构建模块化、可插拔的 Agent SDK，让外部可以调用集群执行任务

## 约束
- 不修改现有 Pipeline/Dispatch 核心逻辑
- 使用 Python + FastAPI 构建
- 安全边界：review gate、max iterations、git branch 隔离

## 具体改动

### 1. 目录结构
```
agent-sdk/
├── src/
│   ├── agent_sdk/
│   │   ├── __init__.py
│   │   ├── api.py          # HTTP API 入口
│   │   ├── task_router.py  # 任务拆解
│   │   ├── executor.py     # 执行器 (调用 Dispatch)
│   │   ├── security.py     # 安全边界
│   │   └── models.py       # 数据模型
│   └── main.py             # FastAPI 入口
├── tests/
├── pyproject.toml
└── README.md
```

### 2. 核心模块

**api.py**
- POST /task - 接收任务
- GET /task/{id} - 查询状态
- GET /task/{id}/result - 获取结果

**task_router.py**
- 解析任务描述
- 拆解成可执行的子任务
- 返回任务 DAG

**executor.py**
- 调用 Dispatch 执行任务
- 轮询任务状态
- 收集结果

**security.py**
- Max iterations (默认 3)
- Review gate flag
- Git branch 隔离
- Sandbox 模式

### 3. 安全边界设计
```python
class SecurityConfig:
    max_iterations: int = 3      # 最大迭代次数
    review_required: bool = True # 是否需要 review
    sandbox_mode: bool = True     # 沙箱模式
    branch_isolation: bool = True # 分支隔离
```

## 验收标准
- [ ] API 能接收任务并返回 task_id
- [ ] 能调用 Dispatch 执行任务
- [ ] 能查询任务状态和结果
- [ ] 安全边界生效 (max iterations, review flag)

## 测试命令
```bash
cd ~/Downloads/agent-sdk
python3 -m pytest tests/ -v
```
