## 任务: 修复 GCP 节点 GLM dispatch 权限问题

### 问题
`gcloud compute ssh <node> --command='claude -p "任务"'` 在 GCP 节点上执行失败。
原因: `claude -p` 写文件时需要权限确认，远程 SSH 无法交互。

### 两台 GCP 节点
- codex-node-1: `gcloud compute ssh codex-node-1 --zone=us-west1-b`
- glm-node-2: `gcloud compute ssh glm-node-2 --zone=us-west1-b`

### 解决方案 (两台都要做)

#### 方案 A: Claude Code settings 配置 (推荐)
```bash
# 在 GCP 节点上配置 claude settings，允许所有工具
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    "deny": []
  }
}
EOF
```

#### 方案 B: 每次 dispatch 加 flag
```bash
claude -p "任务" --dangerously-skip-permissions
```

#### 方案 C: 项目级 .claude/settings.json
```bash
# 在工作目录下创建
mkdir -p ~/clawphones/.claude
cat > ~/clawphones/.claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    "deny": []
  }
}
EOF
```

### 验证步骤
每台节点验证:
```bash
gcloud compute ssh <node> --zone=us-west1-b --command='cd ~/clawphones && claude -p "读 server.s11-6.js 的前 10 行，然后创建一个 /tmp/test-write.txt 写入 hello" --dangerously-skip-permissions && cat /tmp/test-write.txt'
```

### 额外配置
1. 确认 claude CLI 版本: `claude --version`
2. 确认 z.ai API key 已配置 (ANTHROPIC_AUTH_TOKEN)
3. 确认 ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
4. 配置别名: `alias claude-glm='claude --dangerously-skip-permissions'`
5. 写入 ~/.bashrc 永久生效

### 验收标准
- [ ] 两台 GCP 节点都能通过 SSH 远程 dispatch claude -p 任务
- [ ] 文件读写无需交互确认
- [ ] 创建 ~/clawphones/ 工作目录并解压代码包
