---
task_id: S22-mem0-integration
project: dispatch-infra
priority: 1
depends_on: []
modifies:
  - dispatch/memory_store.py
executor: glm
---

# Mem0 Integration: AI 长期记忆层

## 目标
集成 Mem0 到 dispatch，为 Agent 提供长期记忆能力

## 背景
- Mem0: 47k stars, 通用记忆层
- 支持向量存储, 个性化, 自适应检索

##具体改动

### 1. 新增 memory_store.py
```python
from mem0 import Memory

class DispatchMemory:
    """Dispatch 的记忆存储"""
    
    def __init__(self, config: dict = None):
        self.memory = Memory(config or {})
    
    def add(self, data: str, user_id: str = "dispatch") -> str:
        """添加记忆"""
        return self.memory.add(data, user_id=user_id)
    
    def search(self, query: str, user_id: str = "dispatch") -> list:
        """搜索记忆"""
        return self.memory.search(query, user_id=user_id)
    
    def get_all(self, user_id: str = "dispatch") -> list:
        """获取全部记忆"""
        return self.memory.get_all(user_id=user_id)
    
    def update(self, memory_id: str, data: str):
        """更新记忆"""
        self.memory.update(memory_id, data)
    
    def delete(self, memory_id: str):
        """删除记忆"""
        self.memory.delete(memory_id)
```

### 2. 记忆类型
- **任务记忆**: 任务历史, 成功模式
- **错误记忆**: 失败教训, 避免重复
- **用户记忆**: 用户偏好, 交互历史

### 3. 配置
```json
{
  "mem0": {
    "enabled": false,
    "vector_store": "qdrant",
    "embedder": "claude"
  }
}
```

## 验收标准
- [ ] 能添加记忆
- [ ] 能搜索记忆
- [ ] 能更新/删除
