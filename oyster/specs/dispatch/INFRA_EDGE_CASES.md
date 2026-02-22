# 基础设施 Edge Cases 思考

## 1. 代码同步 Edge Cases

| Edge Case | 影响 | 解决方案 |
|-----------|------|----------|
| rsync 失败 | 任务无法执行 | 重试 3 次，失败告警 |
| 同步时任务正在执行 | 代码版本不一致 | 同步前检查任务状态，或等任务完成 |
| 同步中断 | 不完整代码 | 删除远程目录后重试 |
| 磁盘空间不足 | 同步失败 | 检查磁盘空间，不足则跳过 |

## 2. task-watcher Edge Cases

| Edge Case | 影响 | 解决方案 |
|-----------|------|----------|
| 多个 watcher 同一任务 | 重复执行 | status.json 锁或检查 |
| spec 文件格式错误 | 执行失败 | 跳过并标记 failed |
| 任务执行超时 | 占用 slot | 2 小时强制 kill |
| wrapper 不存在 | 无法执行 | Guardian 检查并推送 |

## 3. Guardian Edge Cases

| Edge Case | 影响 | 解决方案 |
|-----------|------|----------|
| SSH 超时 | 检查失败 | 加 timeout=30s，重试 |
| 节点完全失联 | 监控盲区 | 连续 3 次失败标记 dead |
| DB 锁死 | 检查卡住 | timeout=10s，skip |
| 检查间隔太长 | 问题发现慢 | 可配置间隔，默认 5 分钟 |

## 4. Bridge Edge Cases

| Edge Case | 影响 | 解决方案 |
|-----------|------|----------|
| 消息格式错误 | 处理崩溃 | try-catch，跳过 |
| 处理超时 | 消息积压 | 30s timeout |
| 循环消息 | 无限循环 | 检查 reply_to，防止回环 |
| DB 锁 | 写入失败 | retry 3 次 |

## 5. dispatch Edge Cases

| Edge Case | 影响 | 解决方案 |
|-----------|------|----------|
| 依赖循环 | 调度死锁 | spec 扫描检测 |
| 节点同时满 | 任务堆积 | 告警 + 排队 |
| slot 计算错误 | 超负载 | 每次检查重新计算 |
| 任务僵尸 | DB 不一致 | Guardian 清理 |

## 6. 待实现修复

### 6.1 rsync 重试
```python
def rsync_with_retry(node, local, remote, max_retries=3):
    for i in range(max_retries):
        result = subprocess.run(...)
        if result.returncode == 0:
            return True
        time.sleep(5)
    return False
```

### 6.2 task-watcher 防重复
```python
# 检查 status 是否已变为 running
if status != "pending":
    continue  # 已被其他 watcher 处理
```

### 6.3 Guardian SSH 超时
```python
def ssh_cmd(node, cmd, timeout=30):
    try:
        return run_cmd(["ssh", "-o", "ConnectTimeout=30", node, cmd], timeout)
    except:
        return (-1, "", "timeout")
```

### 6.4 Bridge 防循环
```python
# 检查消息是否已处理
if msg["id"] in processed_ids:
    continue
processed_ids.add(msg["id"])
```

## 7. 监控告警

需要加的告警：
- [ ] 任务 pending > 1 小时
- [ ] 节点 running > slots
- [ ] rsync 失败 > 3 次
- [ ] SSH 连续失败 > 3 次
- [ ] Bridge 消息积压 > 10 条
