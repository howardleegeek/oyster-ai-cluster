---
task_id: S19-agent-teams-integration
project: dispatch-infra
priority: 2
depends_on: ["S13-ai-os-integration"]
modifies:
  - dispatch/agent_teams_bridge.py
  - dispatch/task_decomposer.py
executor: glm
---

# Agent Teams Integration: 智能任务分解 × 动态重规划

## 目标
将 Claude Code Agent Teams 概念引入 dispatch，实现：
1. AI 驱动的任务智能分解
2. 动态重规划（失败自动重分配）
3. 跨 Agent 信息共享
4. 成本优化（简单任务用便宜模型）

## 背景
当前 dispatch 是"一个 spec → 一个任务"。Agent Teams 可以做到：
- 复杂 spec → 多个子任务并行
- 失败时自动重试 + 重分配
- Agent 间直接沟通

## 具体改动

### 1. 任务分解器 (task_decomposer.py)
```python
class TaskDecomposer:
    """用 AI 分解复杂任务"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def decompose(self, spec_content: str) -> list[dict]:
        """
        输入: spec 文件内容
        输出: 子任务列表
        [
            {"task": "implement API", "model": "sonnet", "priority": 1},
            {"task": "write tests", "model": "sonnet", "priority": 2},
            {"task": "update docs", "model": "haiku", "priority": 3}
        ]
        """
```

### 2. Agent Teams Bridge (agent_teams_bridge.py)
```python
class AgentTeamsBridge:
    """连接 dispatch 到 Agent Teams"""
    
    def __init__(self, config_path: str):
        self.config = self.load_config()
    
    def spawn_team(self, task: dict) -> str:
        """Spawn agent team for complex task"""
        # 使用 CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
    
    def monitor_team(self, team_id: str) -> dict:
        """监控团队状态"""
        # 检查每个 teammate 进度
    
    def reallocate(self, team_id: str, failed_task: str):
        """失败任务重新分配"""
    
    def shutdown_team(self, team_id: str):
        """关闭团队"""
```

### 3. 配置
```json
// dispatch/agent_teams_config.json
{
  "enabled": false,
  "threshold_complexity": 5,
  "model_mapping": {
    "complex": "claude-opus",
    "medium": "claude-sonnet", 
    "simple": "claude-haiku"
  },
  "max_teammates": 5,
  "auto_reallocate": true,
  "cost_budget_per_task": 10.0
}
```

### 4. 成本优化策略
```
- 字数 < 500: haiku
- 字数 500-2000: sonnet  
- 字数 > 2000: opus
- 重试: 一律 haiku
- code review: sonnet
```

## Agent Teams vs Dispatch 对比

| 维度 | Dispatch | Agent Teams 增强 |
|------|---------|---------------|
| 任务粒度 | Spec 级 | 子任务级 |
| 失败处理 | 重试 | 重分配 + 重试 |
| Agent 沟通 | 无 | 直接消息 |
| 成本控制 | 固定模型 | 动态模型选择 |

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `dispatch/task_decomposer.py` | 新建 | AI 任务分解器 |
| `dispatch/agent_teams_bridge.py` | 新建 | Agent Teams 桥接 |
| `dispatch/agent_teams_config.json` | 新建 | 配置文件 |

## 验收标准

- [ ] 能分解复杂 spec 为子任务
- [ ] 能根据任务复杂度选择模型
- [ ] 能监控团队状态
- [ ] 失败时能自动重分配
- [ ] 能生成成本报告

## 不要做

- ❌ 不修改现有调度逻辑
- ❌ 不强制使用 Agent Teams
- ❌ 不存储敏感 API keys
