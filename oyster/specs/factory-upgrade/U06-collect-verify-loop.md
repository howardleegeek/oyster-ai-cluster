---
task_id: U06
title: "collect 后自动 build + test 闭环验证"
depends_on: ["U03", "U05"]
modifies: ["dispatch/dispatch.py"]
executor: glm
---

## 目标
dispatch collect 拉回代码后，在 Mac-1 本地跑 build + test，不通过则标记任务为 failed。

## 学到的
文章要求：导入后再导出应保持等价（闭环验证）。
我们的问题：collect 拉回代码但不验证，合并了才发现 79 个 test fail。

## 改动

### dispatch.py collect 命令增加验证阶段

```python
def collect_and_verify(project):
    # 1. 拉回代码（已有）
    collect(project)

    # 2. 本地验证
    project_dir = get_project_dir(project)

    # 尝试跑 make test
    verify_cmd = None
    if os.path.exists(os.path.join(project_dir, 'Makefile')):
        verify_cmd = f"cd {project_dir} && make test"
    elif os.path.exists(os.path.join(project_dir, 'run.sh')):
        verify_cmd = f"cd {project_dir} && ./run.sh test"

    if verify_cmd:
        log(f"Running local verification: {verify_cmd}")
        result = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            log(f"❌ LOCAL VERIFICATION FAILED")
            log(f"stdout: {result.stdout[-500:]}")
            log(f"stderr: {result.stderr[-500:]}")
            # 标记为需要修复
            write_report(project, status="VERIFY_FAILED", details=result.stderr[-500:])
            return False
        else:
            log(f"✅ Local verification passed")
            write_report(project, status="VERIFIED")
            return True

    log("⚠️ No verification command found, skipping")
    return True
```

### report 命令显示验证状态
```
=== Project Report ===
Tasks: 17 completed, 0 failed
Local Verification: ✅ PASSED (make test: 191/191)
```

## 验收标准
- [ ] collect 后自动跑 make test
- [ ] 测试失败 → report 显示 VERIFY_FAILED
- [ ] 测试通过 → report 显示 VERIFIED
