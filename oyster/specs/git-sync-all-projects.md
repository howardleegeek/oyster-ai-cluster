# Spec: Git Sync All Projects to GitHub

## 任务
把 9 个项目全部整理并推送到 GitHub `howardleegeek` 账号，所有新 repo 设为 **private**。

## GitHub 账号
- `howardleegeek`
- GitHub token 在 `~/.oyster-keys/github.env` (已配好 `gh auth`)

## 分两类执行

### A. 已有 Git Repo (commit + push)

| 项目 | 路径 | Remote | 待提交 |
|------|------|--------|--------|
| twitter-poster | `~/Downloads/twitter-poster/` | howardleegeek/MCP | 6 modified + 13 untracked |
| openclaw-proxy | `~/Downloads/openclaw-proxy/` | howardleegeek/openclaw-proxy | 1 modified + 2 untracked |
| openclaw-mobile | `~/.openclaw/workspace/` | howardleegeek/openclaw-mobile | 1 modified + 9 untracked |

**步骤:**
1. `cd <dir>`
2. 检查 `.gitignore` — 确保排除: `.env`, `*.pyc`, `__pycache__/`, `node_modules/`, `.DS_Store`, `*.key`, `*.pem`
3. 如果 `.gitignore` 缺失或不完整，先创建/补充
4. `git add -A && git commit -m "sync: update all changes [automated]"`
5. `git push origin main` (或当前分支)

### B. 无 Git Repo (init + create + push)

| 项目 | 路径 | 建议 Repo 名 | 文件数 |
|------|------|-------------|--------|
| Oysterworld | `~/Downloads/claw-nation/` | `oysterworld` | 5 |
| Discord Admin | `~/Downloads/discord-admin/` | `discord-admin` | 32 |
| Article Pipeline | `~/Downloads/article_pipeline/` | `article-pipeline` | 9 |
| Oyster Org | `~/Downloads/oyster-org/` | `oyster-org` | 31 |
| Investor Materials | `~/Downloads/investor-materials-2026-02/` | `investor-materials` | 11 |
| Specs | `~/Downloads/specs/` | `oyster-specs` | 26+ |

**步骤:**
1. `cd <dir>`
2. 创建 `.gitignore`:
   ```
   .env
   *.pyc
   __pycache__/
   node_modules/
   .DS_Store
   *.key
   *.pem
   *.log
   .venv/
   ```
3. `git init && git add -A && git commit -m "initial commit"`
4. `gh repo create howardleegeek/<repo-name> --private --source=. --push`

## 安全检查 (每个项目都要做!)
- **扫描敏感文件**: 执行前 `grep -r "API_KEY\|SECRET\|PASSWORD\|sk-\|ghp_\|ANTHROPIC" --include="*.py" --include="*.js" --include="*.json" --include="*.env" .`
- 如果发现任何 secret/key，**不要 commit 该文件**，加入 `.gitignore`
- 特别注意: `accounts.json` (twitter-poster) 可能有 token — 检查后决定

## 验收标准
- [ ] 9 个项目全部有 GitHub remote
- [ ] 所有 repo 都是 private
- [ ] 没有 secret/key 被提交
- [ ] 每个 repo 有合理的 .gitignore
- [ ] `gh repo list howardleegeek --limit 20` 能看到所有 repo
