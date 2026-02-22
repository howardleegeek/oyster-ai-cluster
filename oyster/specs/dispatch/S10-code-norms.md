---
task_id: S10-code-norms
project: dispatch
priority: 1
depends_on: []
modifies: ["CLAUDE.md"]
executor: local
---

# S10: 代码规范与模块化检查清单

## 背景
并发 spec 执行时，多个 GLM agent 同时改代码，容易出现：
- 代码风格不一致
- 模块边界模糊
- 缺少测试

## 代码规范要求

### 1. 模块化检查
- [ ] 新代码必须在已有模块内添加，不是新建文件
- [ ] 如果新建文件 > 3 个，必须说明理由
- [ ] 改动必须符合项目现有架构

### 2. 代码风格
- [ ] Python: Black 格式化
- [ ] JS/TS: ESLint 检查
- [ ] 无 unused imports/variables

### 3. 测试要求
- [ ] 改动必须有对应测试
- [ ] 测试必须能跑通 (`pytest` 或 `npm test`)

### 4. 不要做
- [ ] 不重构现有代码（只修 bug）
- [ ] 不改 UI/样式（除非 spec 明确要求）
- [ ] 不加新依赖（除非 spec 批准）

## 验证方式
```bash
# Python
black --check .
pytest

# JS/TS
eslint .
npm test
```

## 模板更新
更新 spec 模板，加入规范要求。
