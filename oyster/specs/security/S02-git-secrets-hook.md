---
task_id: SEC-005
project: security
priority: 2
depends_on: ["SEC-004"]
modifies: []
executor: glm
---

## 目标
安装 git-secrets pre-commit hook，在 commit 时自动检测私钥和 API key 泄漏。

## 步骤
1. 检查 `git-secrets` 是否安装：`which git-secrets`
   - 如未安装：`brew install git-secrets`
2. 注册全局检测模式：
   ```bash
   git secrets --register-aws --global
   git secrets --add --global '-----BEGIN .* PRIVATE KEY-----'
   git secrets --add --global 'sk-[a-zA-Z0-9]{20,}'
   git secrets --add --global 'nvapi-[a-zA-Z0-9]{20,}'
   git secrets --add --global 'GOCSPX-[a-zA-Z0-9]+'
   ```
3. 为 `~/Downloads/` 下所有 git repo 安装 hook：
   ```bash
   for repo in ~/Downloads/*/.git; do
     [ -d "$repo" ] && (cd "$repo/.." && git secrets --install -f 2>/dev/null || true)
   done
   ```
4. 测试：在某个 repo 里尝试 commit 一个包含 `sk-xxxxxxxxxxxxxxxxxxxxxxxx` 的文件，确认被拦截

## 验收标准
- [ ] `git secrets --list --global` 显示注册的模式
- [ ] `~/Downloads/clawmarketing/.git/hooks/pre-commit` 存在
- [ ] 尝试 commit 包含假 API key 的文件时被阻止

## 不要做
- 不修改现有 .git/hooks 中已有的自定义 hook（追加而非覆盖）
- 不动任何源代码
