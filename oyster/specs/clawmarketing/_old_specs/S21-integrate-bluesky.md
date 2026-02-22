---
task_id: S21-integrate-bluesky
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
Integrate existing bluesky-poster module into ClawMarketing as a new agent.

## 约束
- bluesky-poster project is at ~/Downloads/bluesky-poster/
- The source files are in ~/Downloads/bluesky-poster/bluesky/ (client.py, queue.py, worker.py, rate_limiter.py, scheduler.py, analytics.py, feed_discovery.py)
- Create new agent in backend/agents/bluesky_agent.py
- Add API endpoints for bluesky posting
- Do NOT change frontend UI

## 具体改动
1. First, sync bluesky-poster to the node:
   - Run: rsync -avz ~/Downloads/bluesky-poster/ oci-paid-1:/home/ubuntu/bluesky-poster/
   - Or verify: ls ~/Downloads/bluesky-poster/bluesky/ to see client.py, queue.py, worker.py, rate_limiter.py, scheduler.py, analytics.py, feed_discovery.py
   
2. Copy/reference bluesky-poster modules into ClawMarketing backend:
   - client.py → backend/agents/bluesky/
   - queue.py → backend/agents/bluesky/
   - worker.py → backend/agents/bluesky/
   - rate_limiter.py → backend/agents/bluesky/
   - scheduler.py → backend/agents/bluesky/
   
2. Create backend/agents/bluesky_agent.py with:
   - BlueskyAgent class
   - post() method
   - schedule_post() method
   - get_status() method
   
3. Add API routes in backend/routers/bluesky.py:
   - POST /api/v1/bluesky/post
   - POST /api/v1/bluesky/schedule
   - GET /api/v1/bluesky/status
   
4. Register bluesky router in backend/main.py

## 验收标准
- [ ] bluesky_agent.py exists with working class
- [ ] /api/v1/bluesky/post endpoint returns 200
- [ ] bluesky router registered in main.py
- [ ] Unit tests pass

## 不要做
- Don't modify existing Twitter/Discord agents
- Don't touch frontend
- Don't add new database tables (reuse existing)
