---
task_id: S24-self-acting-orchestrator
project: dispatch-infra
priority: 1
depends_on: ["S21-browser-use-integration", "S22-mem0-integration", "S23-langgraph-integration"]
modifies:
  - dispatch/self_orchestrator.py
  - dispatch/event_bus.py
executor: glm
---

# Self-Acting Orchestrator: 让模块自主协作

## 目标
让 Browser-Use、Mem0、LangGraph 等模块能**自主协作**，形成闭环：

```
发现问题 → 记忆 → 推理 → 行动 → 验证 → 学习
```

## 核心概念

### 1. 事件总线 (Event Bus)
模块之间通过事件通信：

```python
class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.subscribers = {}  # event_type -> [callbacks]
    
    def publish(self, event_type: str, data: dict):
        """发布事件"""
        for callback in self.subscribers.get(event_type, []):
            callback(data)
    
    def subscribe(self, event_type: str, callback: callable):
        """订阅事件"""
        self.subscribers.setdefault(event_type, []).append(callback)
```

### 2. 事件类型

| 事件 | 触发者 | 消费者 |
|------|--------|--------|
| `task.started` | dispatch | memory, graph |
| `task.completed` | executor | memory, orchestrator |
| `task.failed` | executor | memory, orchestrator |
| `error.detected` | any module | memory, orchestrator |
| `fix.applied` | guardian | memory, graph |
| `finding.found` | auditor | memory, orchestrator |

### 3. 自我行动循环

```python
class SelfOrchestrator:
    """自我行动编排器"""
    
    def __init__(self, event_bus, memory, browser, graph):
        self.event_bus = event_bus
        self.memory = memory
        self.browser = browser
        self.graph = graph
        self._setup_subscriptions()
    
    def _setup_subscriptions(self):
        """设置事件订阅"""
        self.event_bus.subscribe("error.detected", self.on_error)
        self.event_bus.subscribe("finding.found", self.on_finding)
        self.event_bus.subscribe("task.completed", self.on_completed)
    
    def on_error(self, data: dict):
        """错误发生时"""
        # 1. 记忆错误
        self.memory.add(f"Error: {data['error']}", tags=["error"])
        
        # 2. 推理根因
        root_cause = self.graph.reason(data)
        
        # 3. 决定行动
        action = self.decide_action(root_cause)
        
        # 4. 执行行动
        if action == "retry":
            self.browser.retry_task(data["task_id"])
        elif action == "fix":
            self.apply_fix(data)
        elif action == "escalate":
            self.escalate(data)
    
    def on_finding(self, data: dict):
        """发现问题时"""
        # 1. 记忆发现
        self.memory.add(f"Finding: {data['finding']}", tags=["finding"])
        
        # 2. 评估严重度
        severity = self.graph.assess(data)
        
        # 3. 如果严重，自动修复
        if severity > 7:
            self.auto_fix(data)
    
    def on_completed(self, data: dict):
        """任务完成时"""
        # 1. 提取经验
        lessons = self.graph.extract_lessons(data)
        
        # 2. 存入记忆
        for lesson in lessons:
            self.memory.add(lesson, tags=["lesson", "success"])
        
        # 3. 更新图谱
        self.graph.update_success_pattern(data)
```

### 4. 自主行动流程

```
┌─────────────────────────────────────────────────────────┐
│                    事件总线                             │
│   error.detected ←─ finding.found ←─ task.completed   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  自我编排器                              │
│  1. 记忆 (Mem0)                                        │
│     - 存错误、存发现、存经验                            │
│  2. 推理 (LangGraph)                                    │
│     - 分析根因、评估严重度、决定行动                     │
│  3. 行动 (Browser-Use)                                │
│     - 重试、修复、升级                                  │
│  4. 验证                                              │
│     - 确认修复有效                                      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    反馈循环                              │
│  验证结果 → 更新记忆 → 优化决策                         │
└─────────────────────────────────────────────────────────┘
```

### 5. 配置

```json
{
  "orchestrator": {
    "enabled": true,
    "auto_fix_threshold": 7,
    "max_auto_retries": 3,
    "escalate_after": 5,
    "learning_enabled": true
  },
  "events": {
    "queue_size": 1000,
    "retry_failed": true
  }
}
```

## 文件清单

| 文件 | 描述 |
|------|------|
| `dispatch/event_bus.py` | 事件总线 |
| `dispatch/self_orchestrator.py` | 自我编排器 |

## 验收标准

- [ ] 事件能触发行动
- [ ] 错误能自动重试
- [ ] 严重问题能自动修复
- [ ] 经验能存入记忆
- [ ] 决策能自我优化

## 不做

- ❌ 不修改现有模块内部逻辑
- ❌ 不自动执行危险操作（需人工确认）
