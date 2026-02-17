#!/usr/bin/env python3
"""PR Bot - 自动 PR 管理

支持：
- 自动创建 PR
- 检查 CI 状态
- Rerun workflow
- 高风险文件标记
"""

import subprocess
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field
from enum import Enum


class CIStatus(str, Enum):
    """CI 状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class PRResult:
    """PR 创建结果"""
    success: bool
    pr_url: str = ""
    pr_number: int = 0
    error: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowRun:
    """Workflow 运行信息"""
    id: int
    name: str
    status: CIStatus
    conclusion: Optional[str]
    created_at: str
    updated_at: str
    html_url: str


@dataclass
class CIResult:
    """CI 检查结果"""
    overall_status: CIStatus
    workflows: List[WorkflowRun] = field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0
    checks_pending: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RerunResult:
    """Rerun 结果"""
    success: bool
    workflow_id: int = 0
    error: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class PRBot:
    """自动 PR 管理

    支持通过 GitHub CLI 进行 PR 创建、CI 检查和 rerun
    """

    # 高风险文件关键词
    HIGH_RISK_KEYWORDS = [
        "auth", "authentication", "login", "password", "credential",
        "payment", "billing", "checkout", "stripe", "paypal",
        "security", "encrypt", "decrypt", "secret", "token",
        "api_key", "private_key", "jwt", "oauth", "saml",
        "admin", "superuser", "privilege", "permission"
    ]

    def __init__(self, repo: Optional[str] = None):
        """初始化 PRBot

        Args:
            repo: 仓库格式 (owner/repo)，如果为 None 则从当前 git repo 自动检测
        """
        self.repo = repo or self._detect_repo()

    def _detect_repo(self) -> Optional[str]:
        """从当前 git 仓库检测 repo 名称

        Returns:
            Optional[str]: repo 名称，如果无法检测则返回 None
        """
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=10
            )

            url = result.stdout.strip()

            if not url:
                return None

            # 解析 URL (支持 git@ 和 https://)
            if url.startswith("git@"):
                # git@github.com:owner/repo.git
                repo = url.split(":")[1].replace(".git", "")
            elif url.startswith("https://"):
                # https://github.com/owner/repo.git
                repo = url.replace("https://github.com/", "").replace(".git", "")
            else:
                raise ValueError(f"Unsupported git URL format: {url}")

            return repo

        except Exception:
            return None

    def _check_gh_cli(self):
        """检查 GitHub CLI 是否可用"""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError("GitHub CLI (gh) not installed or not authenticated")

        except FileNotFoundError:
            raise RuntimeError("GitHub CLI (gh) not found. Install from https://cli.github.com/")

    def _run_gh(self, args: List[str], repo: Optional[str] = None) -> str:
        """运行 gh 命令

        Args:
            args: gh 命令参数
            repo: repo 名称（如果与 self.repo 不同）

        Returns:
            stdout 输出

        Raises:
            RuntimeError: 命令执行失败
        """
        full_args = ["gh"]
        if repo:
            full_args.extend(["--repo", repo])
        full_args.extend(args)

        try:
            result = subprocess.run(
                full_args,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                error = result.stderr.strip() or result.stdout.strip()
                raise RuntimeError(f"gh command failed: {error}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("gh command timed out")

    def create_pr(
        self,
        repo: str,
        branch: str,
        title: str,
        body: str,
        base: str = "main",
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> PRResult:
        """创建 PR

        Args:
            repo: 仓库 (owner/repo)
            branch: 源分支
            title: PR 标题
            body: PR 描述
            base: 目标分支（默认 main）
            labels: 标签列表
            assignees: 指定人员列表

        Returns:
            PRResult: PR 创建结果
        """
        try:
            # 获取变更文件列表
            changed_files = self._get_changed_files(branch, base)

            # 判断高风险
            is_high_risk = self.is_high_risk(changed_files)

            # 构建描述
            if is_high_risk:
                body = f"**⚠️ HIGH RISK CHANGES**\n\n{body}\n\n---\n\n**Changed Files:**\n" + "\n".join(f"- {f}" for f in changed_files)
                labels = (labels or []) + ["needs-review", "high-risk"]
            else:
                body = f"{body}\n\n---\n\n**Changed Files:**\n" + "\n".join(f"- {f}" for f in changed_files)

            # 构建 gh 命令
            args = [
                "pr", "create",
                "--base", base,
                "--head", branch,
                "--title", title,
                "--body", body,
                "--json", "url,number"
            ]

            if labels:
                args.extend(["--label", ",".join(labels)])

            if assignees:
                args.extend(["--assignee", ",".join(assignees)])

            # 如果是不同的 repo，添加 --repo 参数
            if repo != self.repo:
                args.extend(["--repo", repo])

            output = self._run_gh(args, repo if repo != self.repo else None)

            # 解析输出
            data = json.loads(output)

            return PRResult(
                success=True,
                pr_url=data.get("url", ""),
                pr_number=data.get("number", 0),
                details={
                    "branch": branch,
                    "base": base,
                    "high_risk": is_high_risk,
                    "changed_files": changed_files,
                    "labels": labels
                }
            )

        except Exception as e:
            return PRResult(
                success=False,
                error=str(e),
                details={"branch": branch, "base": base}
            )

    def _get_changed_files(self, branch: str, base: str) -> List[str]:
        """获取变更文件列表

        Args:
            branch: 源分支
            base: 目标分支

        Returns:
            List[str]: 变更文件列表
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base}...{branch}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return []

            files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            return files

        except Exception:
            return []

    def check_ci_status(self, pr_url: str) -> CIResult:
        """检查 CI 状态

        Args:
            pr_url: PR URL

        Returns:
            CIResult: CI 检查结果
        """
        try:
            # 从 PR URL 提取 PR number
            pr_number = self._extract_pr_number(pr_url)

            if not pr_number:
                return CIResult(
                    overall_status=CIStatus.UNKNOWN,
                    details={"error": f"Invalid PR URL: {pr_url}"}
                )

            # 获取 PR 的检查状态
            args = [
                "api",
                f"repos/{self.repo}/pulls/{pr_number}/checks",
                "--jq", '.check_runs[] | {id, name, status, conclusion, created_at, updated_at, html_url}'
            ]

            output = self._run_gh(args)

            # 解析检查结果
            workflows = []
            checks_passed = 0
            checks_failed = 0
            checks_pending = 0

            for line in output.split('\n'):
                if not line.strip():
                    continue

                try:
                    data = json.loads(line)

                    status_map = {
                        "queued": CIStatus.PENDING,
                        "in_progress": CIStatus.RUNNING,
                        "completed": CIStatus.SUCCESS
                    }

                    status = status_map.get(data.get("status"), CIStatus.UNKNOWN)

                    # 如果已完成，检查 conclusion
                    if status == CIStatus.SUCCESS:
                        conclusion = data.get("conclusion", "")
                        if conclusion == "success":
                            checks_passed += 1
                        elif conclusion in ["failure", "timed_out", "cancelled"]:
                            status = CIStatus.FAILURE
                            checks_failed += 1
                            conclusion = conclusion
                        else:
                            checks_pending += 1
                    elif status == CIStatus.PENDING:
                        checks_pending += 1
                    elif status == CIStatus.RUNNING:
                        checks_pending += 1

                    workflow = WorkflowRun(
                        id=data.get("id", 0),
                        name=data.get("name", ""),
                        status=status,
                        conclusion=conclusion if status == CIStatus.FAILURE else None,
                        created_at=data.get("created_at", ""),
                        updated_at=data.get("updated_at", ""),
                        html_url=data.get("html_url", "")
                    )

                    workflows.append(workflow)

                except json.JSONDecodeError:
                    continue

            # 确定总体状态
            if checks_failed > 0:
                overall_status = CIStatus.FAILURE
            elif checks_pending > 0:
                overall_status = CIStatus.PENDING
            elif checks_passed > 0:
                overall_status = CIStatus.SUCCESS
            else:
                overall_status = CIStatus.UNKNOWN

            return CIResult(
                overall_status=overall_status,
                workflows=workflows,
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                checks_pending=checks_pending,
                details={"pr_url": pr_url, "pr_number": pr_number}
            )

        except Exception as e:
            return CIResult(
                overall_status=CIStatus.UNKNOWN,
                details={"error": str(e), "pr_url": pr_url}
            )

    def _extract_pr_number(self, pr_url: str) -> Optional[int]:
        """从 PR URL 提取 PR number

        Args:
            pr_url: PR URL

        Returns:
            Optional[int]: PR number，如果解析失败则返回 None
        """
        # GitHub PR URL 格式: https://github.com/owner/repo/pull/123
        match = re.search(r'/pull/(\d+)', pr_url)
        if match:
            return int(match.group(1))
        return None

    def wait_for_ci(
        self,
        pr_url: str,
        timeout: int = 600,
        poll_interval: int = 30
    ) -> CIResult:
        """等待 CI 完成

        Args:
            pr_url: PR URL
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）

        Returns:
            CIResult: 最终 CI 结果
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.check_ci_status(pr_url)

            # 如果状态不再是 PENDING 或 RUNNING，返回结果
            if result.overall_status in [CIStatus.SUCCESS, CIStatus.FAILURE, CIStatus.ERROR]:
                return result

            # 等待下一次轮询
            time.sleep(poll_interval)

        # 超时
        return CIResult(
            overall_status=CIStatus.UNKNOWN,
            details={"error": f"CI check timed out after {timeout}s", "pr_url": pr_url}
        )

    def rerun_workflow(self, pr_url: str, workflow: Optional[str] = None) -> RerunResult:
        """重新运行 workflow

        Args:
            pr_url: PR URL
            workflow: workflow 名称，如果为 None 则 rerun 所有失败的 workflow

        Returns:
            RerunResult: Rerun 结果
        """
        try:
            pr_number = self._extract_pr_number(pr_url)

            if not pr_number:
                return RerunResult(
                    success=False,
                    error=f"Invalid PR URL: {pr_url}"
                )

            # 获取 PR 的检查状态
            args = [
                "api",
                f"repos/{self.repo}/pulls/{pr_number}/checks",
                "--jq", '.check_runs[] | .id'
            ]

            output = self._run_gh(args)

            workflow_ids = []
            for line in output.split('\n'):
                if line.strip():
                    workflow_ids.append(int(line.strip()))

            if not workflow_ids:
                return RerunResult(
                    success=False,
                    error="No workflows found"
                )

            # Rerun workflow(s)
            if workflow:
                # Rerun 特定 workflow
                # 先找到匹配的 workflow ID
                args = [
                    "api",
                    f"repos/{self.repo}/pulls/{pr_number}/checks",
                    "--jq", f'.check_runs[] | select(.name=="{workflow}") | .id'
                ]

                output = self._run_gh(args)
                workflow_ids = [int(line.strip()) for line in output.split('\n') if line.strip()]

                if not workflow_ids:
                    return RerunResult(
                        success=False,
                        error=f"Workflow '{workflow}' not found"
                    )

            # Rerun 每个 workflow
            rerun_count = 0
            for workflow_id in workflow_ids:
                try:
                    args = [
                        "api",
                        "--method", "POST",
                        f"repos/{self.repo}/actions/runs/{workflow_id}/rerun"
                    ]

                    self._run_gh(args)
                    rerun_count += 1

                except Exception as e:
                    # 继续尝试其他 workflows
                    continue

            if rerun_count == 0:
                return RerunResult(
                    success=False,
                    error="Failed to rerun any workflows"
                )

            return RerunResult(
                success=True,
                details={
                    "rerun_count": rerun_count,
                    "workflow": workflow,
                    "pr_url": pr_url
                }
            )

        except Exception as e:
            return RerunResult(
                success=False,
                error=str(e),
                details={"pr_url": pr_url}
            )

    def add_comment(self, pr_url: str, comment: str) -> bool:
        """添加评论

        Args:
            pr_url: PR URL
            comment: 评论内容

        Returns:
            bool: 是否成功
        """
        try:
            pr_number = self._extract_pr_number(pr_url)

            if not pr_number:
                raise ValueError(f"Invalid PR URL: {pr_url}")

            args = [
                "pr", "comment", str(pr_number),
                "--body", comment
            ]

            self._run_gh(args)
            return True

        except Exception:
            return False

    def is_high_risk(self, changes: List[str]) -> bool:
        """判断是否高风险改动

        Args:
            changes: 变更文件列表

        Returns:
            bool: 是否高风险
        """
        if not changes:
            return False

        for file_path in changes:
            file_path_lower = file_path.lower()

            for keyword in self.HIGH_RISK_KEYWORDS:
                if keyword in file_path_lower:
                    return True

        return False

    def generate_changelog(self, changes: List[str], spec_title: str) -> str:
        """生成 CHANGELOG

        Args:
            changes: 变更文件列表
            spec_title: spec 标题

        Returns:
            str: CHANGELOG 内容
        """
        lines = [
            "## Changes",
            "",
            f"- {spec_title}",
            ""
        ]

        # 按文件类型分组
        by_type: Dict[str, List[str]] = {}

        for file_path in changes:
            ext = Path(file_path).suffix

            if ext == ".py":
                file_type = "Python"
            elif ext in [".js", ".ts", ".jsx", ".tsx"]:
                file_type = "JavaScript/TypeScript"
            elif ext in [".md", ".txt"]:
                file_type = "Documentation"
            elif ext in [".yml", ".yaml"]:
                file_type = "Configuration"
            else:
                file_type = "Other"

            if file_type not in by_type:
                by_type[file_type] = []

            by_type[file_type].append(file_path)

        # 输出按类型分组的文件
        for file_type in sorted(by_type.keys()):
            lines.append(f"### {file_type}")
            lines.append("")
            for file_path in sorted(by_type[file_type]):
                lines.append(f"- {file_path}")
            lines.append("")

        return "\n".join(lines)


# 测试验证
if __name__ == "__main__":
    import sys

    # 测试基本初始化
    try:
        bot = PRBot()
        print(f"PRBot initialized for repo: {bot.repo}")
        print(f"High risk keywords: {len(bot.HIGH_RISK_KEYWORDS)}")

        # 测试高风险判断
        test_files = [
            "app/auth/login.py",
            "app/user/profile.py",
            "app/payment/stripe.py",
            "docs/api.md",
            "app/security/jwt.py",
            "app/utils/helpers.py"
        ]

        high_risk = [f for f in test_files if bot.is_high_risk([f])]
        print(f"\nHigh risk files: {high_risk}")

        print("\n✓ PRBot initialized successfully")

    except Exception as e:
        print(f"✗ PRBot initialization failed: {e}")
        sys.exit(1)
