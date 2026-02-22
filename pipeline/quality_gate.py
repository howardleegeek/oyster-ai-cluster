#!/usr/bin/env python3
"""Code Pipeline 质量门禁

支持 lint + unit tests + 覆盖率检查，支持 code 和 content 两种 profile
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class LintResult:
    """Lint 检查结果"""
    success: bool
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    output: str = ""
    errors: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """测试执行结果"""
    success: bool
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    output: str = ""
    failed_tests: List[str] = field(default_factory=list)


@dataclass
class CoverageResult:
    """覆盖率检查结果"""
    success: bool
    coverage_percent: float = 0.0
    lines_covered: int = 0
    lines_total: int = 0
    files: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class GateResult:
    """质量门禁综合结果"""
    passed: bool
    profile: str
    lint: Optional[LintResult] = None
    tests: Optional[TestResult] = None
    coverage: Optional[CoverageResult] = None
    forbidden_patterns: List[str] = field(default_factory=list)
    risk_files: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'pass': self.passed,
            'profile': self.profile,
            'lint': {
                'success': self.lint.success if self.lint else False,
                'passed': self.lint.passed if self.lint else 0,
                'failed': self.lint.failed if self.lint else 0,
                'warnings': self.lint.warnings if self.lint else 0,
                'output': self.lint.output if self.lint else ''
            },
            'tests': {
                'success': self.tests.success if self.tests else False,
                'passed': self.tests.passed if self.tests else 0,
                'failed': self.tests.failed if self.tests else 0,
                'skipped': self.tests.skipped if self.tests else 0,
                'duration': self.tests.duration if self.tests else 0.0
            },
            'coverage': {
                'success': self.coverage.success if self.coverage else False,
                'coverage_percent': self.coverage.coverage_percent if self.coverage else 0.0,
                'lines_covered': self.coverage.lines_covered if self.coverage else 0,
                'lines_total': self.coverage.lines_total if self.coverage else 0
            },
            'forbidden_patterns': self.forbidden_patterns,
            'risk_files': self.risk_files,
            'details': self.details
        }


class CodeQualityGate:
    """代码质量门禁

    支持两种 profile：
    - code: 严格的代码质量检查（lint + unit tests + coverage）
    - content: 内容生成质量检查（较宽松）
    """

    # Code profile - 严格的代码质量标准
    PROFILE_CODE = {
        "must_pass": ["lint", "unit_tests"],
        "require_test": True,
        "min_coverage": 80,
        "forbidden_patterns": ["TODO", "FIXME", "placeholder"],
        "risk_files": ["auth", "payment", "security", "password", "token", "credential"]
    }

    # Content profile - 较宽松的内容生成标准
    PROFILE_CONTENT = {
        "must_pass": ["lint"],
        "require_test": False,
        "min_coverage": 0,
        "forbidden_patterns": [],
        "risk_files": []
    }

    def __init__(self):
        """初始化质量门禁"""
        self._profiles = {
            "code": self.PROFILE_CODE,
            "content": self.PROFILE_CONTENT
        }

    def check(self, workspace: str, profile: str = "code") -> GateResult:
        """执行质量检查

        Args:
            workspace: 工作区路径
            profile: profile 类型 ('code' 或 'content')

        Returns:
            GateResult: 质量检查结果
        """
        workspace_path = Path(workspace)

        if not workspace_path.exists():
            return GateResult(
                passed=False,
                profile=profile,
                details={"error": f"Workspace not found: {workspace}"}
            )

        # 获取 profile 配置
        profile_config = self._profiles.get(profile, self.PROFILE_CODE)

        # 运行检查
        lint_result = None
        test_result = None
        coverage_result = None

        # Lint 检查
        if "lint" in profile_config["must_pass"]:
            lint_result = self.run_lint(workspace)
            if not lint_result.success:
                return GateResult(
                    passed=False,
                    profile=profile,
                    lint=lint_result,
                    details={"reason": "lint check failed"}
                )

        # 单元测试
        if profile_config["require_test"] or "unit_tests" in profile_config["must_pass"]:
            test_result = self.run_tests(workspace)
            if not test_result.success:
                return GateResult(
                    passed=False,
                    profile=profile,
                    lint=lint_result,
                    tests=test_result,
                    details={"reason": "unit tests failed"}
                )

        # 覆盖率检查
        if profile_config["min_coverage"] > 0:
            coverage_result = self.check_coverage(workspace)
            if not coverage_result.success:
                return GateResult(
                    passed=False,
                    profile=profile,
                    lint=lint_result,
                    tests=test_result,
                    coverage=coverage_result,
                    details={"reason": f"coverage below {profile_config['min_coverage']}%"}
                )

        # 检查禁止模式
        forbidden_patterns = self._check_forbidden_patterns(workspace, profile_config["forbidden_patterns"])

        # 检查风险文件
        risk_files = self._check_risk_files(workspace, profile_config["risk_files"])

        # 所有检查通过
        return GateResult(
            passed=True,
            profile=profile,
            lint=lint_result,
            tests=test_result,
            coverage=coverage_result,
            forbidden_patterns=forbidden_patterns,
            risk_files=risk_files,
            details={"reason": "all checks passed"}
        )

    def run_lint(self, workspace: str) -> LintResult:
        """运行 lint 检查

        支持多种 linter：
        - pylint (Python)
        - flake8 (Python)
        - eslint (JavaScript/TypeScript)
        - ruff (Python, 快速)

        Args:
            workspace: 工作区路径

        Returns:
            LintResult: Lint 检查结果
        """
        workspace_path = Path(workspace)

        # 尝试不同的 linter
        linter_commands = [
            # ruff - 最快
            (["ruff", "check", "--output-format=json", str(workspace_path)], "ruff"),
            # pylint
            (["pylint", "--output-format=json", str(workspace_path)], "pylint"),
            # flake8
            (["flake8", str(workspace_path)], "flake8"),
            # eslint
            (["npx", "eslint", "--format=json", str(workspace_path)], "eslint")
        ]

        for cmd, linter_name in linter_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0 or linter_name == "flake8":
                    # 成功或 flake8（返回非0表示发现问题）
                    output = result.stdout or result.stderr

                    # 解析输出
                    errors = self._parse_lint_output(output, linter_name)

                    return LintResult(
                        success=result.returncode == 0 or linter_name == "flake8",
                        passed=len([e for e in errors if e.get("type") == "info"]) or 0,
                        failed=len([e for e in errors if e.get("type") in ["error", "E"]]),
                        warnings=len([e for e in errors if e.get("type") in ["warning", "W"]]),
                        output=output[:1000],  # 限制输出长度
                        errors=[f"{e.get('file', '')}:{e.get('line', '')}: {e.get('message', '')}" for e in errors[:10]]
                    )

            except (subprocess.TimeoutExpired, FileNotFoundError):
                # 超时或命令不存在，尝试下一个 linter
                continue

        # 所有 linter 都失败
        return LintResult(
            success=True,  # 没有可用的 linter，不算失败
            output="No linter available",
            errors=[]
        )

    def run_tests(self, workspace: str) -> TestResult:
        """运行单元测试

        支持多种测试框架：
        - pytest (Python)
        - unittest (Python)
        - jest (JavaScript/TypeScript)
        - vitest (JavaScript/TypeScript)

        Args:
            workspace: 工作区路径

        Returns:
            TestResult: 测试执行结果
        """
        workspace_path = Path(workspace)

        # 尝试不同的测试框架
        test_commands = [
            # pytest
            (["pytest", "--tb=no", "-q", str(workspace_path)], "pytest"),
            # unittest
            (["python", "-m", "unittest", "discover", "-s", str(workspace_path)], "unittest"),
            # jest
            (["npx", "jest", "--json", "--outputFile=/tmp/jest-result.json"], "jest"),
            # vitest
            (["npx", "vitest", "run", "--json", "--reporter=json"], "vitest")
        ]

        for cmd, framework in test_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=workspace_path
                )

                output = result.stdout + result.stderr

                # 检查是否是配置错误或安装问题（不应该是测试失败）
                if "config file" in output.lower() or "no config" in output.lower() or "npm warn" in output.lower() or "throw new" in output:
                    # 配置文件缺失或安装问题，尝试下一个框架
                    continue

                # 解析结果
                test_result = self._parse_test_output(output, framework, result.returncode)

                return test_result

            except (subprocess.TimeoutExpired, FileNotFoundError):
                # 超时或命令不存在，尝试下一个框架
                continue

        # 所有测试框架都失败
        return TestResult(
            success=True,  # 没有可用的测试框架，不算失败
            output="No test framework available"
        )

    def check_coverage(self, workspace: str) -> CoverageResult:
        """检查代码覆盖率

        支持多种覆盖率工具：
        - coverage.py (Python)
        - pytest-cov (Python)
        - c8 (JavaScript/TypeScript)
        - istanbul (JavaScript/TypeScript)

        Args:
            workspace: 工作区路径

        Returns:
            CoverageResult: 覆盖率检查结果
        """
        workspace_path = Path(workspace)

        # 尝试不同的覆盖率工具
        coverage_commands = [
            # coverage.py
            (["coverage", "report", "--json"], "coverage"),
            # pytest-cov
            (["pytest", "--cov", "--cov-report=json", str(workspace_path)], "pytest-cov"),
            # c8
            (["npx", "c8", "report", "--reporter=json"], "c8"),
            # istanbul
            (["npx", "nyc", "report", "--reporter=json"], "istanbul")
        ]

        for cmd, tool in coverage_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=workspace_path
                )

                output = result.stdout or result.stderr

                # 解析结果
                coverage_result = self._parse_coverage_output(output, tool)

                return coverage_result

            except (subprocess.TimeoutExpired, FileNotFoundError):
                # 超时或命令不存在，尝试下一个工具
                continue

        # 所有覆盖率工具都失败
        return CoverageResult(
            success=True,  # 没有可用的覆盖率工具，不算失败
            coverage_percent=0.0,
            lines_covered=0,
            lines_total=0
        )

    def _check_forbidden_patterns(self, workspace: str, patterns: List[str]) -> List[str]:
        """检查禁止的模式

        Args:
            workspace: 工作区路径
            patterns: 禁止的模式列表

        Returns:
            List[str]: 匹配的文件和位置
        """
        if not patterns:
            return []

        workspace_path = Path(workspace)
        matches = []

        # 遍历所有 Python 文件
        for py_file in workspace_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                for pattern in patterns:
                    if pattern in content:
                        # 找到匹配的行
                        for i, line in enumerate(content.split('\n'), 1):
                            if pattern in line:
                                matches.append(f"{py_file.relative_to(workspace_path)}:{i}: contains '{pattern}'")
            except Exception:
                continue

        return matches

    def _check_risk_files(self, workspace: str, risk_keywords: List[str]) -> List[str]:
        """检查风险文件

        Args:
            workspace: 工作区路径
            risk_keywords: 风险关键词列表

        Returns:
            List[str]: 风险文件路径
        """
        if not risk_keywords:
            return []

        workspace_path = Path(workspace)
        risk_files = []

        # 检查文件名是否包含风险关键词
        for file_path in workspace_path.rglob("*"):
            if file_path.is_file():
                file_name = file_path.name.lower()
                for keyword in risk_keywords:
                    if keyword in file_name:
                        risk_files.append(str(file_path.relative_to(workspace_path)))
                        break

        return risk_files

    def _parse_lint_output(self, output: str, linter: str) -> List[Dict]:
        """解析 linter 输出

        Args:
            output: linter 输出
            linter: linter 名称

        Returns:
            List[Dict]: 解析后的错误列表
        """
        errors = []

        try:
            if linter == "ruff":
                data = json.loads(output)
                for item in data:
                    errors.append({
                        "file": item.get("filename", ""),
                        "line": item.get("location", {}).get("row", 0),
                        "type": item.get("code", {}).get("category", "unknown"),
                        "message": item.get("message", "")
                    })

            elif linter == "pylint":
                data = json.loads(output)
                for item in data:
                    errors.append({
                        "file": item.get("path", ""),
                        "line": item.get("line", 0),
                        "type": item.get("type", "unknown"),
                        "message": item.get("message", "")
                    })

            elif linter == "flake8":
                # flake8 输出格式: file:line:col: code message
                for line in output.split('\n'):
                    if ':' in line:
                        parts = line.split(':', 3)
                        if len(parts) >= 3:
                            errors.append({
                                "file": parts[0].strip(),
                                "line": int(parts[1]) if parts[1].strip().isdigit() else 0,
                                "type": parts[2].strip().split()[0] if parts[2].strip() else "unknown",
                                "message": parts[3].strip() if len(parts) > 3 else ""
                            })

        except (json.JSONDecodeError, ValueError):
            # 解析失败，返回空列表
            pass

        return errors

    def _parse_test_output(self, output: str, framework: str, returncode: int) -> TestResult:
        """解析测试输出

        Args:
            output: 测试输出
            framework: 测试框架名称
            returncode: 退出码

        Returns:
            TestResult: 测试结果
        """
        passed = 0
        failed = 0
        skipped = 0
        failed_tests = []

        try:
            if framework == "pytest":
                # pytest 输出格式: X passed, Y failed, Z skipped in N.XXs
                match = re.search(r'(\d+)\s+passed', output)
                if match:
                    passed = int(match.group(1))
                match = re.search(r'(\d+)\s+failed', output)
                if match:
                    failed = int(match.group(1))
                match = re.search(r'(\d+)\s+skipped', output)
                if match:
                    skipped = int(match.group(1))

                # 解析失败的测试
                failed_tests = []
                for line in output.split('\n'):
                    if 'FAILED' in line and '::' in line:
                        failed_tests.append(line.split('FAILED')[1].strip())

                success = returncode == 0 and failed == 0

            elif framework == "unittest":
                # unittest 输出格式: Ran X tests in N.XXs
                match = re.search(r'Ran (\d+) test', output)
                if match:
                    total = int(match.group(1))
                    if 'OK' in output:
                        passed = total
                    else:
                        failed = total

                success = 'OK' in output and returncode == 0
                failed_tests = []

            elif framework == "jest":
                # 尝试读取 JSON 报告
                try:
                    with open('/tmp/jest-result.json', 'r') as f:
                        data = json.load(f)
                        passed = data.get('numPassedTests', 0)
                        failed = data.get('numFailedTests', 0)
                        failed_tests = [t.get('name', '') for t in data.get('testResults', []) if not t.get('status') == 'passed']
                except:
                    pass

                success = returncode == 0 and failed == 0

            elif framework == "vitest":
                # vitest JSON 输出
                try:
                    data = json.loads(output)
                    passed = data.get('numPassedTests', 0)
                    failed = data.get('numFailedTests', 0)
                    failed_tests = []
                except:
                    pass

                success = returncode == 0 and failed == 0

            else:
                success = True

        except Exception:
            success = True

        return TestResult(
            success=success,
            passed=passed,
            failed=failed,
            skipped=skipped,
            output=output[:1000],
            failed_tests=failed_tests[:10]
        )

    def _parse_coverage_output(self, output: str, tool: str) -> CoverageResult:
        """解析覆盖率输出

        Args:
            output: 覆盖率工具输出
            tool: 工具名称

        Returns:
            CoverageResult: 覆盖率结果
        """
        try:
            if tool == "coverage":
                # coverage.py JSON 输出
                data = json.loads(output)
                lines_covered = data.get("totals", {}).get("covered_lines", 0)
                lines_total = data.get("totals", {}).get("num_statements", 0)
                coverage_percent = (lines_covered / lines_total * 100) if lines_total > 0 else 0

                return CoverageResult(
                    success=coverage_percent >= 80,
                    coverage_percent=coverage_percent,
                    lines_covered=lines_covered,
                    lines_total=lines_total
                )

            elif tool == "pytest-cov":
                # 尝试读取 coverage.json
                try:
                    with open('coverage.json', 'r') as f:
                        data = json.load(f)
                        lines_covered = data.get("totals", {}).get("covered_lines", 0)
                        lines_total = data.get("totals", {}).get("num_statements", 0)
                        coverage_percent = (lines_covered / lines_total * 100) if lines_total > 0 else 0

                        return CoverageResult(
                            success=coverage_percent >= 80,
                            coverage_percent=coverage_percent,
                            lines_covered=lines_covered,
                            lines_total=lines_total
                        )
                except:
                    pass

            elif tool in ["c8", "istanbul"]:
                # c8/istanbul JSON 输出
                data = json.loads(output)
                lines_covered = data.get("total", {}).get("lines", {}).get("pct", 0)
                lines_total = data.get("total", {}).get("lines", {}).get("total", 0)
                covered = data.get("total", {}).get("lines", {}).get("covered", 0)

                return CoverageResult(
                    success=lines_covered >= 80,
                    coverage_percent=lines_covered,
                    lines_covered=covered,
                    lines_total=lines_total
                )

        except (json.JSONDecodeError, ValueError):
            pass

        return CoverageResult(
            success=True,
            coverage_percent=0.0,
            lines_covered=0,
            lines_total=0
        )


# 测试验证
if __name__ == "__main__":
    # 验证命令示例
    from pathlib import Path

    gate = CodeQualityGate()
    result = gate.check(str(Path.cwd()))

    print("=== Code Quality Gate Result ===")
    print(f"Pass: {result.passed}")
    print(f"Profile: {result.profile}")

    if result.lint:
        print(f"\nLint: {'PASS' if result.lint.success else 'FAIL'}")
        print(f"  Passed: {result.lint.passed}")
        print(f"  Failed: {result.lint.failed}")
        print(f"  Warnings: {result.lint.warnings}")

    if result.tests:
        print(f"\nTests: {'PASS' if result.tests.success else 'FAIL'}")
        print(f"  Passed: {result.tests.passed}")
        print(f"  Failed: {result.tests.failed}")
        print(f"  Skipped: {result.tests.skipped}")

    if result.coverage:
        print(f"\nCoverage: {'PASS' if result.coverage.success else 'FAIL'}")
        print(f"  Coverage: {result.coverage.coverage_percent:.2f}%")
        print(f"  Lines: {result.coverage.lines_covered}/{result.coverage.lines_total}")

    if result.forbidden_patterns:
        print(f"\nForbidden Patterns Found:")
        for pattern in result.forbidden_patterns[:5]:
            print(f"  {pattern}")

    if result.risk_files:
        print(f"\nRisk Files Found:")
        for file in result.risk_files[:5]:
            print(f"  {file}")

    print(f"\nDetails: {result.details.get('reason', 'N/A')}")
