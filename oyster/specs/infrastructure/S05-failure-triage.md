---
task_id: S05-failure-triage
project: infrastructure
priority: 1
depends_on: []
modifies:
  - dispatch/failure_classifier.py
executor: glm
---

## 目标
创建失败分类器，自动识别失败原因

## 具体改动

### 创建文件: dispatch/failure_classifier.py

```python
#!/usr/bin/env python3
"""Failure classifier - auto-detect failure reasons"""

from typing import Optional, Dict, List

# Failure patterns
FAILURE_PATTERNS = {
    "deps": [
        "npm install failed",
        "pip install failed",
        "package not found",
        "ENOENT: no such file or directory",
        "ModuleNotFoundError",
        "ImportError",
    ],
    "auth": [
        "unauthorized",
        "permission denied",
        "API key",
        "401",
        "403",
        "invalid credentials",
    ],
    "test": [
        "AssertionError",
        "test failed",
        "pytest failed",
        "FAIL:",
        "Error: expect",
    ],
    "flaky": [
        "timeout",
        "connection reset",
        "ECONNRESET",
        "ETIMEDOUT",
        "network error",
    ],
    "infra": [
        "disk full",
        "memory error",
        "no such file",
        "ENOENT",
        "cannot allocate memory",
    ],
}

def classify_failure(error_output: str) -> str:
    """Classify failure type from error output"""
    error_lower = error_output.lower()
    
    for failure_type, patterns in FAILURE_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in error_lower:
                return failure_type
    
    return "unknown"

def get_failure_description(failure_type: str) -> str:
    """Get human-readable description"""
    descriptions = {
        "deps": "Dependency installation or import failed",
        "auth": "Authentication or authorization failed",
        "test": "Test assertion failed",
        "flaky": "Network or timing issue (may be flaky)",
        "infra": "Infrastructure issue (disk, memory, etc.)",
        "unknown": "Unknown failure reason",
    }
    return descriptions.get(failure_type, "Unknown")

def analyze_failure(error_output: str, stdout: str = "") -> Dict:
    """Full failure analysis"""
    combined = error_output + "\n" + stdout
    failure_type = classify_failure(combined)
    
    return {
        "type": failure_type,
        "description": get_failure_description(failure_type),
        "recommendation": get_recommendation(failure_type),
    }

def get_recommendation(failure_type: str) -> str:
    """Get fix recommendation"""
    recommendations = {
        "deps": "Check package.json/requirements.txt, run npm install/pip install",
        "auth": "Verify API keys and credentials in .env",
        "test": "Fix test assertions or update expected values",
        "flaky": "Retry the task, check network stability",
        "infra": "Check disk space, memory, restart node",
        "unknown": "Manual investigation needed",
    }
    return recommendations.get(failure_type, "Manual investigation needed")

if __name__ == "__main__":
    # Test
    test_errors = [
        "npm install failed: package not found",
        "Error: unauthorized - invalid API key",
        "AssertionError: expected 'foo' to equal 'bar'",
        "Error: ETIMEDOUT connection timeout",
    ]
    
    for err in test_errors:
        result = analyze_failure(err)
        print(f"Error: {err}")
        print(f"  Type: {result['type']}")
        print(f"  Description: {result['description']}")
        print(f"  Recommendation: {result['recommendation']}")
        print()
```

## 验收标准
- [ ] 模块可导入 `from failure_classifier import classify_failure`
- [ ] `classify_failure("npm install failed")` 返回 "deps"
- [ ] `classify_failure("unauthorized")` 返回 "auth"
- [ ] `analyze_failure()` 返回 type, description, recommendation

## 测试命令
```bash
cd ~/Downloads/dispatch
python3 -c "from failure_classifier import classify_failure; print(classify_failure('npm install failed'))"
```
