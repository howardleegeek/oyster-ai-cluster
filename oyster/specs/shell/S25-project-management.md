---
task_id: S25-project-management
project: shell-vibe-ide
priority: 2
estimated_minutes: 50
depends_on: ["S24-user-auth"]
modifies: ["web-ui/app/components/projects/project-list.tsx", "web-ui/app/components/projects/project-card.tsx", "web-ui/app/lib/supabase/projects.ts", "web-ui/app/stores/project-store.ts"]
executor: glm
---

## 目标

添加项目管理功能：创建、保存、列表、切换项目。

## 开源方案

- **Supabase**: github.com/supabase/supabase (77k stars) — 数据库 + 存储 + Auth
- bolt.diy 已有 Supabase 集成 — 直接复用

## 步骤

1. 项目数据模型:
   ```sql
   projects (
     id uuid primary key,
     user_id uuid references users(id),
     name text,
     chain 'svm' | 'evm' | 'move',
     description text,
     files jsonb,
     created_at timestamp,
     updated_at timestamp,
     is_public boolean default false
   )
   ```
2. 项目 CRUD:
   - 创建: 从模板或空白
   - 保存: 自动保存 + 手动保存 (Ctrl+S)
   - 列表: 我的项目页面
   - 删除: 确认后删除
3. 文件存储:
   - Supabase Storage (大文件)
   - JSONB (小项目直接存 files 字段)
4. UI:
   - 项目列表页 (网格卡片)
   - 每个卡片: 名称 + 链 + 最后修改时间 + 状态
   - "New Project" 按钮 → 模板画廊 (S16)
5. Git 集成:
   - 连 GitHub 后可以 push/pull
   - 每个项目 = 一个 repo (可选)

## 验收标准

- [ ] 创建新项目成功
- [ ] 项目自动保存
- [ ] 项目列表页显示所有项目
- [ ] 可以切换项目
- [ ] 项目数据持久化到 Supabase

## 不要做

- 不要自己搭数据库 (用 Supabase)
- 不要实现版本控制 (用 Git)
- 不要实现协作 (S29 做)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
