---
task_id: S15-L4-test-rewrite
project: pipeline-v2
priority: 3
depends_on: [S11-L4a-api-qa, S12-L4b-browser-qa, S13-L4c-ui-review, S14-L4d-regression]
modifies: ["dispatch/pipeline/layers/L4_test.py"]
executor: glm
---

## 目标
重写 L4_test.py — 编排 L4a→L4b→L4c→L4d 四个子层，用 qa_standards.check_all() 汇总

## 约束
- **覆盖写** 现有 L4_test.py (完全替换)
- L4a/L4d 在任何节点可跑 (GCP/Mac)
- L4b/L4c 需要 Playwright，只在 Mac-2 跑 (检测 `platform.system() == "Darwin"`)
- 如果不在 Mac 环境，L4b/L4c 标记 skip 但不阻塞
- 使用 Layer 基类 (from layers.base import Layer, LayerResult)
- 所有函数用 kwargs

## 具体改动

### dispatch/pipeline/layers/L4_test.py (完全重写)

```python
#!/usr/bin/env python3
"""L4: 质检总控 — 编排 L4a/L4b/L4c/L4d"""
import json, platform, subprocess, sys
from pathlib import Path
from layers.base import Layer, LayerResult
sys.path.insert(0, str(Path(__file__).parent.parent))

class L4Test(Layer):
    name = "L4"
    max_retries = 1  # 测试不重试，失败交给 L5
    required_prev = ["L3"]

    SUB_LAYERS = ["L4a", "L4b", "L4c", "L4d"]

    def _is_mac(self) -> bool:
        return platform.system() == "Darwin"

    def _get_report_dir(self, *, project_name: str) -> Path:
        d = Path(__file__).parent.parent / "reports" / project_name
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _run_sublayer(self, *, sub: str, project_config, prev_results: dict, report_dir: Path) -> dict:
        """执行单个子层，返回子层 report dict"""
        # 根据 sub 调用对应的 L4x 模块
        # 传递 project_config 中的 path, backend, frontend, test_urls 等信息
        # 捕获异常返回 {"skipped": True, "reason": str(e)}
        pass

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")
        report_dir = self._get_report_dir(project_name=project_config.name)
        sub_results = {}

        # L4a: API 拜占庭 (任何节点)
        sub_results["L4a"] = self._run_sublayer(sub="L4a", project_config=project_config, prev_results=prev_results, report_dir=report_dir)

        # L4b: 浏览器 (Mac-2 only)
        if self._is_mac():
            sub_results["L4b"] = self._run_sublayer(sub="L4b", project_config=project_config, prev_results=prev_results, report_dir=report_dir)
        else:
            sub_results["L4b"] = {"skipped": True, "reason": "not Mac environment"}

        # L4c: UI 评审 (依赖 L4b, Mac-2 only)
        if self._is_mac() and not sub_results.get("L4b", {}).get("skipped"):
            sub_results["L4c"] = self._run_sublayer(sub="L4c", project_config=project_config, prev_results=prev_results, report_dir=report_dir)
        else:
            sub_results["L4c"] = {"skipped": True, "reason": "L4b skipped or not Mac"}

        # L4d: 回归测试 (任何节点)
        sub_results["L4d"] = self._run_sublayer(sub="L4d", project_config=project_config, prev_results=prev_results, report_dir=report_dir)

        # 汇总
        from qa_standards import check_all
        verdict = check_all(project=project_config.name, reports_dir=str(report_dir))

        # 合并 bug 列表
        all_bugs = []
        for sub_key, sub_report in sub_results.items():
            all_bugs.extend(sub_report.get("bugs", []))

        report = {
            "sub_results": sub_results,
            "verdict": verdict,
            "bugs": all_bugs,
            "bug_count": len(all_bugs),
            "s1_bugs": len([b for b in all_bugs if b.get("severity") == "S1"]),
            "s2_bugs": len([b for b in all_bugs if b.get("severity") == "S2"]),
        }

        # 保存总报告
        (report_dir / "L4-test-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

        if verdict.get("overall_pass"):
            result.finish("PASS", report=report)
        else:
            result.finish("FAIL", report=report, error=f"{report['bug_count']} bugs ({report['s1_bugs']} S1, {report['s2_bugs']} S2)")

        return result
```

## 验收标准
- [ ] L4Test 继承 Layer 基类，name="L4"
- [ ] L4a/L4d 在 GCP 节点正常执行
- [ ] L4b/L4c 在非 Mac 环境标记 skip 不崩溃
- [ ] qa_standards.check_all() 汇总正确
- [ ] L4-test-report.json 包含 sub_results + verdict + bugs
- [ ] `python3 -c "from layers.L4_test import L4Test; print(L4Test.name)"` 输出 L4

## 不要做
- 不要保留旧的 curl-only 测试逻辑
- 不要硬编码 Mac-2 hostname (用 platform.system())
- 不要修改 layers/base.py
- 不要修改其他层的代码
