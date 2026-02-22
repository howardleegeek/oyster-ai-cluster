---
task_id: S23-langgraph-integration
project: dispatch-infra
priority: 1
depends_on: []
modifies:
  - dispatch/graph_scheduler.py
executor: glm
---

# LangGraph Integration: 复杂任务编排

## 目标
集成 LangGraph 实现复杂任务的 DAG 编排

## 背景
- LangGraph: 25k stars, LangChain 的 Graph 版本
- 支持循环, 条件分支, 状态管理

## 具体改动

### 1. 新增 graph_scheduler.py
```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from typing import TypedDict

class DispatchState(TypedDict):
    task_id: str
    spec: dict
    messages: list
    result: dict
    error: str

class GraphScheduler:
    """基于 LangGraph 的调度器"""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建任务图"""
        graph = StateGraph(DispatchState)
        
        # 节点
        graph.add_node("parse", self.parse_spec)
        graph.add_node("execute", self.execute_task)
        graph.add_node("review", self.review_result)
        graph.add_node("fix", self.fix_errors)
        
        # 边
        graph.set_entry_point("parse")
        graph.add_edge("parse", "execute")
        graph.add_conditional_edges(
            "execute",
            self.should_review,
            {"review": "review", "fix": "fix", "end": END}
        )
        graph.add_edge("review", "execute")
        graph.add_edge("fix", "execute")
        graph.add_edge("review", END)
        
        return graph.compile()
    
    def run(self, task: dict) -> dict:
        """运行任务图"""
        return self.graph.invoke({
            "task_id": task["id"],
            "spec": task,
            "messages": [],
            "result": {},
            "error": ""
        })
    
    def should_review(self, state: DispatchState) -> str:
        """判断是否需要审核"""
        if state.get("error"):
            return "fix"
        return "review"
```

### 2. 支持的模式

| 模式 | 说明 |
|------|------|
| Sequential | 顺序执行 |
| Parallel | 并行分支 |
| Conditional | 条件分支 |
| Loop | 循环直到成功 |
| Human-in-loop | 人工审核节点 |

### 3. 配置
```json
{
  "langgraph": {
    "enabled": false,
    "max_retries": 3,
    "checkpoint_enabled": true
  }
}
```

## 验收标准
- [ ] 能构建任务图
- [ ] 支持条件分支
- [ ] 支持循环重试
- [ ] 支持检查点
