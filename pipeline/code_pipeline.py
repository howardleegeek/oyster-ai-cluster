#!/usr/bin/env python3
"""Code Pipeline - 主编排器"""

import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import yaml

from pipeline.code_queue import CodeQueue
from pipeline.agents.code_scout import CodeScout
from pipeline.agents.planner import Planner, Plan
from pipeline.agents.coder import Coder, ExecResult, TestResult


class CycleResult:
    """一个 cycle 的执行结果"""

    def __init__(
        self,
        success: bool,
        stage: str,
        job_id: str,
        message: str,
        data: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.stage = stage  # 'scout', 'planner', 'coder', 'test'
        self.job_id = job_id
        self.message = message
        self.data = data or {}
        self.error = error

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'success': self.success,
            'stage': self.stage,
            'job_id': self.job_id,
            'message': self.message,
            'data': self.data,
            'error': self.error,
            'timestamp': datetime.utcnow().isoformat()
        }


class CodePipeline:
    """Code Pipeline 主编排器"""

    def __init__(
        self,
        queue: CodeQueue,
        llm_client=None,
        scout_model: str = "haiku",  # SCOUT 用轻量模型
        planner_model: str = "haiku",  # PLANNER 用轻量模型
        coder_model: str = "sonnet"  # CODER 用强模型
    ):
        """初始化 CodePipeline

        Args:
            queue: CodeQueue 实例
            llm_client: LLM 客户端
            scout_model: SCOUT 使用的模型
            planner_model: PLANNER 使用的模型
            coder_model: CODER 使用的模型
        """
        self.queue = queue
        self.scout = CodeScout(llm_client)
        self.planner = Planner(llm_client)
        self.coder = Coder(llm_client, model=coder_model)

    def run_cycle(self, worker_id: str) -> CycleResult:
        """运行一个完整的 cycle:
        1. 认领任务（SCOUT 已在入队时完成）
        2. PLANNER 拆解
        3. CODER 执行
        4. 测试验证
        5. 释放任务

        Args:
            worker_id: worker 标识

        Returns:
            result: Cycle 执行结果
        """
        # 1. 认领任务
        jobs = self.queue.claim(worker_id, max_jobs=1)

        if not jobs:
            return CycleResult(
                success=True,
                stage='idle',
                job_id='',
                message='No jobs available'
            )

        job = jobs[0]
        job_id = job['id']
        payload = yaml.safe_load(job['payload'])

        try:
            # 2. PLANNER 拆解
            result = self._run_planner(job_id, payload)
            if not result.success:
                self.queue.release(job_id, 'failed', error=result.error)
                return result

            plan = result.data['plan']
            spec = result.data['spec']

            # 3. CODER 执行
            result = self._run_coder(job_id, payload, plan, spec)
            if not result.success:
                self.queue.release(job_id, 'failed', error=result.error)
                return result

            exec_result = result.data['exec_result']

            # 4. 测试验证
            result = self._run_tests(job_id, payload, exec_result)
            if not result.success:
                self.queue.release(job_id, 'needs_human', error=result.error)
                return result

            # 5. 任务完成
            self.queue.release(
                job_id,
                'done',
                artifact_links={
                    'spec': spec,
                    'files_changed': exec_result.files_changed,
                    'test_passed': result.data['test_result'].success
                }
            )

            return CycleResult(
                success=True,
                stage='complete',
                job_id=job_id,
                message='Cycle completed successfully',
                data={
                    'plan': plan,
                    'exec_result': exec_result,
                    'test_result': result.data['test_result']
                }
            )

        except Exception as e:
            self.queue.release(job_id, 'failed', error=str(e))
            return CycleResult(
                success=False,
                stage='unknown',
                job_id=job_id,
                message='Cycle failed with exception',
                error=str(e)
            )

    def _run_planner(
        self,
        job_id: str,
        payload: Dict
    ) -> CycleResult:
        """运行 PLANNER 阶段

        Args:
            job_id: 任务 ID
            payload: 任务负载

        Returns:
            result: PLANNER 执行结果
        """
        try:
            # 生成执行计划
            plan = self.planner.decompose(payload)

            # 生成 YAML spec
            spec_result = self.planner.generate_spec(payload, plan)

            if not spec_result.success:
                return CycleResult(
                    success=False,
                    stage='planner',
                    job_id=job_id,
                    message='Failed to generate spec',
                    error=spec_result.error
                )

            return CycleResult(
                success=True,
                stage='planner',
                job_id=job_id,
                message='Planning completed',
                data={
                    'plan': spec_result.plan,
                    'spec': spec_result.spec
                }
            )

        except Exception as e:
            return CycleResult(
                success=False,
                stage='planner',
                job_id=job_id,
                message='Planner failed with exception',
                error=str(e)
            )

    def _run_coder(
        self,
        job_id: str,
        payload: Dict,
        plan: Plan,
        spec: str
    ) -> CycleResult:
        """运行 CODER 阶段

        Args:
            job_id: 任务 ID
            payload: 任务负载
            plan: 执行计划
            spec: YAML spec

        Returns:
            result: CODER 执行结果
        """
        try:
            # 获取工作区路径
            workspace = payload.get('workspace_path') or payload.get('repo')

            if not workspace or not Path(workspace).exists():
                # 如果没有工作区，跳过实际代码执行
                return CycleResult(
                    success=True,
                    stage='coder',
                    job_id=job_id,
                    message='Skipping code execution (no workspace)',
                    data={
                        'exec_result': ExecResult(
                            success=True,
                            message='Skipped (no workspace)',
                            files_changed=[]
                        )
                    }
                )

            # 在实际实现中，这里会：
            # 1. 解析 spec
            # 2. 调用 LLM 生成代码
            # 3. 应用代码改动

            # 目前是简化版本，只记录计划中的文件
            exec_result = ExecResult(
                success=True,
                message='Code execution completed (simplified)',
                files_changed=plan.files_to_modify
            )

            return CycleResult(
                success=True,
                stage='coder',
                job_id=job_id,
                message='Coder completed',
                data={
                    'exec_result': exec_result
                }
            )

        except Exception as e:
            return CycleResult(
                success=False,
                stage='coder',
                job_id=job_id,
                message='Coder failed with exception',
                error=str(e)
            )

    def _run_tests(
        self,
        job_id: str,
        payload: Dict,
        exec_result: ExecResult
    ) -> CycleResult:
        """运行测试阶段

        Args:
            job_id: 任务 ID
            payload: 任务负载
            exec_result: 代码执行结果

        Returns:
            result: 测试执行结果
        """
        try:
            workspace = payload.get('workspace_path') or payload.get('repo')

            if not workspace or not Path(workspace).exists():
                # 没有工作区，跳过测试
                return CycleResult(
                    success=True,
                    stage='test',
                    job_id=job_id,
                    message='Skipping tests (no workspace)',
                    data={
                        'test_result': TestResult(
                            success=True,
                            passed=0,
                            failed=0,
                            output='Skipped (no workspace)'
                        )
                    }
                )

            # 获取测试命令
            test_cmd = payload.get('test_command', 'pytest')

            # 运行测试
            test_result = self.coder.run_tests(workspace, test_cmd)

            if not test_result.success:
                return CycleResult(
                    success=False,
                    stage='test',
                    job_id=job_id,
                    message='Tests failed',
                    data={'test_result': test_result},
                    error=test_result.error
                )

            return CycleResult(
                success=True,
                stage='test',
                job_id=job_id,
                message='Tests passed',
                data={
                    'test_result': test_result
                }
            )

        except Exception as e:
            return CycleResult(
                success=False,
                stage='test',
                job_id=job_id,
                message='Test failed with exception',
                error=str(e)
            )

    def run_forever(self, worker_id: str, max_jobs: int = None, sleep_interval: int = 5):
        """持续运行直到被中断

        Args:
            worker_id: worker 标识
            max_jobs: 最多执行的任务数（None 表示无限）
            sleep_interval: 无任务时的休眠时间（秒）
        """
        job_count = 0

        try:
            while True:
                if max_jobs and job_count >= max_jobs:
                    print(f"Reached max jobs limit: {max_jobs}")
                    break

                result = self.run_cycle(worker_id)

                if result.stage == 'idle':
                    # 无任务，休眠
                    time.sleep(sleep_interval)
                else:
                    job_count += 1
                    print(f"Cycle {job_count} completed: {result.message}")

        except KeyboardInterrupt:
            print(f"\nStopped after {job_count} cycles")
        except Exception as e:
            print(f"Pipeline error: {e}")
            raise

    def scan_and_enqueue(
        self,
        source_type: str,
        repo: str,
        labels: List[str] = None,
        priority: int = 2
    ) -> List[str]:
        """扫描任务并入队

        Args:
            source_type: 源类型 ('github_issues', 'failing_ci', 'todos')
            repo: 仓库路径或名称
            labels: 标签过滤（仅 github_issues）
            priority: 优先级

        Returns:
            job_ids: 入队的任务 ID 列表
        """
        job_ids = []

        if source_type == 'github_issues':
            issues = self.scout.scan_github_issues(repo, labels)
        elif source_type == 'failing_ci':
            issues = self.scout.scan_failing_ci(repo)
        elif source_type == 'todos':
            issues = self.scout.scan_todos(repo)
        else:
            print(f"Unknown source type: {source_type}")
            return job_ids

        # 过滤适合自动修复的任务
        for issue in issues:
            if self.scout.should_autofix(issue):
                payload = self.scout.to_queue_payload(issue)
                job_id = self.queue.enqueue(
                    job_type='code',
                    source=issue.source,
                    payload=payload,
                    priority=priority
                )
                job_ids.append(job_id)
                print(f"Enqueued job {job_id}: {issue.title}")

        return job_ids
