---
task_id: S17-infra-integration-test
project: dispatch-infra
priority: 2
depends_on: ["S10-infra-guardian", "S11-predictive-scheduling", "S12-code-self-audit", "S15-ghost-task-cleaner"]
modifies:
  - dispatch/tests/test_self_iterating.py
executor: glm
---

# Infra Integration Test: 自我迭代模块集成测试

## 目标
为所有自我迭代模块创建集成测试，确保它们能协同工作

## 具体改动

### 1. 新增测试文件
```python
# dispatch/tests/test_self_iterating.py

def test_guardian_smoke():
    """Guardian 能运行检查"""
    
def test_predictor_training():
    """Predictor 能训练模型"""
    
def test_auditor_scan():
    """Auditor 能扫描代码"""
    
def test_cleaner_detection():
    """Cleaner 能检测 ghost tasks"""
    
def test_full_loop():
    """完整循环: 检查 -> 分析 -> 修复 -> 验证"""
```

### 2. 测试场景
- Guardian: 检查 DB Schema、Wrapper 版本
- Predictor: 训练模型、预测耗时
- Auditor: 扫描代码、生成报告
- Cleaner: 检测并清理 ghost tasks

### 3. 断言
- 每个模块能独立运行
- 输出符合预期格式
- 错误处理正确

## 验收标准
- [ ] 4 个模块都有单元测试
- [ ] 集成测试覆盖完整流程
- [ ] 测试可重复执行
