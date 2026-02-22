---
task_id: S29
project: dispatch-infra
priority: 1
depends_on: []
modifies:
  - dispatch/memory_store.py
  - dispatch/event_bus.py
  - dispatch/self_orchestrator.py
  - dispatch/memory_learner.py
---

## 目标

在 dispatch 系统中集成 zvec (embedded vector store)，提供语义记忆层。

## 约束
- 不改现有事件流结构
- 不碰 UI/CSS
- 不加新外部依赖（用已有的或 pip install）
- zvec 作为 adapter 可替换，不硬编码

## 具体改动

### 1. 创建 zvec adapter (dispatch/memory_store.py)
- 基于纯 Python 实现 (SimpleEmbedder)
- 提供 `add()`, `search()`, `delete()` 接口
- SQLite 存储向量 (无需外部依赖)

### 2. 集成到 event_bus
- 事件写入时自动向量化存储
- 支持语义检索历史事件

### 3. 创建 CLI 命令
- `python dispatch.py memory search <query>` - 语义搜索
- `python dispatch.py memory stats` - 向量库统计
- `python dispatch.py memory add <content> --type <type>` - 添加记忆
- `python dispatch.py memory clear --type <type>` - 清除记忆

### 4. 集成到 self_orchestrator
- 自动创建 MemoryStore (如未提供)
- 错误分析时搜索相似解决方案

### 5. Memory Learner (dispatch/memory_learner.py)
- 定期从 dispatch.db 学习已完成任务
- 提供 `--recommend` 命令获取问题建议
- 定时任务: 每 6 小时自动学习

### 6. 初始化向量库
- 加载 dispatch.db 历史任务 (200+)
- 加载 AIOS events
- 加载 specs 摘要
- 加载 flight_rules

## 验收标准
- [x] 纯 Python 向量存储实现
- [x] `from memory_store import MemoryStore` 无报错
- [x] 向量搜索返回相关结果
- [x] CLI 命令可用
- [x] Event bus 集成自动向量化
- [x] SelfOrchestrator 自动使用 memory
- [x] 定时学习任务已配置
- [x] 349 条记忆已初始化

## 使用方式

```bash
# CLI 搜索
python3 dispatch.py memory search "scheduling patterns" --limit 5

# CLI 统计
python3 dispatch.py memory stats

# 获取问题建议
python3 memory_learner.py --recommend "connection timeout"

# 手动学习
python3 memory_learner.py --learn --hours 24
```

## 架构

```
Events → EventBus → MemoryStore (SQLite)
              ↓
         SelfOrchestrator → 搜索相似解决方案
              ↓
         MemoryLearner (定时) → 从 dispatch.db 学习
```
