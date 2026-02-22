---
executor: glm
task_id: S99-code-quality-gate
project: dispatch
priority: 2
depends_on: [S99-code-queue-infra]
modifies:
  - pipeline/quality_gate.py
  - pipeline/qa_standards.py
---
executor: glm

## 目标
为 Code Pipeline 增加质量门禁，支持 lint + unit tests + 覆盖率检查。

## 约束
- 复用现有 pipeline/qa_standards.py 结构
- 支持 profile: "code" (新) vs "content" (现有)
- 失败自动回到 CODER 迭代（带日志）

## 具体改动

### pipeline/quality_gate.py (新文件)
```python
class CodeQualityGate:
    """代码质量门禁"""
    
    PROFILE_CODE = {
        "must_pass": ["lint", "unit_tests"],
        "require_test": True,
        "min_coverage": 80,
        "forbidden_patterns": ["TODO", "FIXME", "placeholder"],
        "risk_files": ["auth", "payment", "security"],
    }
    
    def check(self, workspace: str, profile: str = "code") -> GateResult:
        """执行质量检查"""
    
    def run_lint(self, workspace: str) -> LintResult:
        """运行 lint"""
    
    def run_tests(self, workspace: str) -> TestResult:
        """运行测试"""
    
    def check_coverage(self, workspace: str) -> CoverageResult:
        """检查覆盖率"""
```

## 验收标准
- [ ] lint 检查可运行
- [ ] unit tests 可运行
- [ ] 覆盖率检查可运行
- [ ] 门禁结果标准化

## 验证命令
```bash
cd ~/Downloads/dispatch && python3 -c "
from pipeline.quality_gate import CodeQualityGate
gate = CodeQualityGate()
result = gate.check('.')
print(result)
"
```
