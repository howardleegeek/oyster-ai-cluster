---
task_id: S04-ai-social-network-post-creation
project: ai-social-network
priority: 2
depends_on: ["S01-ai-social-network-bootstrap"]
modifies: ["backend/posts.py", "backend/main.py", "tests/test_posts.py"]
executor: glm
---
## 目标
实现用户发布帖子的功能，包括文本内容和图片上传

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
