---
task_id: S01-fork-bolt-diy
project: shell-vibe-ide
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["package.json", "README.md"]
executor: glm
---

## 目标

Fork bolt.diy 到 howardleegeek/shell repo，替换现有 web-ui/ 目录。

## 背景

Shell 是一个 Web3 Vibe Coding IDE。我们 fork bolt.diy (https://github.com/stackblitz-labs/bolt.diy) 作为 UI 基座。

## 步骤

1. Clone bolt.diy 到本地
2. 删除现有 `web-ui/` 目录的内容
3. 将 bolt.diy 的源代码复制到 `web-ui/` 下
4. 更新 `web-ui/package.json`:
   - name: `"shell-web-ui"`
   - description: `"Shell - Web3 Vibe Coding IDE"`
5. 确保 `pnpm install && pnpm dev` 能正常启动
6. 更新 `web-ui/README.md` 说明这是 bolt.diy 的 fork

## 约束

- 不要修改 bolt.diy 的核心代码，只改 package.json 元数据
- 保留 bolt.diy 的 .gitignore
- 不要碰 desktop/ 目录
- 不要碰 runner/ 目录

## 验收标准

- [ ] `cd web-ui && pnpm install` 成功
- [ ] `cd web-ui && pnpm dev` 能启动开发服务器
- [ ] 浏览器打开 localhost 能看到 bolt.diy 界面
- [ ] package.json name 改为 shell-web-ui

## 不要做

- 不要改 bolt.diy 的任何功能代码
- 不要改主题 (S02 做)
- 不要改语言支持 (S03 做)
- 不要动 desktop/ 和 runner/
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
