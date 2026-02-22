---
task_id: S36-git-integration
project: shell-vibe-ide
priority: 2
estimated_minutes: 40
depends_on: ["S25-project-management"]
modifies: ["web-ui/app/components/git/git-panel.tsx", "web-ui/app/components/git/diff-viewer.tsx", "web-ui/app/lib/git/git-operations.ts", "web-ui/app/lib/git/ai-commit-message.ts"]
executor: glm
---

## 目标

在 IDE 中集成 Git 操作，支持版本控制和 GitHub 同步。

## 开源方案

- **isomorphic-git**: github.com/nickvdyck/isomorphic-git (7.4k stars, MIT) — 浏览器端 Git
- **bolt.diy 已有 Git clone/import** — 直接复用

## 步骤

1. Git 面板:
   - 文件变更列表 (modified, added, deleted)
   - Diff 查看 (side-by-side 或 inline)
   - Stage / Unstage
   - Commit (输入消息)
   - Push / Pull
2. GitHub 集成:
   - 连接 GitHub 账户 (OAuth, S24 已有)
   - Clone 仓库
   - 创建新仓库
   - Push 到 GitHub
3. 分支管理:
   - 创建 / 切换 / 删除分支
   - 合并分支
4. AI Commit Message:
   - 分析 diff → AI 生成 commit 消息
   - 用户确认后提交
5. Desktop: 使用系统 git 命令
6. Web: 使用 isomorphic-git (浏览器内)

## 验收标准

- [ ] 文件变更列表显示
- [ ] Diff 查看
- [ ] Commit + Push 工作
- [ ] GitHub Clone 工作
- [ ] AI 生成 commit 消息
- [ ] 分支管理

## 不要做

- 不要自己实现 Git (用 isomorphic-git 或系统 git)
- 不要实现 Git 冲突解决 UI (用编辑器的 merge 视图)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
