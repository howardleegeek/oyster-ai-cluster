---
task_id: S27-promptfoo-testing
project: dispatch-infra
priority: 2
depends_on: []
modifies:
  - dispatch/tests/prompts.yaml
executor: glm
---

# Promptfoo: Prompt 回归测试

## 目标
集成 Promptfoo 实现 prompt/agent behavior 回归测试

## 背景
- S17 integration test 已有
- 需要 prompt 级别的回归测试
- 防止 prompt 变更导致输出退化

## 具体改动

### 1. 新增 prompts.yaml (Promptfoo 配置)
```yaml
prompts:
  - id: guardian_check
    raw: |
      你是一个基础设施 Guardian。
      检查: {{check_type}}
      返回 JSON: {"status": "ok/warn/fail", "findings": []}

  - id: code_audit
    raw: |
      审计代码: {{file_path}}
      返回: {"issues": [{"severity": "high/medium/low", "line": N}]}

tests:
  - id: guardian_db_check
    prompt: guardian_check
    vars:
      check_type: "db_schema"
    assert:
      - json_equals:
          path: status
          value: "ok"

  - id: audit_simple_file
    prompt: code_audit
    vars:
      file_path: "dispatch/dispatch.py"
    assert:
      - type: is-json
      - json_schema_valid:
          schema:
            type: object
            properties:
              issues:
                type: array
```

### 2. 集成到 CI
```bash
# 在 PR 中运行
promptfoo eval --config dispatch/tests/prompts.yaml
promptfoo judge --config dispatch/tests/prompts.yaml
```

### 3. 与 S17 集成
- S17 运行后自动触发 promptfoo
- 失败阻止合并

## 验收标准

- [ ] 有 5+ 测试用例
- [ ] 能检测输出退化
- [ ] 能集成 CI

## 不做

- ❌ 不修改生产代码
