"""
Temporal Workflow Definitions for Dispatch System
==================================================

Architecture: 1 BatchWorkflow (orchestrator) + N TaskWorkflow (independent top-level)
Each spec runs as its own TOP-LEVEL workflow, directly visible in Temporal UI.
No child workflows — every task shows up in the main workflow list.

Fixes (2026-02-22):
- TOP-LEVEL workflows (not children) so every task visible in Temporal UI
- depends_on validation: check if external deps are merged before dispatch
- max_retries reduced from 10 to 4 (size diff early kill handles the rest)
- Layer-level gate: if >90% of a layer fails, skip subsequent layers
- Blocked tasks tracked separately from failures
"""

from datetime import timedelta
from typing import List, Optional
import asyncio

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from dataclasses import dataclass, field


# -- Data Models --


@dataclass
class TaskSpec:
    """A single coding task specification."""

    task_id: str
    project: str
    spec_file: str
    spec_content: str
    depends_on: List[str] = field(default_factory=list)
    estimated_minutes: int = 30
    max_retries: int = 4


@dataclass
class TaskResult:
    """Result of executing a task."""

    task_id: str
    status: str  # "completed" | "failed" | "blocked"
    output: str = ""
    error: str = ""
    duration_seconds: float = 0
    loc_added: int = 0
    loc_removed: int = 0
    files_changed: int = 0


# -- Dependency Check Activity --


@dataclass
class DepCheckRequest:
    """Request to check if a dependency branch has been merged."""

    project: str
    dep_task_id: str


@dataclass
class DepCheckResult:
    """Result of dependency check."""

    dep_task_id: str
    is_merged: bool
    branch_exists: bool
    detail: str = ""


@dataclass
class StartWorkflowRequest:
    """Request to start a top-level TaskWorkflow."""

    workflow_id: str
    spec: TaskSpec


@dataclass
class WaitWorkflowRequest:
    """Request to wait for a workflow to complete."""

    workflow_id: str
    timeout_minutes: int = 120


# -- Task Workflow (child, one per spec) --


@workflow.defn
class TaskWorkflow:
    """
    Executes a single coding task with fallback reflection.
    Each spec runs as its own workflow, visible in Temporal UI.
    """

    @workflow.run
    async def run(self, spec: TaskSpec) -> TaskResult:
        try:
            return await self._run_with_fallback(spec)
        except Exception as e:
            return TaskResult(
                task_id=spec.task_id,
                status="failed",
                error=str(e)[-2000:],
            )

    async def _run_with_fallback(self, spec: TaskSpec) -> TaskResult:
        """Dify-style fallback: if initial retries fail, rewrite spec and try alternative approach."""
        try:
            return await workflow.execute_activity(
                "run_coding_task",
                spec,
                result_type=TaskResult,
                start_to_close_timeout=timedelta(
                    minutes=max(spec.estimated_minutes * 4, 120)
                ),
                heartbeat_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=30),
                    backoff_coefficient=2.0,
                    maximum_attempts=spec.max_retries,
                    maximum_interval=timedelta(minutes=10),
                    non_retryable_error_types=[
                        "EmptyRun",
                        "OpencodeMissing",
                        "AllModelsExhausted",
                        "SyntaxError",
                        "ValueError",
                    ],
                ),
            )
        except Exception as e:
            workflow.logger.warning(
                f"{spec.task_id} stuck! Triggering Fallback Reflection."
            )

            fallback_spec = TaskSpec(
                task_id=spec.task_id,
                project=spec.project,
                spec_file=spec.spec_file,
                spec_content=spec.spec_content
                + f"\n\n## FALLBACK PROTOCOL INITIATED\nPrevious attempts continuously failed. Final error:\n```\n{str(e)[-1000:]}\n```\n\n**CRITICAL INSTRUCTION**: Abandon your previous approach. Simplify your solution, use alternative methods, or stub the functionality safely. Do NOT repeat the same mistakes.",
                depends_on=spec.depends_on,
                estimated_minutes=spec.estimated_minutes,
                max_retries=1,
            )

            try:
                return await workflow.execute_activity(
                    "run_coding_task",
                    fallback_spec,
                    result_type=TaskResult,
                    start_to_close_timeout=timedelta(
                        minutes=max(spec.estimated_minutes * 4, 120)
                    ),
                    heartbeat_timeout=timedelta(minutes=10),
                    retry_policy=RetryPolicy(maximum_attempts=1),
                )
            except Exception as fallback_e:
                workflow.logger.error(
                    f"{spec.task_id} completely failed. Sending to Repair Factory."
                )
                repair_path = await workflow.execute_activity(
                    "send_to_repair_factory",
                    args=[spec, str(fallback_e)],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(maximum_attempts=2),
                )
                return TaskResult(
                    task_id=spec.task_id,
                    status="needs_repair",
                    output=f"Task structurally failed. Root cause analysis generated at: {repair_path}",
                    duration_seconds=0,
                    loc_added=0,
                    loc_removed=0,
                    files_changed=0,
                )


