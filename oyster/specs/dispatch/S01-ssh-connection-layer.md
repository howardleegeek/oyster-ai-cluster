---
task_id: S01-ssh-connection-layer
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/dispatch.py", "dispatch/nodes.json"]
executor: glm
---

# dispatch.py 连接层重构 - SSH/SCP 统一抽象

## 目标

重构 dispatch.py 的连接层：用 `ssh_host` 别名替代 `ssh_cmd` 完整命令，统一 SCP 逻辑，删除 gcloud 特殊分支。~/.ssh/config 已配好 ControlMaster。

## nodes.json 新格式

```json
{
  "nodes": [
    {
      "name": "codex-node-1",
      "ssh_host": "codex-node-1",
      "slots": 8,
      "api_mode": "direct",
      "executor": "glm",
      "priority": 1
    },
    {
      "name": "glm-node-2",
      "ssh_host": "glm-node-2",
      "slots": 8,
      "api_mode": "direct",
      "executor": "glm",
      "priority": 1
    },
    {
      "name": "mac2",
      "ssh_host": "howard-mac2",
      "slots": 5,
      "api_mode": "zai",
      "executor": "glm",
      "priority": 2
    },
    {
      "name": "mac1",
      "ssh_host": null,
      "slots": 2,
      "api_mode": "direct",
      "executor": "glm",
      "priority": 3
    },
    {
      "name": "codex-local",
      "ssh_host": null,
      "slots": 3,
      "api_mode": "codex",
      "executor": "codex",
      "priority": 2
    }
  ]
}
```

## 具体改动

### 1. `run_ssh_command()` → `run_ssh()`

旧签名: `run_ssh_command(ssh_cmd: str, remote_command: str, timeout=30)`
新签名: `run_ssh(ssh_host: str | None, cmd: str, timeout=30) -> tuple[str | None, str | None]`

```python
def run_ssh(ssh_host, cmd, timeout=30):
    """Execute command via SSH or locally. Returns (stdout, error)."""
    if not ssh_host:
        return None, "No SSH host configured"
    try:
        result = subprocess.run(
            ["ssh", ssh_host, cmd],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip(), None
        else:
            return None, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return None, "SSH command timed out"
    except Exception as e:
        return None, str(e)
```

### 2. 新增 `scp_to_remote()`

```python
def scp_to_remote(ssh_host, local_path, remote_path, timeout=60):
    """SCP file to remote node. Returns (success, error)."""
    result = subprocess.run(
        ["scp", str(local_path), f"{ssh_host}:{remote_path}"],
        capture_output=True, text=True, timeout=timeout
    )
    if result.returncode == 0:
        return True, None
    return False, result.stderr.strip()
```

### 3. 全文替换

- `node['ssh_cmd']` → `node['ssh_host']` (所有出现)
- `run_ssh_command(node['ssh_cmd'], ...)` → `run_ssh(node['ssh_host'], ...)`
- `node.get('host')` / `node['host']` → 删除，用 `node['ssh_host']`

### 4. 删除代码块

- 所有 `if 'gcloud' in node['ssh_cmd']:` 条件分支及其内容
- gcloud SCP 命令构建 (`['gcloud', 'compute', 'scp', ...]`)
- `ssh_parts = node['ssh_cmd'].split()` 及 identity_file 解析
- regular SCP 命令构建中的 identity_file/user_host 拼接
- 用 `scp_to_remote(node['ssh_host'], local_path, remote_path)` 替代

### 5. `load_nodes_config()` 适配

读取新格式，`ssh_host` 替代 `ssh_cmd` 和 `host`。

## 验收标准

- [ ] `grep -n "ssh_cmd" dispatch.py` 无结果
- [ ] `grep -n "gcloud" dispatch.py` 无结果
- [ ] `grep -n "identity_file" dispatch.py` 无结果
- [ ] `python3 -c "import dispatch; print('OK')"` 导入成功
- [ ] `ssh codex-node-1 "echo test"` 通过 run_ssh 正常执行
- [ ] `scp /tmp/test.txt codex-node-1:/tmp/test.txt` 通过 scp_to_remote 正常执行
- [ ] 本地执行路径 (mac1, codex-local) 不受影响
- [ ] 代码净减少 ≥40 行

## 不要做

- 不动 enrich_spec / build_enriched_spec 函数
- 不动 DAG 调度逻辑
- 不动数据库 schema 和操作
- 不动 collect / report 逻辑
- 不动 task-wrapper.sh
- 不加新依赖
- 不加重试逻辑（后续单独做）
- 不动 UI/CSS（无前端）
