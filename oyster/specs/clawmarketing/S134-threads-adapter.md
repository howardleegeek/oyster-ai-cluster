---
task_id: S134-threads-adapter
project: clawmarketing
priority: 2
depends_on: ["S133-threads-client"]
modifies: ["backend/adapters/threads_adapter.py"]
executor: glm
---
## 目标
实现 Threads 内容适配器，500字符限制 + 图片支持

## 约束
- 500字符限制
- 支持图片/视频 attachments
- Hashtag 提取
- Graph API payload 格式
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_threads_adapter.py 全绿
- [ ] adapt_post() 正确处理超长内容
- [ ] adapt_media() 处理图片/视频
- [ ] extract_hashtags() 提取标签

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
