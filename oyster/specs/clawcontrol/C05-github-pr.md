---
task_id: C05-github-pr
project: clawcontrol
priority: 1
depends_on: []
modifies:
  - pipeline/clawcontrol/services/github.py
---

## 目标
集成 GitHub API，实现自动创建 PR

## 约束
- 使用 GitHub REST API
- 支持 repo fork + branch
- 自动生成 PR body

## 具体改动
1. 创建 github.py 服务
2. 支持 fork repo
3. 支持 create branch
4. 支持 create PR
5. 支持 auto-merge

## 验收标准
- [ ] 可以 fork repo
- [ ] 可以创建 branch
- [ ] 可以创建 PR
- [ ] PR 包含 diff 和报告
