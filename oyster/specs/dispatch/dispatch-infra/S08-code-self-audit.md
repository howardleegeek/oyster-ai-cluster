---
task_id: S12-code-self-audit
project: dispatch
priority: 2
depends_on: []
modifies:
  - dispatch/code_auditor.py
  - dispatch/audit_config.json
executor: glm
---

# Code Self-Audit: 代码自审计

## 目标
定期自动 review Infra 自己写的代码，找 bug、提优化建议、记录技术债务

## 约束
- 只读分析，不修改代码
- 生成报告，不强制执行建议
- 使用 MiniMax + 静态分析工具

## 背景
Infra 每天在跑任务、生成代码，但没有人检查代码质量。时间久了会有：
- 重复代码
- 未处理的异常
- 过时的依赖
- 安全漏洞

## 具体改动

### 1. 新增 code_auditor.py
```python
class CodeAuditor:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir
        self.issues = []
    
    def scan(self):
        """扫描所有代码文件"""
        # 1. 静态分析 (AST)
        # 2. 复杂度检查
        # 3. 安全扫描
        # 4. 依赖检查
    
    def analyze_with_minimax(self, code: str) -> dict:
        """用 MiniMax 分析代码质量问题"""
        prompt = f"""
        Review this Python code for:
        1. Bug potential
        2. Security issues
        3. Code smells
        4. Performance issues
        
        Code:
        {code}
        """
    
    def generate_report(self) -> dict:
        """生成审计报告"""
```

### 2. 检查项

| 检查项 | 工具 | 严重度 |
|--------|------|--------|
| 代码复杂度 | radon / lizard | 中 |
| 未处理异常 | AST 分析 | 高 |
| 硬编码 secrets | regex | 高 |
| 重复代码 | dupl | 中 |
| 过期依赖 | pip-audit | 高 |
| 安全漏洞 | bandit | 高 |
| 代码风格 | pylint | 低 |

### 3. 审计报告格式
```json
{
  "timestamp": "2026-02-14T12:00:00Z",
  "files_scanned": 50,
  "issues": [
    {
      "file": "dispatch/executor.py",
      "line": 42,
      "issue": "硬编码 API key",
      "severity": "high",
      "suggestion": "使用环境变量"
    }
  ],
  "metrics": {
    "total_lines": 5000,
    "complexity_avg": 8.5,
    "tech_debt_hours": 24
  }
}
```

### 4. 定时执行
```python
# 每周日凌晨 3 点执行
cron = "0 3 * * 0"
# 或通过 launchd
```

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `dispatch/code_auditor.py` | 新建 | 审计引擎 (~400行) |
| `dispatch/audit_config.json` | 新建 | 扫描配置 |
| `dispatch/audit_reports/` | 新建 | 报告目录 |

## audit_config.json

```json
{
  "target_dirs": [
    "~/Downloads/dispatch/",
    "~/Downloads/agent-sdk/src/"
  ],
  "exclude_patterns": [
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/venv/**"
  ],
  "severity_threshold": "medium",
  "tools": {
    "complexity": true,
    "security": true,
    "duplication": true,
    "dependencies": true
  },
  "schedule": "0 3 * * 0",
  "report_dir": "~/Downloads/dispatch/audit_reports/",
  "minimax_enabled": true
}
```

## 验收标准

- [ ] 能扫描指定目录的所有代码文件
- [ ] 能检测高严重度问题 (bug、安全漏洞)
- [ ] 能用 MiniMax 生成改进建议
- [ ] 报告能保存到文件
- [ ] 能设置定时执行

## 测试命令
```bash
cd ~/Downloads/dispatch
python3 -m pytest tests/test_code_auditor.py -v
```

## 不要做

- 不修改任何源代码
- 不删除文件
- 不提交 git
- 不执行任何代码
