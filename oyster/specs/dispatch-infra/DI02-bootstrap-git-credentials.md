---
task_id: DI02-bootstrap-git-credentials
project: dispatch-infra
priority: 0
estimated_minutes: 25
depends_on: []
modifies: ["bootstrap.sh"]
executor: glm
---
## 目标
在 bootstrap.sh 中添加 git credentials 自动部署，确保新节点可以 clone 私有 GitHub repo

## 技术方案
在 bootstrap.sh 的节点初始化流程中添加：

1. **Git identity 配置**:
```bash
git config --global user.name "Oyster AI Agent"
git config --global user.email "ai@oysterlabs.com"
git config --global credential.helper store
```

2. **Git credentials 部署** — 从 controller 节点拷贝：
```bash
# Copy git credentials from controller
CONTROLLER_HOST="${CONTROLLER_HOST:-100.91.32.29}"  # mac1 Tailscale IP
scp ${CONTROLLER_HOST}:~/.git-credentials ~/.git-credentials 2>/dev/null || {
    echo "WARNING: Could not copy git credentials. Git mode projects will fail."
    echo "Manual fix: scp controller:~/.git-credentials ~/.git-credentials"
}
chmod 600 ~/.git-credentials
```

3. **验证 git auth**:
```bash
git ls-remote https://github.com/howardleegeek/agentforge.git HEAD >/dev/null 2>&1 && \
    echo "✓ Git auth OK" || echo "✗ Git auth FAILED"
```

## 约束
- 修改现有 bootstrap.sh，在已有的 "Setup git" 段落后添加
- 不硬编码 GitHub token（从 controller 拷贝）
- 失败时只 warn 不 exit（非致命错误）
- 不改 bootstrap.sh 的其他功能

## 验收标准
- [ ] 新节点 bootstrap 后自动有 ~/.git-credentials
- [ ] git config --global credential.helper 为 store
- [ ] git config --global user.name 为 "Oyster AI Agent"
- [ ] 可以 git clone 私有 repo

## 不要做
- 不硬编码 GitHub token
- 不改 SSH 配置
- 不改 systemd 服务
