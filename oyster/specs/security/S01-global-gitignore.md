---
task_id: SEC-004
project: security
priority: 1
depends_on: []
modifies: ["~/.gitignore_global"]
executor: glm
---

## 目标
创建全局 .gitignore 防止敏感文件被提交到任何 Git 仓库。

## 步骤
1. 创建 `~/.gitignore_global`，包含以下模式：
   - `*.key`, `*.pem`, `*.p12`, `*.pfx`
   - `.env`, `.env.local`, `.env.*.local`, `.env.production`
   - `credentials.json`, `*secret*`, `*credential*`
   - `*.sqlite`, `*.db` (防止 dispatch.db 等泄漏)
   - `.DS_Store`
2. 执行 `git config --global core.excludesFile ~/.gitignore_global`
3. 验证配置生效

## 验收标准
- [ ] `~/.gitignore_global` 存在
- [ ] `git config --global core.excludesFile` 返回 `~/.gitignore_global`
- [ ] 在任意 repo 下 `echo "test.key" > test.key && git status` 不显示 test.key

## 不要做
- 不修改任何项目级 .gitignore
- 不动现有代码或配置
