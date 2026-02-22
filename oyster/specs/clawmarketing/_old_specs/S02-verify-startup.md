---
task_id: S02-verify-startup
project: clawmarketing
priority: 2
depends_on: [S01-fix-jwt]
modifies: []
executor: codex-node-1
---

## 目标
验证后端可本地启动

## 具体改动
1. cd ~/Downloads/clawmarketing/backend
2. python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
3. PYTHONPATH=.. JWT_SECRET=test_test_test_test .venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
4. sleep 5
5. curl http://localhost:8000/

## 验收标准
- [ ] curl 返回 {"status":"ok"}
