---
task_id: S24-pipeline-l4-test
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
Run Pipeline L4 API tests to verify the 17 S2 bugs are fixed.

## 约束
- Run existing pipeline L4 tests
- Do NOT modify test code
- Do NOT change API endpoints

## 具体改动
1. Start the backend server: cd backend && .venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
2. Wait 10 seconds for server to start
3. Run pipeline L4 tests: cd ~/Downloads/dispatch/pipeline && python3 run.py clawmarketing L4
4. Capture results and check for S2 bugs

## 验收标准
- [ ] Backend starts without errors
- [ ] L4 tests run
- [ ] Check if 17 S2 bugs are fixed

## 不要做
- Don't modify test code
- Don't change API routes
