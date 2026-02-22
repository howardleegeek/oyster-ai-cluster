---
task_id: S07-TWITTER-AGENT-LOOP
project: clawmarketing
priority: 1
depends_on: [S04-PERSONA-ENGINE-TELOS, S05-MEMORY-ENGINE, S06-QUALITY-GATE-TELOS]
modifies:
  - backend/agents/twitter_agent.py
executor: glm
---

## 目标
重写 TwitterAgent.execute_engagement_reply() 实现完整闭环

##具体改动
1. 重写 execute_engagement_reply(task, db) 方法
2. 实现 7 步闭环:
   1. Load brand TELOS
   2. Load memory context (history + learnings)
   3. Generate reply with full context (TELOS + Memory)
   4. Quality gate check
   5. If fail: retry once with feedback
   6. If still fail: mark task failed
   7. If pass: post via CDP, record to Post table, mark completed

## 验收标准
- [ ] Agent 能从 task queue 拿任务
- [ ] 用 TELOS + Memory 生成回复
- [ ] Quality gate 检查
- [ ] 失败会 retry 一次
- [ ] 成功的帖子记录到 Post 表
- [ ] black backend/agents/twitter_agent.py 检查通过

## 不要做
- 不动其他文件
