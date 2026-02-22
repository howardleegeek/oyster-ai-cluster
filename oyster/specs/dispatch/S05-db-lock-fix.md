---
task_id: S05-db-lock-fix
project: dispatch
priority: 0
depends_on: []
modifies: ["dispatch/dispatch.py"]
executor: glm
---
## 目标
修复 dispatch.py 中 apply_task_updates → release_file_locks 的 SQLite "database is locked" 错误

## 问题
`apply_task_updates()` (line ~612) 在一个事务中调用 `release_file_locks()`，而 `release_file_locks()` (line ~210) 内部又打开了一个独立的 `sqlite3.connect()`。这导致两个连接竞争同一个 DB，触发 "database is locked"。

## 具体改动
文件: `~/Downloads/dispatch/dispatch.py`

方案: 让 `release_file_locks()` 接受一个可选的 `conn` 参数。如果传入了外部连接就用它，不新建连接。

1. 修改 `release_file_locks` 函数签名:
```python
def release_file_locks(db_path, task_id, conn=None):
```

2. 函数内部: 如果 `conn` 不为 None，直接用它执行 SQL，不新建连接也不关闭。如果 `conn` 为 None，保持原有逻辑（自己创建连接）。

3. 在 `apply_task_updates()` 调用处，把当前事务的 `conn` 传进去:
```python
release_file_locks(db_path, update['id'], conn=conn)
```

## 验收标准
- [ ] `python3 dispatch.py start dispatch` 不再报 "database is locked"
- [ ] `python3 -c "import dispatch"` 无语法错误
- [ ] `grep "def release_file_locks" dispatch.py` 显示函数签名包含 `conn=None`

## 不要做
- 不改其他函数
- 不改 DB schema
- 不加新依赖
