# 🦪 Oyster Labs AI 集群搭建指南

> 本指南教你如何在 30 分钟内搭建自己的分布式 AI 开发集群

## 📋 前置要求

| 组件 | 要求 |
|------|------|
| **控制器 (Mac)** | 1 台 (安装 Python 3.10+, Node.js 18+) |
| **节点机器** | 1-10 台 Linux/Mac 服务器 |
| **网络** | 所有机器能访问互联网 |
| **API Key** | GLM / MiniMax / Claude API |

---

## 🏗️ 架构一览

```
控制器 (Mac-1)
    │
    ├── 调度: dispatch.py
    ├── 状态: SQLite (dispatch.db)
    │
    └── SSH → 节点集群 (GCP/AWS/Oracle/本地)
                  │
                  ├── codex-node-1 (8 槽)
                  ├── glm-node-2    (8 槽)
                  ├── glm-node-3    (8 槽)
                  └── oci-paid-1    (32 槽)
```

---

## Step 1: 初始化控制器 (Mac-1)

```bash
# 1. 创建工作目录
mkdir -p ~/Downloads/dispatch
cd ~/Downloads/dispatch

# 2. 安装依赖
pip3 install sqlite3 json os sys  # 内置模块，无需安装

# 3. 配置 SSH 免密登录到各节点
ssh-keygen -t ed25519 -C "oyster-controller"
ssh-copy-id your-node-ip
```

## Step 2: 配置节点信息

编辑 `nodes.json`:

```json
{
  "nodes": [
    {
      "name": "codex-node-1",
      "ssh_host": "codex-node-1",  // 或 IP 地址
      "slots": 8,
      "api_mode": "zai",           // zai/minimax/direct
      "executor": "glm",
      "priority": 1,
      "daemon": true,
      "socket_path": "/tmp/agent-daemon.sock"
    }
  ]
}
```

## Step 3: 在各节点安装 Agent

### 方式 A: 一键 Bootstrap (推荐)

```bash
# 在控制器上运行
curl -sL https://raw.githubusercontent.com/howardleegeek/oyster-ai-cluster/main/bootstrap.sh | \
  bash -s -- --name node-1 --slots 8 --mode glm
```

Bootstrap 会自动安装:
- Python 3
- Node.js 22
- Claude Code
- API Keys 配置

### 方式 B: 手动安装

```bash
# SSH 到节点
ssh user@your-node-ip

# 安装系统依赖
apt update && apt install -y git python3 python3-pip curl jq

# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 创建工作目录
mkdir -p ~/dispatch ~/agent-worker
```

## Step 4: 配置 API Keys

```bash
# 创建 key 目录
mkdir -p ~/.oyster-keys

# Z.ai (GLM) 配置
echo "your-zai-api-key" > ~/.oyster-keys/zai.key
chmod 600 ~/.oyster-keys/zai.key

# MiniMax 配置 (可选)
echo "your-minimax-api-key" > ~/.oyster-keys/minimax.key
chmod 600 ~/.oyster-keys/minimax.key
```

添加到 ~/.bashrc:

```bash
# Z.ai GLM
export ZAI_API_KEY=$(cat ~/.oyster-keys/zai.key)
export ZAI_BASE_URL=https://api.z.ai/api/paas/v4

# MiniMax
export MINIMAX_API_KEY=$(cat ~/.oyster-keys/minimax.key)

# Claude 别名
alias claude-glm='ANTHROPIC_AUTH_TOKEN=$ZAI_API_KEY ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic claude'
```

## Step 5: 验证节点连接

```bash
# 测试 SSH 连接
ssh your-node-ip "hostname && claude --version"

# 测试任务执行
ssh your-node-ip "cd ~/agent-worker && bash task-wrapper.sh test test-001 /tmp/test-spec.txt"
```

---

## 📖 使用方法

### 基本命令

```bash
# 查看集群状态
python3 dispatch.py status

# 启动项目任务
python3 dispatch.py start clawmarketing

# 查看项目详细状态
python3 dispatch.py status gem-platform

# 收集任务结果
python3 dispatch.py collect gem-platform

# 生成报告
python3 dispatch.py report gem-platform

# 停止项目
python3 dispatch.py stop gem-platform
```

### 输出示例

```
=== Task Status ===
  completed: 620
  pending: 890
  running: 69

=== Node Status ===
  codex-node-1: 8/8 slots used [✓]
  glm-node-2:   8/8 slots used [✓]
  glm-node-3:   8/8 slots used [✓]
  oci-paid-1:   32/32 slots used [✓]
```

---

## 🔧 扩展集群

### 添加新节点

1. 在新服务器运行 bootstrap.sh
2. 获取节点 IP
3. 添加到 nodes.json:

```json
{
  "name": "my-new-node",
  "ssh_host": "192.168.1.100",
  "slots": 8,
  "api_mode": "zai",
  "priority": 1
}
```

4. 重启调度器

### 支持的云服务商

| 服务商 | 类型 | 推荐配置 |
|--------|------|---------|
| **GCP** | Compute Engine | e2-standard-4 (4核8G) |
| **AWS** | EC2 | t3.large |
| **Oracle** | OCI | VM.Standard.A1.Flex |
| **本地** | Mac/Linux | 任意空闲机器 |

---

## 🐛 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| SSH 连接失败 | 密钥未配置 | 运行 ssh-copy-id |
| 节点显示 offline | 网络不通 | 检查防火墙/端口 |
| 任务一直 pending | 槽位已满 | 等待或添加节点 |
| API 报错 | Key 过期 | 更新 ~/.oyster-keys/ |

### 查看日志

```bash
# 调度器日志
tail -f dispatch.log

# 任务日志
cat ~/dispatch/<project>/tasks/<task-id>/task.log
```

---

## 📞 支持

- 开 Issue: https://github.com/howardleegeek/oyster-ai-cluster/issues
- 文档: ./docs/

---

**有问题随时提问! 🤝**
