---
task_id: S01-contentforge-bootstrap
project: contentforge
priority: 1
depends_on: []
modifies: ["backend/main.py", "backend/config.py"]
executor: glm
---
## 目标
Bootstrap contentforge project: 基于本地LLM的AI社交媒体内容工厂，支持批量生成+多平台发布+数据分析

## 约束
- 技术栈: Python FastAPI + HTML/CSS/JS
- 实现核心功能的骨架代码
- 写基础测试

## 验收标准
- [ ] 核心模块有基础实现
- [ ] pytest 能跑通
- [ ] 不留 TODO/FIXME

## 不要做
- 不留 placeholder
- 不做 UI 相关
