#!/usr/bin/env python3
"""
Spec 碰撞系统 v2 - 基于 LLaMEA 思想 - 完整版

核心机制：
- Fitness-guided: 用测试结果指导生成
- 迭代进化: 上一轮结果→下一轮种子
- Dispatch 集成: 真正调度到集群执行
- 真实测试: fitness = 测试通过率
"""

import sys
import os
import json
import argparse
import subprocess
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# ============== 配置 ==============
MAX_GENERATIONS = 20
POPULATION_SIZE = 5
MUTATION_RATE = 0.4
CROSSOVER_RATE = 0.3
MAX_TOKENS = 16384
TEMPERATURE = 0.7
DISPATCH_TIMEOUT = 600  # 10 分钟超时

# ============== 强验收标准权重 ==============
# pytest 全绿 (50%) + black/flake8 (20%) + mypy (20%) + 集成测试 (10%)
WEIGHT_PYTEST = 0.50
WEIGHT_LINT = 0.20
WEIGHT_MYPY = 0.20
WEIGHT_INTEGRATION = 0.10


class FitnessLevel(Enum):
    EXCELLENT = 1.0
    GOOD = 0.8
    PARTIAL = 0.5
    POOR = 0.2
    FAILED = 0.0


@dataclass
class SpecIndividual:
    id: str
    spec_content: str
    fitness: float = 0.0
    test_passed: int = 0
    test_total: int = 0
    error_msg: str = ""
    parent_ids: List[str] = field(default_factory=list)
    generation: int = 0
    mutations: int = 0
    code_path: str = ""
    acceptance: Optional[AcceptanceResult] = None  # 强验收结果

    @property
    def fitness_level(self) -> FitnessLevel:
        if self.fitness >= 1.0:
            return FitnessLevel.EXCELLENT
        elif self.fitness >= 0.8:
            return FitnessLevel.GOOD
        elif self.fitness >= 0.5:
            return FitnessLevel.PARTIAL
        elif self.fitness >= 0.2:
            return FitnessLevel.POOR
        return FitnessLevel.FAILED


