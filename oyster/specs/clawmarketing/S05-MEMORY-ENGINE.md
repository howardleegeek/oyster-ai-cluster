---
task_id: S05-MEMORY-ENGINE
project: clawmarketing
priority: 1
depends_on: [S02-BRAND-TELOS-MODEL]
modifies:
  - backend/services/memory_engine.py
executor: glm
---

## 目标
实现 Brand Memory Engine - 三层记忆系统

## 具体改动
1. 新建 backend/services/memory_engine.py
2. 实现 MemoryEngine 类:
   - get_recent_history(brand_id, limit=20): 热记忆 - 最近帖子效果
   - extract_learnings(brand_id): 温记忆 - 从历史提取规律
   - build_memory_context(history, learnings): 构建注入 prompt 的上下文
3. learnings 结构:
   - best_content_type
   - avg_engagement_by_type
   - top_posts_summary
   - total_posts_analyzed
4. learnings 存储在 brand.telos._learnings

## 验收标准
- [ ] get_recent_history 返回最近帖子列表
- [ ] extract_learnings 能分析 best_content_type
- [ ] build_memory_context 能构建可读上下文
- [ ] black backend/services/memory_engine.py 检查通过

## 不要做
- 不动其他文件
