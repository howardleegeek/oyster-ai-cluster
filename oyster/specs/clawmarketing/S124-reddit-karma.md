---
task_id: S124-reddit-karma
project: clawmarketing
priority: 2
depends_on: ["S120-reddit-client", "S121-reddit-posting"]
modifies: ["backend/clients/reddit_client.py", "backend/agents/reviewer_agent.py"]
executor: glm
---
## 目标
实现 Karma 管理和账户健康检查

## 约束
- 新增: get_karma(), get_account_info(), analyze_karma_trend(days=7), get_karma_health_score()
- 健康分数 0-100
- 集成到 Reviewer Agent
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_reddit_karma.py 全绿
- [ ] get_karma 返回详细分类
- [ ] get_karma_health_score 返回 0-100
- [ ] Reviewer Agent 可调用所有方法

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