# -- Batch Workflow (parent, orchestrates all children) --


@workflow.defn
class BatchWorkflow:
    """
    Orchestrates all tasks for a project via child workflows.
    Each spec becomes a separate TaskWorkflow visible in Temporal UI.
    """

    @workflow.run
    async def run(self, specs: List[TaskSpec]) -> dict:
        layers = self._build_layers(specs)

        results = []
        completed_task_ids = set()
        project = specs[0].project if specs else ""

        for layer_idx, layer in enumerate(layers):
            workflow.logger.info(f"Layer {layer_idx}: {len(layer)} tasks")

            # First pass: check dependencies
            spec_deps_map = {}
            external_deps_to_check = set()

            for spec in layer:
                internal_unmet = []
                external_unchecked = []
                for dep in spec.depends_on:
                    if dep in completed_task_ids:
                        continue
                    if dep in {s.task_id for s in specs}:
                        internal_unmet.append(dep)
                    else:
                        external_unchecked.append(dep)

                spec_deps_map[spec.task_id] = {
                    "spec": spec,
                    "blocked_by": internal_unmet.copy(),
                    "external_unchecked": external_unchecked,
                }
                external_deps_to_check.update(external_unchecked)

            # Check external deps
            if external_deps_to_check:
                check_futures = []
                ordered_checks = list(external_deps_to_check)
                for ext_dep in ordered_checks:
                    check_req = DepCheckRequest(project=project, dep_task_id=ext_dep)
                    fut = workflow.execute_activity(
                        "check_dependency_merged",
                        check_req,
                        result_type=DepCheckResult,
                        start_to_close_timeout=timedelta(minutes=2),
                        retry_policy=RetryPolicy(
                            initial_interval=timedelta(seconds=5),
                            maximum_attempts=3,
                        ),
                    )
                    check_futures.append(fut)

                check_results = await asyncio.gather(
                    *check_futures, return_exceptions=True
                )
                ext_results_map = {}
                for idx, res in enumerate(check_results):
                    dep_id = ordered_checks[idx]
                    if isinstance(res, Exception):
                        workflow.logger.warning(f"Error checking dep {dep_id}: {res}")
                        ext_results_map[dep_id] = False
                    else:
                        ext_results_map[dep_id] = res.is_merged

                for task_id, data in spec_deps_map.items():
                    for ext_dep in data["external_unchecked"]:
                        if not ext_results_map.get(ext_dep, False):
                            data["blocked_by"].append(f"{ext_dep} (external, unmerged)")

            # Separate runnable vs blocked
            runnable = []
            for task_id, data in spec_deps_map.items():
                blocked_deps = data["blocked_by"]
                spec = data["spec"]
                if blocked_deps:
                    workflow.logger.warning(
                        f"{task_id} BLOCKED: deps not met: {blocked_deps}"
                    )
                    results.append(
                        {
                            "task_id": task_id,
                            "status": "blocked",
                            "error": f"Blocked by unmet dependencies: {blocked_deps}",
                            "loc_added": 0,
                            "loc_removed": 0,
                            "files_changed": 0,
                            "duration_seconds": 0,
                            "output": "",
                        }
                    )
                else:
                    runnable.append(spec)

            if not runnable:
                workflow.logger.warning(
                    f"Layer {layer_idx}: all tasks blocked, skipping"
                )
                continue

            # Dispatch each spec as an INDEPENDENT top-level workflow (visible in Temporal UI)
            batch_run_id = workflow.info().run_id[:8]
            start_futures = []
            workflow_ids = []
            for spec in runnable:
                wf_id = f"spec-{project}-{spec.task_id}-{batch_run_id}"
                workflow_ids.append(wf_id)
                req = StartWorkflowRequest(workflow_id=wf_id, spec=spec)
                fut = workflow.execute_activity(
                    "start_task_workflow",
                    req,
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=RetryPolicy(maximum_attempts=3),
                )
                start_futures.append(fut)

            # Start all workflows in parallel
            await asyncio.gather(*start_futures, return_exceptions=True)

            # Wait for all workflows to complete
            wait_futures = []
            for i, spec in enumerate(runnable):
                req = WaitWorkflowRequest(
                    workflow_id=workflow_ids[i],
                    timeout_minutes=max(spec.estimated_minutes * 4, 120),
                )
                fut = workflow.execute_activity(
                    "wait_for_task_workflow",
                    req,
                    result_type=TaskResult,
                    start_to_close_timeout=timedelta(
                        minutes=max(spec.estimated_minutes * 4, 120) + 5
                    ),
                    heartbeat_timeout=timedelta(minutes=10),
                    retry_policy=RetryPolicy(maximum_attempts=2),
                )
                wait_futures.append(fut)

            layer_results = await asyncio.gather(*wait_futures, return_exceptions=True)

            layer_completed = 0
            layer_failed = 0

            for i, result in enumerate(layer_results):
                if isinstance(result, Exception):
                    layer_failed += 1
                    results.append(
                        {
                            "task_id": runnable[i].task_id,
                            "status": "failed",
                            "error": str(result),
                            "loc_added": 0,
                            "loc_removed": 0,
                            "files_changed": 0,
                            "duration_seconds": 0,
                            "output": "",
                        }
                    )
                else:
                    results.append(
                        {
                            "task_id": result.task_id,
                            "status": result.status,
                            "output": result.output,
                            "error": result.error,
                            "duration_seconds": result.duration_seconds,
                            "loc_added": result.loc_added,
                            "loc_removed": result.loc_removed,
                            "files_changed": result.files_changed,
                        }
                    )
                    if result.status in ("completed", "already_completed"):
                        layer_completed += 1
                        completed_task_ids.add(result.task_id)
                    elif result.status == "needs_repair":
                        layer_failed += 1
                    else:
                        layer_failed += 1

            workflow.logger.info(
                f"Layer {layer_idx} complete. Completed: {layer_completed}, Failed: {layer_failed}"
            )

            # Layer gate: if >90% failed, skip remaining layers
            total_in_layer = layer_completed + layer_failed
            if total_in_layer > 0 and layer_failed / total_in_layer > 0.9:
                remaining_count = sum(len(l) for l in layers[layer_idx + 1 :])
                if remaining_count > 0:
                    workflow.logger.warning(
                        f"Layer {layer_idx}: {layer_failed}/{total_in_layer} failed (>90%), "
                        f"skipping {remaining_count} remaining tasks"
                    )
                    for future_layer in layers[layer_idx + 1 :]:
                        for spec in future_layer:
                            results.append(
                                {
                                    "task_id": spec.task_id,
                                    "status": "blocked",
                                    "error": f"Blocked: previous layer {layer_idx} had >90% failure rate",
                                    "loc_added": 0,
                                    "loc_removed": 0,
                                    "files_changed": 0,
                                    "duration_seconds": 0,
                                    "output": "",
                                }
                            )
                    break

        completed = sum(1 for r in results if r["status"] == "completed")
        failed = sum(1 for r in results if r["status"] == "failed")
        blocked = sum(1 for r in results if r["status"] == "blocked")

        return {
            "project": project,
            "total": len(specs),
            "completed": completed,
            "failed": failed,
            "blocked": blocked,
            "results": results,
        }

    def _build_layers(self, specs: List[TaskSpec]) -> List[List[TaskSpec]]:
        """Topological sort specs into dependency layers."""
        spec_map = {s.task_id: s for s in specs}
        completed = set()
        layers = []

        remaining = set(spec_map.keys())
        while remaining:
            ready = [
                tid
                for tid in remaining
                if all(
                    dep in completed or dep not in spec_map
                    for dep in spec_map[tid].depends_on
                )
            ]
            if not ready:
                ready = list(remaining)

            layers.append([spec_map[tid] for tid in ready])
            completed.update(ready)
            remaining -= set(ready)

        return layers


# Keep backward compat: ProjectWorkflow as alias
ProjectWorkflow = BatchWorkflow
