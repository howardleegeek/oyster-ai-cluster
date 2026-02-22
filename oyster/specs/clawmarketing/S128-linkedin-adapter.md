---
task_id: S128-linkedin-adapter
project: clawmarketing
priority: 2
depends_on: []
modifies: ["backend/services/linkedin_content_adapter.py"]
executor: glm
---
## 目标
实现 LinkedIn 内容适配器，将通用内容转换为 LinkedIn 专业格式

## 约束
- LinkedIn 帖子最长 3000 字符
- 自动添加专业格式（段落、项目符号）
- 保留核心信息、添加 CTA
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_linkedin_content_adapter.py 全绿
- [ ] ContentAdapter.adapt() 正确转换内容
- [ ] 字符数限制在 3000 以内
- [ ] 保持专业语气

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
