# Auto Feedback Loop — 自动验证 + 自动修复

> 解决 ClawMarketing 的核心问题: 18 个 session 跑完了, 但 router 没注册、import 缺失、测试没跑。
> 目标: 执行完成 → 自动验证 → 自动修复 → 再验证 → 直到通过或人工介入

---

## 架构: 双模式反馈

### 模式 A: 实时 Fix (默认, 更快)

```
┌──────────────────────────────────────────────────────────┐
│                  dispatch.py 主循环                        │
│                                                            │
│  S01 完成 → 立即验证(语法/import) → 失败? → 生成 F-S01    │
│  S02 完成 → 立即验证 → 通过 ✓                              │
│  S03 完成 → 立即验证 → 失败? → 生成 F-S03                 │
│  ...                                                       │
│  F-S01 完成 → 再验证 S01 → 通过 ✓                          │
│  ...                                                       │
│  全部 S* + F-S* 完成                                       │
│  ↓                                                         │
│  Phase B: 收集 + 合并                                      │
│  Phase C: 全局集成验证 (S99 → Codex)                       │
│  Phase D: 如有问题, 集成修复 → 最多 2 轮                    │
│  Phase E: 生成 report                                      │
└──────────────────────────────────────────────────────────┘
```

**核心改进**: 不等所有任务完成再验证。每个 S* 完成后:
1. Controller 立即 SSH 读取 output/ 中的文件列表
2. 对 .py 文件做远程 ast.parse() 检查
3. 如果有语法/import 错误 → 自动生成 F-S<id> 修复 spec
4. F-S<id> 作为新任务加入 DB → 分配给同一个节点立即执行
5. 修复完后再验证 → 最多重试 2 次

**优势**: 修复和执行并行进行, 不浪费等待时间

### 模式 B: 批量 Fix (Fallback)

和原来一样: 全部完成 → 统一验证 → 统一修复 → 最多 3 轮。
当实时 fix 效果不好时切换到此模式。

---

## Phase B: 自动收集 + 合并

所有 S* 任务 completed 后, controller 自动:

```python
def collect_and_merge(project):
    """收集所有节点的 output/ 到本地合并目录"""
    merge_dir = f"~/Downloads/dispatch/{project}/merged"

    for task in get_completed_tasks(project):
        node = task.node
        remote_path = f"~/dispatch/{project}/tasks/{task.id}/output/"

        if node == "mac1":
            # 本地 cp
            shutil.copytree(remote_path, f"{merge_dir}/")
        else:
            # rsync 从远端拉
            subprocess.run(f"rsync -az {ssh(node)}:{remote_path} {merge_dir}/")

    return merge_dir
```

**合并策略**: 按任务 ID 顺序覆盖 (S01 先, S18 后)。如果文件冲突, 后者覆盖前者并记录 warning。

---

## Phase C: 自动验证

Controller 在合并目录运行一系列验证检查:

### 验证检查清单

```python
CHECKS = [
    # 1. 语法检查
    {
        "name": "python_syntax",
        "cmd": "find . -name '*.py' -exec python3 -c 'import ast; ast.parse(open(\"{}\").read())' \\;",
        "severity": "critical"
    },
    # 2. TypeScript 语法检查
    {
        "name": "typescript_syntax",
        "cmd": "npx tsc --noEmit 2>&1 || true",
        "severity": "high"
    },
    # 3. Import 完整性
    {
        "name": "python_imports",
        "cmd": "python3 -c 'import importlib; ...'",  # 检查所有 import 是否可解析
        "severity": "critical"
    },
    # 4. __init__.py 完整性
    {
        "name": "init_files",
        "description": "每个 Python package 目录都有 __init__.py",
        "severity": "high"
    },
    # 5. Router 注册 (项目特定)
    {
        "name": "router_registration",
        "description": "main.py 中注册了所有 router 文件",
        "severity": "critical"
    },
    # 6. 测试运行
    {
        "name": "pytest",
        "cmd": "cd backend && python3 -m pytest --tb=short 2>&1 | tail -50",
        "severity": "medium"
    },
]
```

### 验证执行方式

验证本身也是一个任务, dispatch 到一个节点执行:

```python
def run_verification(project, round_num):
    """生成验证 spec 并 dispatch"""
    verify_spec = generate_verify_spec(project, round_num)
    # 写入 specs/<project>/V01-verify.md
    # 作为普通任务加入 DB
    # 执行完成后解析 verify_report.json
    add_task(f"V{round_num:02d}", project, verify_spec)
```

验证 spec 模板:

```markdown
# V01: 自动验证

检查以下合并后的代码库: ~/dispatch/<project>/merged/

执行以下检查并输出 JSON 报告到 verify_report.json:

1. Python 语法: 对每个 .py 文件运行 ast.parse()
2. Import 检查: 检查所有 from X import Y 语句是否可解析
3. __init__.py 检查: 每个 Python 包目录是否有 __init__.py
4. Router 注册: main.py 是否 include_router 了所有 routers/*.py
5. 模型注册: models/__init__.py 是否 import 了所有 models/*.py
6. 测试运行: pytest --tb=short (收集结果, 允许失败)

输出格式:
{
  "passed": ["python_syntax", ...],
  "failed": [
    {"check": "router_registration", "details": "missing: organizations, users, ..."},
    {"check": "import_check", "details": "models/content_calendar.py not found"}
  ]
}
```

