---
task_id: S99-final-acceptance
project: clawmarketing
priority: 99
depends_on: [S03-deploy]
modifies: []
executor: glm
---

## 你的角色
你是 ClawMarketing 的终局验收官。运行验收检查，输出 PASS/FAIL 报告。

## 终局验收标准

### A. 后端编译
- [ ] A1: `cd ~/Downloads/clawmarketing/backend && python3 -m py_compile main.py` 通过
- [ ] A2: 后端所有路由可正常 import

### B. 启动测试
- [ ] B1: 后端可启动 `uvicorn backend.main:app`
- [ ] B2: curl http://localhost:8000/ 返回 {"status":"ok"}

### C. 项目结构
- [ ] C1: 有 `backend/Dockerfile`
- [ ] C2: 有 `.env.example`

## 输出
创建 `CLAWMARKETING-FINAL-REPORT.md`
