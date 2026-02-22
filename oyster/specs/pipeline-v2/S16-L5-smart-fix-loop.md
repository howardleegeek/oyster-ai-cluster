---
task_id: S16-L5-smart-fix-loop
project: pipeline-v2
priority: 3
depends_on: [S15-L4-test-rewrite]
modifies: ["dispatch/pipeline/layers/L5_fix_loop.py"]
executor: glm
---

## 目标
实现智能修复循环: 5 轮迭代，bug 递减策略，只重跑失败的子层，对不同 bug 类型使用对应修复策略

## 约束
- 最多 5 轮迭代，第 5 轮必须收敛
- 每轮调用 skill_prompts.py 加载对应 skill 知识
- 使用 Layer 基类继承
- 所有函数用 kwargs
- 不动任何已有文件

## 具体改动

### dispatch/pipeline/layers/L5_fix_loop.py

```python
#!/usr/bin/env python3
"""L5: 智能修复循环 — 5 轮迭代，bug 递减"""
import json, subprocess, sys, time
from pathlib import Path
from layers.base import Layer, LayerResult
sys.path.insert(0, str(Path(__file__).parent.parent))

# 修复策略映射
FIX_STRATEGIES = {
    "S1_security": ["senior-security", "code-reviewer"],      # SQL注入/XSS/权限
    "S1_crash": ["systematic-debugging", "code-reviewer"],   # 崩溃/500错误
    "S2_ui": ["frontend-design", "component-refactoring"],   # UI/布局问题
    "S2_logic": ["code-reviewer", "TDD"],                     # 逻辑错误
    "S2_performance": ["performance-testing", "senior-qa"],  # 性能问题
}

MAX_ROUNDS = 5

class L5FixLoop(Layer):
    name = "L5"
    max_retries = 0  # 自己控制重试
    required_prev = ["L4"]

    def _classify_bugs(self, *, bugs: list) -> dict:
        """将 bug 分类到不同策略组"""
        classified = {"S1_security": [], "S1_crash": [], "S2_ui": [], "S2_logic": [], "S2_performance": []}
        for b in bugs:
            t = b.get("type", "")
            s = b.get("severity", "S2")
            if s == "S1":
                if t in ["sql_injection", "xss", "path_traversal", "auth"]:
                    classified["S1_security"].append(b)
                else:
                    classified["S1_crash"].append(b)
            else:
                if t in ["ui", "layout", "overflow", "css"]:
                    classified["S2_ui"].append(b)
                elif t in ["performance", "slow"]:
                    classified["S2_performance"].append(b)
                else:
                    classified["S2_logic"].append(b)
        return classified

    def _get_fix_strategy(self, *, bug_group: str) -> list:
        """获取对应 bug 组的修复 skill 列表"""
        return FIX_STRATEGIES.get(bug_group, ["code-reviewer"])

    def _build_fix_prompt(self, *, bugs: list, skills: list, project_config: dict, layer_context: str) -> str:
        """构建修复 prompt，包含 skill 知识"""
        from skill_prompts import load_skill
        skill_context = "\n---\n".join([load_skill(name=s) for s in skills if load_skill(name=s)])
        
        bug_desc = "\n".join([f"- {b.get('type')}: {b.get('detail', '')[:100]}" for b in bugs])
        
        return f"""你是修复专家。请根据以下 bug 列表进行修复。

## 技能知识
{skill_context}

## Bug 列表
{bug_desc}

## 项目信息
{json.dumps(project_config, indent=2)}

## 修复要求
1. 只修复列出的 bug，不要改其他代码
2. 修复后运行对应测试验证
3. 返回修复结果: {{"fixed": [bug_id], "remaining": [bug_id]}}
"""

    def _run_fix_round(self, *, bugs: list, project_config: dict, round_num: int, report_dir: Path) -> dict:
        """执行单轮修复"""
        if not bugs:
            return {"fixed": [], "remaining": [], "new_bugs": []}
        
        classified = self._classify_bugs(bugs=bugs)
        fixed = []
        remaining = []
        new_bugs = []
        
        for group, group_bugs in classified.items():
            if not group_bugs:
                continue
            
            skills = self._get_fix_strategy(bug_group=group)
            prompt = self._build_fix_prompt(
                bugs=group_bugs, 
                skills=skills, 
                project_config=project_config,
                layer_context=f"L5 round {round_num}"
            )
            
            # 调用 GLM/Claude 修复 (通过 dispatch 或直接 subprocess)
            # 这里需要集成 skill prompt
            result = self._call_fix_agent(prompt=prompt, project_dir=project_config.get("path"))
            
            fixed.extend(result.get("fixed", []))
            remaining.extend(result.get("remaining", []))
            new_bugs.extend(result.get("new_bugs", []))
        
        return {"fixed": fixed, "remaining": remaining, "new_bugs": new_bugs}

    def _call_fix_agent(self, *, prompt: str, project_dir: str) -> dict:
        """调用 agent 修复 (placeholder - 实际通过 dispatch 或 subprocess 调用)"""
        # 这里应该调用 claude-glm 或 dispatch 触发修复
        # 返回格式: {"fixed": [], "remaining": [], "new_bugs": []}
        pass

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")
        report_dir = Path(__file__).parent.parent / "reports" / project_config.name
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 从 L4 获取 bug 列表
        l4_report_path = report_dir / "L4-test-report.json"
        if not l4_report_path.exists():
            result.finish("SKIP", error="L4 report not found")
            return result
        
        l4_report = json.loads(l4_report_path.read_text())
        bugs = l4_report.get("bugs", [])
        
        if not bugs:
            result.finish("PASS", report={"rounds": 0, "message": "no bugs to fix"})
            return result
        
        # 5 轮迭代
        rounds = []
        current_bugs = bugs
        
        for round_num in range(1, MAX_ROUNDS + 1):
            round_result = self._run_fix_round(
                bugs=current_bugs, 
                project_config=project_config, 
                round_num=round_num,
                report_dir=report_dir
            )
            rounds.append(round_result)
            
            # 检查是否收敛
            remaining = round_result.get("remaining", [])
            new_bugs = round_result.get("new_bugs", [])
            
            current_bugs = remaining + new_bugs
            
            if len(current_bugs) == 0:
                break  # 所有 bug 修复
            
            # 检查是否发散 (bug 数量不减)
            if len(current_bugs) >= len(bugs) and round_num >= 3:
                # 连续 3 轮不收敛，标记需要人工介入
                break
        
        final_report = {
            "total_rounds": len(rounds),
            "rounds": rounds,
            "initial_bug_count": len(bugs),
            "final_bug_count": len(current_bugs),
            "converged": len(current_bugs) == 0,
            "needs_human": len(current_bugs) > 0 and len(rounds) >= MAX_ROUNDS,
        }
        
        (report_dir / "L5-fix-report.json").write_text(json.dumps(final_report, indent=2, ensure_ascii=False))
        
        if final_report["converged"]:
            result.finish("PASS", report=final_report)
        elif final_report["needs_human"]:
            result.finish("FAIL", report=final_report, error="需要人工介入")
        else:
            result.finish("FAIL", report=final_report, error=f"{len(current_bugs)} bugs remaining")
        
        return result
```

## 验收标准
- [ ] L5FixLoop 继承 Layer 基类，name="L5"
- [ ] 5 轮迭代，每轮调用 skill_prompts.load_skill() 获取知识
- [ ] bug 分类正确 (S1_security/S1_crash/S2_ui/S2_logic/S2_performance)
- [ ] bug 数量不增时继续，遇到发散时停止
- [ ] L5-fix-report.json 包含 rounds 数组和 converged 状态
- [ ] `python3 -c "from layers.L5_fix_loop import L5FixLoop; print(L5FixLoop.name)"` 输出 L5

## 不要做
- 不要超过 5 轮
- 不要忽略 bug 分类
- 不要修改 Layer 基类
- 不要修改其他层代码