# ============== LLM 接口 ==============
def call_llm(
    prompt: str, system_prompt: str = None, temperature: float = TEMPERATURE
) -> str:
    import urllib.request

    key_file = os.path.expanduser("~/.oyster-keys/minimax.env")
    API_KEY = os.environ.get("MINIMAX_API_KEY")
    if not API_KEY and os.path.exists(key_file):
        for line in open(key_file):
            if line.startswith("export MINIMAX_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"')
                break

    if not API_KEY:
        raise Exception("MINIMAX_API_KEY not found")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = json.dumps(
        {
            "model": "MiniMax-M2.5",
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "temperature": temperature,
        }
    ).encode()

    req = urllib.request.Request(
        "https://api.minimax.io/v1/text/chatcompletion_v2",
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  ⚠️ LLM 调用失败: {e}")
        return ""


# ============== Spec 保存 ==============
def save_spec(
    spec_content: str, project: str, individual_id: str, generation: int
) -> str:
    """保存 spec 到文件"""
    spec_dir = Path(f"~/Downloads/specs/{project}/collision").expanduser()
    spec_dir.mkdir(parents=True, exist_ok=True)

    filename = f"gen{generation:02d}_{individual_id}.md"
    path = spec_dir / filename
    path.write_text(spec_content)

    return str(path)


# ============== Dispatch 集成 ==============
def run_dispatch(project: str, spec_path: str) -> Dict:
    """运行 dispatch 执行 spec"""
    print(f"    📤 调度到 dispatch...")

    # 1. 启动 dispatch
    cmd = f"python3 ~/Downloads/dispatch/dispatch.py start {project}"

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        print(f"    ✅ Dispatch 已启动")
    except Exception as e:
        return {"status": "error", "message": f"启动失败: {e}"}

    # 2. 等待并检查状态
    max_wait = DISPATCH_TIMEOUT
    interval = 30
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(interval)
        elapsed += interval

        # 检查状态
        status_cmd = f"python3 ~/Downloads/dispatch/dispatch.py status {project}"
        status_result = subprocess.run(
            status_cmd, shell=True, capture_output=True, text=True, timeout=30
        )

        # 解析状态
        output = status_result.stdout
        if "completed" in output.lower() or "done" in output.lower():
            break
        elif "failed" in output.lower() or "error" in output.lower():
            return {"status": "failed", "output": output}

        print(f"    ⏳ 等待执行... ({elapsed}s)")

    # 3. 收集结果
    return {"status": "timeout", "output": "等待超时"}


def collect_test_results(project: str) -> Tuple[int, int, str]:
    """收集测试结果

    Returns:
        (passed, total, error_msg)
    """
    print(f"    📊 收集测试结果...")

    # 尝试读取 dispatch 报告
    report_path = Path(f"~/Downloads/dispatch/{project}-merge_report.json")
    if report_path.exists():
        try:
            data = json.loads(report_path.read_text())
            # 解析报告结构
            # 这个需要根据实际的报告格式来解析
            passed = data.get("passed", 0)
            total = data.get("total", 0)
            return passed, total, ""
        except:
            pass

    # 尝试运行测试命令
    test_cmd = (
        f"cd ~/Downloads/{project} && python3 -m pytest --tb=no -q 2>&1 | tail -5"
    )
    try:
        result = subprocess.run(
            test_cmd, shell=True, capture_output=True, text=True, timeout=120
        )
        output = result.stdout + result.stderr

        # 解析 pytest 输出
        # 例如: "5 passed, 2 failed" 或 "7 passed"
        passed = 0
        total = 0

        match = re.search(r"(\d+) passed", output)
        if match:
            passed = int(match.group(1))

        match = re.search(r"(\d+) failed", output)
        if match:
            total = passed + int(match.group(1))
        elif passed > 0:
            total = passed

        if total > 0:
            return passed, total, ""

        return 0, 0, "无法解析测试结果"

    except Exception as e:
        return 0, 0, f"测试执行失败: {e}"


# ============== 强验收评估 ==============
@dataclass
class AcceptanceResult:
    """强验收结果"""

    pytest_passed: int = 0
    pytest_total: int = 0
    pytest_score: float = 0.0

    lint_passed: bool = False
    lint_score: float = 0.0

    mypy_passed: bool = False
    mypy_score: float = 0.0

    integration_passed: int = 0
    integration_total: int = 0
    integration_score: float = 0.0

    total_score: float = 0.0
    error_msg: str = ""


def run_strong_acceptance(project: str) -> AcceptanceResult:
    """运行强验收标准：pytest + black + mypy + 集成测试"""
    result = AcceptanceResult()
    project_path = Path(f"~/Downloads/{project}").expanduser()

    # 1. Pytest (50%)
    print(f"    🔬 运行 pytest...")
    pytest_cmd = f"cd {project_path} && python3 -m pytest --tb=no -q 2>&1"
    try:
        proc = subprocess.run(
            pytest_cmd, shell=True, capture_output=True, text=True, timeout=180
        )
        output = proc.stdout + proc.stderr

        # 解析 pytest 结果
        passed = 0
        total = 0
        match = re.search(r"(\d+) passed", output)
        if match:
            passed = int(match.group(1))
        match = re.search(r"(\d+) failed", output)
        if match:
            total = passed + int(match.group(1))
        elif passed > 0:
            total = passed

        result.pytest_passed = passed
        result.pytest_total = total if total > 0 else 1
        result.pytest_score = (
            passed / result.pytest_total if result.pytest_total > 0 else 0
        )
        print(f"      pytest: {passed}/{total} = {result.pytest_score:.2f}")
    except Exception as e:
        result.error_msg += f"pytest错误: {e}; "

    # 2. Black/Flake8 (20%)
    print(f"    🔍 运行 black...")
    lint_passed = True
    for linter in ["black", "flake8"]:
        lint_cmd = f"cd {project_path} && python3 -m {linter} --check . 2>&1"
        try:
            proc = subprocess.run(
                lint_cmd, shell=True, capture_output=True, text=True, timeout=60
            )
            if proc.returncode != 0:
                lint_passed = False
                result.error_msg += f"{linter}失败; "
                break
        except:
            pass

    result.lint_passed = lint_passed
    result.lint_score = 1.0 if lint_passed else 0.0
    print(f"      lint: {'✓' if lint_passed else '✗'} = {result.lint_score:.2f}")

    # 3. Mypy (20%)
    print(f"    🔎 运行 mypy...")
    mypy_cmd = f"cd {project_path} && python3 -m mypy . --ignore-missing-imports 2>&1"
    try:
        proc = subprocess.run(
            mypy_cmd, shell=True, capture_output=True, text=True, timeout=120
        )
        result.mypy_passed = proc.returncode == 0
        result.mypy_score = 1.0 if result.mypy_passed else 0.0
        if not result.mypy_passed:
            result.error_msg += "mypy失败; "
    except Exception as e:
        result.mypy_passed = False
        result.mypy_score = 0.0
        result.error_msg += f"mypy错误: {e}; "

    print(f"      mypy: {'✓' if result.mypy_passed else '✗'} = {result.mypy_score:.2f}")

    # 4. 集成测试 (10%) - 如果有 tests/integration 目录
    print(f"    🌐 运行集成测试...")
    integration_path = project_path / "tests" / "integration"
    if integration_path.exists():
        int_cmd = (
            f"cd {project_path} && python3 -m pytest tests/integration --tb=no -q 2>&1"
        )
        try:
            proc = subprocess.run(
                int_cmd, shell=True, capture_output=True, text=True, timeout=180
            )
            output = proc.stdout + proc.stderr

            passed = 0
            total = 0
            match = re.search(r"(\d+) passed", output)
            if match:
                passed = int(match.group(1))
            match = re.search(r"(\d+) failed", output)
            if match:
                total = passed + int(match.group(1))
            elif passed > 0:
                total = passed

            result.integration_passed = passed
            result.integration_total = total if total > 0 else 1
            result.integration_score = (
                passed / result.integration_total if result.integration_total > 0 else 0
            )
        except Exception as e:
            result.integration_score = 0.0
            result.error_msg += f"集成测试错误: {e}; "
    else:
        result.integration_passed = 1
        result.integration_total = 1
        result.integration_score = 1.0  # 无集成测试目录 = 跳过

    print(
        f"      integration: {result.integration_passed}/{result.integration_total} = {result.integration_score:.2f}"
    )

    # 计算总分
    result.total_score = (
        result.pytest_score * WEIGHT_PYTEST
        + result.lint_score * WEIGHT_LINT
        + result.mypy_score * WEIGHT_MYPY
        + result.integration_score * WEIGHT_INTEGRATION
    )

    print(
        f"    📊 强验收总分: {result.total_score:.2f} (pytest:{result.pytest_score * WEIGHT_PYTEST:.2f} + lint:{result.lint_score * WEIGHT_LINT:.2f} + mypy:{result.mypy_score * WEIGHT_MYPY:.2f} + integration:{result.integration_score * WEIGHT_INTEGRATION:.2f})"
    )

    return result


# ============== 评估 ==============
def evaluate_individual(
    individual: SpecIndividual, project: str, test_cmd: str = None
) -> SpecIndividual:
    """评估一个个體 - 真实执行 + 强验收"""

    # 1. 保存 spec
    spec_path = save_spec(
        individual.spec_content, project, individual.id, individual.generation
    )
    individual.code_path = spec_path
    print(f"    📄 Spec 已保存: {spec_path}")

    # 2. 调用 dispatch 执行
    dispatch_result = run_dispatch(project, spec_path)

    if dispatch_result["status"] == "error":
        individual.error_msg = dispatch_result.get("message", "Dispatch 错误")
        individual.fitness = 0.0
        return individual

    # 3. 运行强验收标准
    acceptance = run_strong_acceptance(project)
    individual.acceptance = acceptance

    individual.test_passed = acceptance.pytest_passed
    individual.test_total = acceptance.pytest_total
    individual.fitness = acceptance.total_score

    if acceptance.error_msg:
        individual.error_msg = acceptance.error_msg

    return individual


# ============== 简化版评估（不需要真实 dispatch）==============
def evaluate_individual_mock(
    individual: SpecIndividual, project: str, test_cmd: str = None
) -> SpecIndividual:
    """模拟评估 - 用于测试（模拟强验收）"""
    import random

    # 模拟强验收各项得分
    pytest_score = random.uniform(0.3, 1.0)
    lint_score = random.choice([0.0, 1.0])
    mypy_score = random.choice([0.0, 1.0])
    integration_score = random.uniform(0.5, 1.0)

    # 构建模拟验收结果
    acceptance = AcceptanceResult()
    acceptance.pytest_passed = int(pytest_score * 10)
    acceptance.pytest_total = 10
    acceptance.pytest_score = pytest_score

    acceptance.lint_passed = lint_score == 1.0
    acceptance.lint_score = lint_score

    acceptance.mypy_passed = mypy_score == 1.0
    acceptance.mypy_score = mypy_score

    acceptance.integration_passed = int(integration_score * 3)
    acceptance.integration_total = 3
    acceptance.integration_score = integration_score

    acceptance.total_score = (
        pytest_score * WEIGHT_PYTEST
        + lint_score * WEIGHT_LINT
        + mypy_score * WEIGHT_MYPY
        + integration_score * WEIGHT_INTEGRATION
    )

    individual.acceptance = acceptance
    individual.fitness = acceptance.total_score
    individual.test_passed = acceptance.pytest_passed
    individual.test_total = acceptance.pytest_total

    if individual.fitness < 0.3:
        individual.error_msg = "测试失败: 某些断言未通过"

    return individual


# ============== 进化相关函数 ==============
def build_generation_prompt(
    task: str,
    project: str,
    population: List[SpecIndividual],
    best_individual: Optional[SpecIndividual],
    all_tests: str,
    generation: int,
    max_gens: int = MAX_GENERATIONS,
    pop_size: int = POPULATION_SIZE,
) -> str:
    prompt = f"""你是一个 AI 代码工厂的进化算法引擎，负责生成能通过所有测试的代码。

## 任务
{task}

## 项目
{project}

## 轮次
第 {generation + 1} 代 (共 {max_gens} 代)

## 测试用例
{all_tests}

"""

    if best_individual:
        prompt += f"""
### 最佳解法 (fitness: {best_individual.fitness:.2f})
```
{best_individual.spec_content[:1000]}
```

错误分析:
{best_individual.error_msg if best_individual.error_msg else "无"}
"""

    if population:
        prompt += "\n### 这一代的解法评估\n"
        for ind in sorted(population, key=lambda x: x.fitness, reverse=True):
            prompt += f"""
- ID: {ind.id}
- Fitness: {ind.fitness:.2f} ({ind.test_passed}/{ind.test_total} 测试通过)
- 错误: {ind.error_msg[:200] if ind.error_msg else "无"}
"""

    prompt += f"""
## 进化策略指导

根据上一代的结果，你需要：
1. 如果有 fitness >= 0.8 的解法，**保留并改进**它
2. 如果所有解法都失败，**改变思路**，尝试全新方案
3. 如果部分成功但有错误，**修复错误**，保持正确部分
4. 尝试不同的**技术路径**（不同的库/架构/算法）

## 输出要求

生成 {pop_size} 个新的 spec 变体。

每个 spec 必须：
1. 有不同的技术路径/实现思路
2. 验收标准必须可测试
3. 包含具体的代码改动

用 "---SPEC_SEPARATOR---" 分隔每个 spec。
"""

    return prompt


SYSTEM_PROMPT = """你是一个专业的 AI 代码进化算法引擎。

你的目标是生成能**通过所有测试**的代码解决方案。

关键原则：
- 测试通过 = 正确
- 测试失败 = 需要改进
- 用测试结果指导你的生成方向

输出格式：直接输出 N 个 spec，用 "---SPEC_SEPARATOR---" 分隔"""


def select_parents(population: List[SpecIndividual]) -> List[SpecIndividual]:
    if not population:
        return []
    sorted_pop = sorted(population, key=lambda x: x.fitness, reverse=True)
    return sorted_pop[: len(sorted_pop) // 2 + 1]


def generate_next_generation(
    task: str,
    project: str,
    population: List[SpecIndividual],
    all_tests: str,
    generation: int,
    pop_size: int = POPULATION_SIZE,
    max_gens: int = MAX_GENERATIONS,
) -> List[SpecIndividual]:
    best = max(population, key=lambda x: x.fitness) if population else None

    prompt = build_generation_prompt(
        task, project, population, best, all_tests, generation, max_gens, pop_size
    )

    print(f"  🔄 调用 LLM 生成第 {generation + 1} 代...")
    result = call_llm(prompt, system_prompt=SYSTEM_PROMPT, temperature=TEMPERATURE)

    if not result:
        print("  ⚠️ LLM 返回空，使用上一代最佳")
        if best:
            return [
                SpecIndividual(
                    id=f"gen{generation + 1}_v{i}",
                    spec_content=best.spec_content,
                    generation=generation + 1,
                )
                for i in range(pop_size)
            ]
        return []

    specs = result.split("---SPEC_SEPARATOR---")
    specs = [s.strip() for s in specs if s.strip()]

    new_population = []
    for i, spec in enumerate(specs[:pop_size]):
        ind = SpecIndividual(
            id=f"gen{generation + 1}_v{i + 1}",
            spec_content=spec,
            generation=generation + 1,
            parent_ids=[p.id for p in select_parents(population)],
        )
        new_population.append(ind)

    while len(new_population) < pop_size:
        if best:
            new_population.append(
                SpecIndividual(
                    id=f"gen{generation + 1}_v{len(new_population) + 1}",
                    spec_content=best.spec_content,
                    generation=generation + 1,
                    mutations=best.mutations + 1,
                )
            )
        else:
            break

    return new_population


# ============== 主循环 ==============
def collision_loop(
    task: str,
    project: str,
    test_cmd: str = None,
    all_tests: str = "",
    max_gens: int = MAX_GENERATIONS,
    pop_size: int = POPULATION_SIZE,
    mock: bool = False,
) -> Dict:
    """碰撞主循环"""

    print(f"\n{'=' * 60}")
    print(f"🎯 Spec 碰撞系统 v2 (LLaMEA-style)")
    print(f"📋 任务: {task}")
    print(f"📁 项目: {project}")
    print(f"⚙️  配置: {pop_size} 个体/代, {max_gens} 代")
    print(f"🔧 模式: {'模拟' if mock else '真实执行'}")
    print(f"{'=' * 60}\n")

    # 选择评估函数
    evaluator = evaluate_individual_mock if mock else evaluate_individual

    population = []
    best_ever = None
    all_history = []

    for generation in range(max_gens):
        print(f"\n📌 第 {generation + 1}/{max_gens} 代")

        if generation == 0:
            print("  🎲 第一代：随机生成...")
            new_pop = generate_next_generation(
                task, project, [], all_tests, generation, pop_size, max_gens
            )
        else:
            print("  🧬 进化生成...")
            new_pop = generate_next_generation(
                task, project, population, all_tests, generation, pop_size, max_gens
            )

        if not new_pop:
            print("  ⚠️ 生成失败，尝试重启...")
            new_pop = generate_next_generation(
                task, project, [], all_tests, generation, pop_size, max_gens
            )
            if not new_pop:
                print("  ❌ 连续生成失败，停止")
                break

        # 评估每个个体
        print(f"  📊 评估 {len(new_pop)} 个个体...")
        for ind in new_pop:
            ind = evaluator(ind, project, test_cmd)
            print(
                f"    {ind.id}: fitness={ind.fitness:.2f} ({ind.test_passed}/{ind.test_total})"
            )

        all_history.extend(new_pop)

        current_best = max(new_pop, key=lambda x: x.fitness)
        if best_ever is None or current_best.fitness > best_ever.fitness:
            best_ever = current_best
            print(f"  ⭐ 新最佳: {best_ever.id}, fitness={best_ever.fitness:.2f}")

        if best_ever.fitness >= 1.0:
            print(f"\n🎉 找到完美解！ fitness=1.0")
            break

        population = new_pop

        avg_fitness = sum(ind.fitness for ind in population) / len(population)
        print(f"  📈 平均 fitness: {avg_fitness:.2f}")

        if generation > 5 and avg_fitness < 0.1:
            print("  ⚠️ 连续低 fitness，重启思路...")
            population = []

    return {
        "task": task,
        "project": project,
        "generations": generation + 1,
        "best_individual": best_ever,
        "history": all_history,
        "success": best_ever.fitness >= 0.8 if best_ever else False,
    }


# ============== CLI ==============
def main():
    parser = argparse.ArgumentParser(description="Spec 碰撞系统 v2 - LLaMEA 风格")
    parser.add_argument("task", help="任务目标")
    parser.add_argument("-p", "--project", required=True, help="项目名")
    parser.add_argument("-t", "--test", help="测试命令")
    parser.add_argument("--tests", help="测试用例内容")
    parser.add_argument(
        "-g", "--generations", type=int, default=MAX_GENERATIONS, help="最大代数"
    )
    parser.add_argument(
        "-n", "--population", type=int, default=POPULATION_SIZE, help="每代个体数"
    )
    parser.add_argument(
        "--mock", action="store_true", help="使用模拟评估（不真实执行）"
    )

    args = parser.parse_args()

    result = collision_loop(
        args.task,
        args.project,
        args.test,
        args.tests or "",
        args.generations,
        args.population,
        args.mock,
    )

    print(f"\n{'=' * 60}")
    print(f"🏁 碰撞完成")
    print(f"代数: {result['generations']}")
    print(f"成功: {result['success']}")
    if result["best_individual"]:
        print(f"最佳 fitness: {result['best_individual'].fitness:.2f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
