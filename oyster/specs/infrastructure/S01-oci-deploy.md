---
task_id: S01-oci-deploy
project: infrastructure
priority: 1
depends_on: []
modifies: []
executor: local
---

## 目标
在 3 台新 OCI 节点 (oci-paid-1, oci-paid-3, oci-arm-1) 上部署完整的基础设施

## 约束
- 只操作 OCI 节点，不动现有 GCP 节点
- 不修改 nodes.json 配置

## 具体改动

### 1. 创建 ~/bin/ 目录并上传文件

对 oci-paid-1, oci-paid-3, oci-arm-1 执行:
```bash
# 创建目录
ssh oci-paid-1 "mkdir -p ~/bin"
ssh oci-paid-3 "mkdir -p ~/bin"
ssh oci-arm-1 "mkdir -p ~/bin"

# 上传 mm
scp ~/Downloads/dispatch/agent-daemon.py oci-paid-1:~/bin/
scp ~/Downloads/dispatch/agent-daemon.py oci-paid-3:~/bin/
scp ~/Downloads/dispatch/agent-daemon.py oci-arm-1:~/bin/

# 上传 mm CLI (从 codex-node-1 复制)
ssh codex-node-1 "cat ~/bin/mm" > /tmp/mm_script
scp /tmp/mm_script oci-paid-1:~/bin/mm
scp /tmp/mm_script oci-paid-3:~/bin/mm
scp /tmp/mm_script oci-arm-1:~/bin/mm

# 上传 minimax.env
scp ~/.oyster-keys/minimax.env oci-paid-1:~/bin/minimax.env
scp ~/.oyster-keys/minimax.env oci-paid-3:~/bin/minimax.env
scp ~/.oyster-keys/minimax.env oci-arm-1:~/bin/minimax.env

# 设置权限
ssh oci-paid-1 "chmod +x ~/bin/mm ~/bin/agent-daemon.py"
ssh oci-paid-3 "chmod +x ~/bin/mm ~/bin/agent-daemon.py"
ssh oci-arm-1 "chmod +x ~/bin/mm ~/bin/agent-daemon.py"
```

### 2. 配置 SSH 免密登录

检查并确保本地 SSH key 可用:
```bash
# 如果没有 SSH key，先创建
# ssh-keygen -t ed25519 -C "howard@oysterlabs"

# 部署 SSH key 到各节点
ssh-copy-id oci-paid-1
ssh-copy-id oci-paid-3
ssh-copy-id oci-arm-1
```

### 3. 启动 agent-daemon

```bash
# 后台启动 daemon
ssh oci-paid-1 "nohup python3 ~/bin/agent-daemon.py > ~/agent-daemon.log 2>&1 &"
ssh oci-paid-3 "nohup python3 ~/bin/agent-daemon.py > ~/agent-daemon.log 2>&1 &"
ssh oci-arm-1 "nohup python3 ~/bin/agent-daemon.py > ~/agent-daemon.log 2>&1 &"

# 验证 daemon 运行
ssh oci-paid-1 "ps aux | grep agent-daemon | grep -v grep"
ssh oci-paid-3 "ps aux | grep agent-daemon | grep -v grep"
ssh oci-arm-1 "ps aux | grep agent-daemon | grep -v grep"
```

### 4. 验证 mm CLI

```bash
ssh oci-paid-1 "~/bin/mm 'hello'"
ssh oci-paid-3 "~/bin/mm 'hello'"
ssh oci-arm-1 "~/bin/mm 'hello'"
```

## 验收标准
- [ ] 3 台 OCI 节点 ~/bin/ 目录包含 mm, agent-daemon.py, minimax.env
- [ ] agent-daemon 进程运行中
- [ ] mm CLI 可执行并返回结果
- [ ] dispatch status 显示节点可用
