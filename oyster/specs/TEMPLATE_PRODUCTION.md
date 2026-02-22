---
task_id: S##-<module>-<feature>
project: <project>
priority: 1
depends_on: []
modifies:
  - path/to/file.py
executor: glm
---

## 目标
[一句话描述功能]

## 约束
- 边界：不动哪些模块
- 安全：不硬编码 secret
- 不重构现有代码

## 具体改动
1. [功能点 1]
2. [功能点 2]
3. [功能点 3]

## 生产级要求

### 测试要求 (必须)
```bash
# 1. 单元测试覆盖率 > 70%
pytest tests/unit/ --cov=src --cov-report=html

# 2. 集成测试
pytest tests/integration/ -v

# 3. 拜占庭测试 (异常场景)
pytest tests/byzantine/ -v
# 覆盖: 空输入/超时/并发/权限/越权

# 4. E2E 测试 (如适用)
playwright test tests/e2e/
```

### 代码质量 (必须)
```bash
# Python
black --check . && mypy . && pytest

# JavaScript/TypeScript
eslint . && tsc --noEmit && vitest run
```

### 验收标准
- [ ] 单元测试覆盖率 > 70%
- [ ] 拜占庭测试全部通过
- [ ] 集成测试通过
- [ ] black/mypy 通过
- [ ] eslint 通过
- [ ] 部署验证通过

### 监控要求 (生产级)
- [ ] 日志结构化 (JSON)
- [ ] 关键指标上报
- [ ] 错误告警配置

### 安全要求
- [ ] 无硬编码 secret
- [ ] API 鉴权检查
- [ ] 输入验证

## 不要做
- [不碰的文件]
- [禁止 TODO/FIXME 交付]
