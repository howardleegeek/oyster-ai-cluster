# GCP Codex Execution Node Setup

## 任务
在 GCP us-west1 创建 e2-standard-4 VM，安装 Codex CLI，配置为远程执行节点。

## 前提
- gcloud CLI 已安装且认证完成
- gcloud 项目已设置

## 步骤

### 1. 创建 VM
```bash
gcloud compute instances create codex-node-1 \
  --zone=us-west1-b \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --tags=codex-node \
  --metadata=startup-script='#!/bin/bash
apt-get update && apt-get install -y curl git nodejs npm'
```

### 2. SSH 进去安装 Codex
```bash
gcloud compute ssh codex-node-1 --zone=us-west1-b
```

在 VM 内执行:
```bash
# 安装 Node.js 22 (Codex 需要)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 Codex CLI
npm install -g @openai/codex

# 验证
codex --version
```

### 3. 配置 SSH 免密登录
生成 SSH config 条目，方便 Mac-1 直接 `ssh codex-node-1` 连接。

### 4. 测试 Codex 执行
```bash
codex exec --full-auto "echo hello from GCP codex node"
```

## 验收标准
- [ ] VM 创建成功，能 SSH 连接
- [ ] Codex CLI 安装完成，`codex --version` 返回版本号
- [ ] 从 Mac-1 可以 `gcloud compute ssh codex-node-1` 免密连接
- [ ] Codex exec 测试命令成功执行

## 注意
- VM 用 Ubuntu 24.04 LTS
- 50GB 磁盘应该够用（代码不大）
- Codex auth login 需要交互式完成，不能在 startup-script 里做
- 不要装不必要的东西，保持干净
