---
task_id: S29-team-collaboration
project: shell-vibe-ide
priority: 3
estimated_minutes: 50
depends_on: ["S24-user-auth", "S25-project-management"]
modifies: ["web-ui/app/lib/collaboration/yjs-provider.ts", "web-ui/app/components/collaboration/collaborators-panel.tsx", "web-ui/app/components/collaboration/comments.tsx", "web-ui/app/lib/collaboration/presence.ts"]
executor: glm
---

## 目标

添加团队协作功能：多人编辑、实时同步、评论。

## 开源方案

- **Yjs**: github.com/yjs/yjs (17k stars, MIT) — CRDT 实时协作框架
- **y-monaco**: Yjs 的 Monaco 编辑器绑定
- **Liveblocks**: 商业方案参考 (不用，用 Yjs)
- **Supabase Realtime**: 实时广播 + Presence

## 步骤

1. 安装: `pnpm add yjs y-monaco y-websocket`
2. 实时协作编辑:
   - Yjs + y-monaco → 多人同时编辑同一文件
   - 光标位置同步 (每个用户不同颜色)
   - 冲突自动解决 (CRDT)
3. 协作 WebSocket 服务:
   - 使用 `y-websocket` server
   - 或 Supabase Realtime channel
4. 项目分享:
   - 生成分享链接 (只读/可编辑)
   - 邀请成员 (通过钱包地址或 GitHub)
5. 评论系统:
   - 在代码行上添加评论
   - 评论线程 (回复)
   - 评论通知
6. Presence 显示:
   - 在线成员列表
   - 每个成员当前编辑的文件

## UI

```
┌─ Collaborators ─────────────┐
│ 🟢 Howard (editing main.rs) │
│ 🟢 Alice (editing test.rs)  │
│ 🟡 Bob (idle)               │
│                              │
│ [Invite] [Share Link]        │
└──────────────────────────────┘
```

## 验收标准

- [ ] 两个用户可以同时编辑同一文件
- [ ] 光标位置实时同步
- [ ] 在线成员列表显示
- [ ] 分享链接工作
- [ ] 代码行评论

## 不要做

- 不要自己实现 CRDT (用 Yjs)
- 不要实现视频通话
- 不要实现权限管理 (先只有 owner + editor 两种角色)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