---

## Phase D: 自动修复

验证发现问题后, controller 自动生成修复 spec:

```python
def generate_fix_spec(project, verify_results, round_num):
    """根据验证结果自动生成修复 spec"""

    failed = verify_results["failed"]

    fix_instructions = []
    for issue in failed:
        if issue["check"] == "router_registration":
            fix_instructions.append(f"在 main.py 中添加缺失的 router: {issue['details']}")
        elif issue["check"] == "import_check":
            fix_instructions.append(f"修复缺失的 import: {issue['details']}")
        elif issue["check"] == "init_files":
            fix_instructions.append(f"创建缺失的 __init__.py: {issue['details']}")
        elif issue["check"] == "pytest":
            fix_instructions.append(f"修复失败的测试: {issue['details']}")

    spec = f"""# F{round_num:02d}: 自动修复

在 ~/dispatch/{project}/merged/ 目录中修复以下问题:

{chr(10).join(f'{i+1}. {inst}' for i, inst in enumerate(fix_instructions))}

修复后重新运行验证并输出 fix_report.json:
{{
  "fixed": ["router_registration", ...],
  "still_broken": [...],
  "new_issues": [...]
}}
"""
    return spec
```

修复 spec 作为新任务加入 DB (F01, F02...), dispatch 到一个节点执行。

---

## Phase E-F: 迭代验证+修复

```python
MAX_FEEDBACK_ROUNDS = 3

for round_num in range(1, MAX_FEEDBACK_ROUNDS + 1):
    # 验证
    verify_task_id = f"V{round_num:02d}"
    add_and_run_task(verify_task_id, verify_spec)
    verify_results = parse_verify_report(verify_task_id)

    if not verify_results["failed"]:
        log(f"Round {round_num}: ALL CHECKS PASSED")
        break

    log(f"Round {round_num}: {len(verify_results['failed'])} issues found")

    # 修复
    fix_spec = generate_fix_spec(project, verify_results, round_num)
    fix_task_id = f"F{round_num:02d}"
    add_and_run_task(fix_task_id, fix_spec)

    # 下一轮验证...

if round_num == MAX_FEEDBACK_ROUNDS and verify_results["failed"]:
    log(f"WARN: {len(verify_results['failed'])} issues remain after {MAX_FEEDBACK_ROUNDS} rounds")
    log("Flagging for human review")
    mark_needs_human_review(project)
```

---

## Phase G: 最终报告

```python
def generate_final_report(project):
    """生成包含 feedback loop 结果的最终报告"""

    report = f"""# {project} - Dispatch Report

## Summary
- Total tasks: {total}
- Completed: {completed}
- Failed: {failed}
- Duration: {total_duration}

## Feedback Loop
- Verification rounds: {num_rounds}
- Issues found (round 1): {r1_issues}
- Issues fixed automatically: {auto_fixed}
- Issues remaining: {remaining}

## Per-Task Details
| Task | Status | Node | Duration | Log Size |
|------|--------|------|----------|----------|
{task_rows}

## Verification History
{verify_history}

## Remaining Issues (if any)
{remaining_issues}
"""

    write_file(f"~/Downloads/dispatch/{project}-report.md", report)
```

---

## 整合到 dispatch.py 主循环

```python
def main_loop(project):
    # Phase A: 并行执行
    init_db(project)
    while has_pending_or_running(project):
        poll_and_dispatch(project)
        time.sleep(30)

    # Phase B: 收集合并
    merge_dir = collect_and_merge(project)

    # Phase C-F: 验证+修复循环
    for round_num in range(1, MAX_ROUNDS + 1):
        verify_result = run_verify(project, merge_dir, round_num)
        if verify_result.all_passed:
            break
        fix_result = run_fix(project, merge_dir, verify_result, round_num)

    # Phase G: 报告
    generate_report(project)
```

---

## 对 Opus 工作流的影响

```
之前: spec → 执行 → 手动验证 → 发现问题 → 手动修复 → 再验证 (5-8 轮 Opus)
之后: spec → dispatch.py start → [全自动] → 读 report.md (2 轮 Opus)
```

自动化掉的:
- 收集产物 (之前手动 rsync/scp)
- 合并代码 (之前手动 merge)
- 验证 (之前 Opus 逐文件审计)
- 修复常见问题 (router 注册、import 缺失、__init__.py)
- 跑测试 (之前手动 dispatch)

Opus 只需看 report.md 的 "Remaining Issues" 部分。

---

## 实现者

- **集成到 dispatch.py**: GLM (在 dispatch.py Phase A 完成后加入 Phase B-G)
- **验证 spec 模板**: GLM
- **测试**: Codex (模拟 3 轮反馈)
