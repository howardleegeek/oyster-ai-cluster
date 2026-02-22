---
task_id: U03
title: "一键启动 + 一键测试 (Makefile)"
depends_on: []
modifies: ["Makefile"]
executor: glm
---

## 目标
项目根目录加 Makefile，agent 自验证直接跑 `make test`。

## 学到的
文章要求：./run.sh dev 启动前后端，./run.sh test 运行所有测试。
我们的问题：每次验证临时拼命令，agent 不知道怎么跑测试。

## 改动
在每个项目根目录创建 Makefile：

```makefile
.PHONY: dev test test-backend test-frontend build lint clean

# 一键启动
dev:
	@echo "Starting backend + frontend..."
	JWT_SECRET=dev-secret uvicorn backend.main:app --reload --port 8000 &
	cd frontend && npm run dev &
	wait

# 一键测试（agent 验证用这个）
test: test-backend test-frontend
	@echo "✅ All tests passed"

test-backend:
	JWT_SECRET=test python -m pytest backend/tests/ -v --tb=short

test-frontend:
	cd frontend && npx vitest run

# 构建
build:
	cd frontend && npx vite build

# Lint
lint:
	cd backend && python -m black --check .
	cd frontend && npx eslint .

# 清理
clean:
	find . -name __pycache__ -exec rm -rf {} +
	rm -rf frontend/dist
```

## 对 task-wrapper.sh 的影响
task-wrapper.sh 已经检查 Makefile 存在就跑 `make test`。
加了 Makefile 后，这个检查自动生效。

## 验收标准
- [ ] make test 能跑
- [ ] make build 能跑
- [ ] task-wrapper.sh 在节点上能自动发现并执行 make test
