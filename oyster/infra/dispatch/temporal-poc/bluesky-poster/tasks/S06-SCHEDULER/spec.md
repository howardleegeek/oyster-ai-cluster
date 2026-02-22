## 目标
实现定时批量发布功能，支持草稿管理和排程发布

## 约束
- 本地 SQLite 存储草稿和排程
- 不使用第三方调度服务
- 最多提前 7 天排程

## 具体改动

### bluesky/scheduler.py
新增调度器模块：
1. `Scheduler` 类
2. `add_draft(text, images?)` - 添加草稿
3. `schedule_draft(draft_id, post_time)` - 排程草稿
4. `list_drafts()` - 列出所有草稿
5. `list_scheduled()` - 列出已排程
6. `publish_draft(draft_id)` - 立即发布草稿
7. `delete_draft(draft_id)` - 删除草稿
8. `get_due_posts()` - 获取待发布的排程

### bluesky/__main__.py
新增 CLI 命令：
- `draft add <text>` - 添加草稿
- `draft list` - 列出草稿
- `draft publish <id>` - 立即发布
- `draft delete <id>` - 删除草稿
- `schedule <draft_id> <datetime>` - 排程发布
- `schedule list` - 列出排程

## 验收标准
- [ ] 文件 bluesky/scheduler.py 存在且包含 `class Scheduler` 定义
- [ ] 文件 bluesky/__main__.py 包含 `draft` 子命令
- [ ] 验证命令 `python bluesky_poster.py draft add "test"` 成功添加草稿
- [ ] 验证命令 `python bluesky_poster.py draft list` 返回草稿列表

## 验证命令 (必须执行)
```bash
cd /home/ubuntu/dispatch/bluesky-poster
python3 bluesky_poster.py draft add "验证测试" 2>&1 | grep -i "draft" || echo "FAIL"
python3 bluesky_poster.py draft list 2>&1 | grep -i "draft" || echo "FAIL"
```

## 不要做
- 不改已有功能
- 不做自动发帖（只手动触发）