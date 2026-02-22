---
task_id: S01-backend-template
project: backend
priority: 1
depends_on: []
modifies:
  - ~/Downloads/backend
executor: glm
---

## 目标
将 FastAPI 生产级模板应用到 backend 项目

## 约束
- 不修改其他项目文件
- 使用 MIT 许可证的开源模板
- 保持目录结构清晰

## 具体改动

### 1. 调研并选择模板
从以下候选模板中选择最适合的：
- fastapi-large-app-template: https://github.com/akhil2308/fastapi-large-app-template (JWT, Rate Limiting, Async PostgreSQL/Redis)
- bybatkhuu/rest-fastapi-template: https://github.com/bybatkhuu/rest.fastapi-template (Docker, CI/CD)

### 2. 应用模板到 backend 目录
克隆或复制选定的模板到 ~/Downloads/backend，覆盖现有空目录结构

### 3. 保留项目元文件
保留原有的 CLAUDE.md 文件（在根目录和各子目录）

### 4. 初始化 git（如果需要）
确保 backend 目录有 git 仓库以便版本控制

## 验收标准
- [ ] backend 目录包含完整的 FastAPI 应用结构
- [ ] 包含 main.py, app/ 目录, requirements.txt 等核心文件
- [ ] 可以运行 `python -m py_compile` 验证语法
- [ ] README.md 存在并说明如何启动

## 验证命令
```bash
ls -la ~/Downloads/backend
python -m py_compile ~/Downloads/backend/*.py 2>/dev/null || echo "No py files in root"
```

## 不要做
- 不提交任何 secrets 或 .env 到 git
- 不修改 frontend 项目
