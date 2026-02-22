#!/usr/bin/env python3
"""
Self-Acting Orchestrator - Autonomous module coordination

This module orchestrates autonomous collaboration between Browser-Use,
Mem0, and LangGraph modules to form a self-improving loop:

发现问题 → 记忆 → 推理 → 行动 → 验证 → 学习

The orchestrator:
1. Listens to events from all modules
2. Analyzes errors and findings
3. Makes decisions about corrective actions
4. Executes actions autonomously
5. Learns from outcomes
"""

import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ActionDecision:
    """Represents a decision to take an action"""

    action_type: str  # "retry", "fix", "escalate", "learn"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    requires_approval: bool
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        return result


@dataclass
class LearningEntry:
    """Represents a learning entry from experience"""

    lesson: str
    pattern: str
    success_rate: float
    applications: int
    last_applied: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        return result


class SelfOrchestrator:
    """
    Self-acting orchestrator for autonomous module coordination

    Coordinates Browser-Use, Mem0, and LangGraph through the event bus
    to enable autonomous decision-making and self-improvement.

    Flow:
    1. Subscribe to events (error.detected, finding.found, task.completed)
    2. On event:
       a. Store in memory (Mem0)
       b. Analyze with reasoning (LangGraph)
       c. Decide action (retry, fix, escalate)
       d. Execute action (Browser-Use if needed)
       e. Verify and learn from outcome

    Example:
        from dispatch.event_bus import EventBus, EventTypes
        from dispatch.memory_store import DispatchMemory
        from dispatch.browser_agent import DispatchBrowserAgent
        from dispatch.self_orchestrator import SelfOrchestrator

        # Create components
        event_bus = EventBus()
        memory = DispatchMemory({"enabled": True, ...})
        browser = DispatchBrowserAgent()

        # Create orchestrator
        orchestrator = SelfOrchestrator(event_bus, memory, browser)

        # Events trigger autonomous actions
        event_bus.publish(EventTypes.ERROR_DETECTED, {
            "error": "Element not found",
            "task_id": "S01"
        })
    """

    def __init__(
        self,
        event_bus: Any,
        memory: Optional[Any] = None,
        browser: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize SelfOrchestrator

        Args:
            event_bus: EventBus instance for communication
            memory: DispatchMemory/MemoryStore instance for long-term memory (auto-created if None)
            browser: Optional DispatchBrowserAgent for actions
            config: Configuration dictionary with options:
                - enabled (bool): Enable orchestrator (default: True)
                - auto_fix_threshold (int): Severity threshold for auto-fix (default: 7)
                - max_auto_retries (int): Maximum auto-retry attempts (default: 3)
                - escalate_after (int): Escalate after N failures (default: 5)
                - learning_enabled (bool): Enable learning from experience (default: True)
                - require_approval_for (list): Action types requiring approval
        """
        self.event_bus = event_bus

        # Auto-create memory if not provided
        if memory is None:
            try:
                from memory_store import DispatchMemory

                memory = DispatchMemory()
                logger.info("Auto-created DispatchMemory for orchestrator")
            except Exception as e:
                logger.warning(f"Could not create memory: {e}")
                memory = None

        self.memory = memory
        self.browser = browser

        # Configuration
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.auto_fix_threshold = self.config.get("auto_fix_threshold", 7)
        self.max_auto_retries = self.config.get("max_auto_retries", 3)
        self.escalate_after = self.config.get("escalate_after", 5)
        self.learning_enabled = self.config.get("learning_enabled", True)
        self.require_approval_for = self.config.get(
            "require_approval_for", ["fix", "escalate"]
        )

        # Track actions
        self._action_history: List[Dict[str, Any]] = []
        self._retry_counts: Dict[str, int] = {}
        self._learning_patterns: List[LearningEntry] = []
        self._lock = threading.Lock()

        # Statistics
        self.stats = {
            "errors_handled": 0,
            "findings_handled": 0,
            "actions_taken": 0,
            "retries_performed": 0,
            "fixes_applied": 0,
            "escalations": 0,
            "lessons_learned": 0,
        }

        # Set up subscriptions
        self._setup_subscriptions()

        logger.info(f"SelfOrchestrator initialized (enabled={self.enabled})")

    def _setup_subscriptions(self) -> None:
        """Subscribe to relevant events"""
        try:
            from event_bus import EventTypes
        except ImportError:
            from dispatch.event_bus import EventTypes

        self.event_bus.subscribe(EventTypes.ERROR_DETECTED, self.on_error)
        self.event_bus.subscribe(EventTypes.FINDING_FOUND, self.on_finding)
        self.event_bus.subscribe(EventTypes.TASK_COMPLETED, self.on_completed)
        self.event_bus.subscribe(EventTypes.TASK_FAILED, self.on_task_failed)
        self.event_bus.subscribe(EventTypes.FIX_APPLIED, self.on_fix_applied)

        logger.info(
            "Subscribed to events: error.detected, finding.found, task.completed"
        )

    def on_error(self, data: Dict[str, Any]) -> None:
        """
        Handle error detection event

        Args:
            data: Event data with 'error', 'source', and optional 'task_id'
        """
        if not self.enabled:
            return

        error_msg = data.get("error", "Unknown error")
        source = data.get("source", "unknown")
        task_id = data.get("task_id")

        logger.info(f"Handling error: {error_msg} from {source}")
        self.stats["errors_handled"] += 1

        # 1. Memory: Store the error
        self._store_error(error_msg, source, data)

        # 2. Reasoning: Analyze the error
        decision = self._analyze_error(error_msg, source, data)

        # 3. Action: Execute decision
        if decision:
            self._execute_action_decision(decision, task_id)

    def on_finding(self, data: Dict[str, Any]) -> None:
        """
        Handle code audit finding

        Args:
            data: Event data with 'finding', 'severity', 'file', 'line'
        """
        if not self.enabled:
            return

        finding = data.get("finding", "Unknown issue")
        severity = data.get("severity", "medium")
        filepath = data.get("file", "unknown")
        line = data.get("line", 0)

        logger.info(f"Handling finding: {finding} (severity={severity})")
        self.stats["findings_handled"] += 1

        # 1. Memory: Store the finding
        self._store_finding(finding, severity, filepath, line, data)

        # 2. Assess severity
        severity_score = self._get_severity_score(severity)

        # 3. Auto-fix if severe enough
        if severity_score >= self.auto_fix_threshold:
            logger.info(
                f"Severity {severity_score} >= {self.auto_fix_threshold}, considering auto-fix"
            )
            decision = self._assess_fix_action(finding, severity_score, data)
            self._execute_action_decision(decision)

    def on_completed(self, data: Dict[str, Any]) -> None:
        """
        Handle task completion - learn from success

        Args:
            data: Event data with 'task_id', 'duration', 'outcome'
        """
        if not self.enabled or not self.learning_enabled:
            return

        task_id = data.get("task_id", "unknown")
        duration = data.get("duration", 0)
        outcome = data.get("outcome", "unknown")

        logger.info(f"Task completed: {task_id} in {duration:.2f}s")

        # Extract lessons
        lessons = self._extract_lessons(data)

        # Store in memory
        for lesson in lessons:
            self._store_lesson(lesson, task_id)

        # Reset retry count on success
        if task_id in self._retry_counts:
            del self._retry_counts[task_id]

    def on_task_failed(self, data: Dict[str, Any]) -> None:
        """
        Handle task failure

        Args:
            data: Event data with 'task_id', 'error', 'attempts'
        """
        if not self.enabled:
            return

        task_id = data.get("task_id", "unknown")
        error = data.get("error", "Unknown failure")

        logger.warning(f"Task failed: {task_id} - {error}")

        # Check retry count
        current_retries = self._retry_counts.get(task_id, 0)

        if current_retries < self.max_auto_retries:
            # Retry the task
            logger.info(f"Auto-retrying {task_id} (attempt {current_retries + 1})")
            self._retry_task(task_id, data)
        else:
            # Escalate
            logger.warning(f"Max retries reached for {task_id}, escalating")
            self._escalate_issue(task_id, error, data)

    def on_fix_applied(self, data: Dict[str, Any]) -> None:
        """
        Handle fix applied event - learn from the fix

        Args:
            data: Event data with 'issue', 'solution', 'source'
        """
        if not self.learning_enabled:
            return

        issue = data.get("issue", "unknown")
        solution = data.get("solution", "unknown")

        logger.info(f"Fix applied for: {issue}")

        # Learn the fix pattern
        self._learn_fix_pattern(issue, solution, data)

    def _store_error(
        self, error_msg: str, source: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Store error in memory"""
        mem_metadata = {"source": source, "type": "error"}
        if metadata:
            mem_metadata.update(metadata)

        memory_id = self.memory.add(
            f"Error: {error_msg}",
            user_id="orchestrator",
            memory_type="error",
            metadata=mem_metadata,
        )

        return memory_id

    def _store_finding(
        self,
        finding: str,
        severity: str,
        filepath: str,
        line: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Store code finding in memory"""
        mem_metadata = {
            "severity": severity,
            "file": filepath,
            "line": line,
            "type": "finding",
        }
        if metadata:
            mem_metadata.update(metadata)

        memory_id = self.memory.add(
            f"Finding: {finding}",
            user_id="orchestrator",
            memory_type="finding",
            metadata=mem_metadata,
        )

        return memory_id

    def _store_lesson(self, lesson: str, context: str) -> Optional[str]:
        """Store lesson in memory"""
        memory_id = self.memory.add(
            f"Lesson: {lesson}",
            user_id="orchestrator",
            memory_type="lesson",
            metadata={"context": context, "type": "success"},
        )

        if memory_id:
            self.stats["lessons_learned"] += 1

        return memory_id

    def _analyze_error(
        self, error_msg: str, source: str, data: Dict[str, Any]
    ) -> Optional[ActionDecision]:
        """
        Analyze error and decide on action

        Returns decision for retry, fix, or escalate
        """
        # Search for similar errors in memory
        similar = self.memory.search(
            error_msg, user_id="orchestrator", limit=3, memory_type="error"
        )

        # Check retry count
        task_id = data.get("task_id")
        current_retries = self._retry_counts.get(task_id, 0)

        # Decision logic
        if current_retries >= self.max_auto_retries:
            # Too many retries - escalate
            return ActionDecision(
                action_type="escalate",
                confidence=0.9,
                reasoning=f"Max retries ({self.max_auto_retries}) reached for {task_id}",
                requires_approval=False,
                metadata={"task_id": task_id, "error": error_msg},
            )

        # Check if error is retryable
        is_retryable = self._is_retryable_error(error_msg, source)

        if is_retryable:
            return ActionDecision(
                action_type="retry",
                confidence=0.8,
                reasoning=f"Retryable error: {error_msg}",
                requires_approval=False,
                metadata={"task_id": task_id},
            )

        # Check for known fixes in memory
        for mem in similar:
            if mem.get("metadata", {}).get("fix"):
                return ActionDecision(
                    action_type="fix",
                    confidence=0.7,
                    reasoning=f"Known fix found for similar error",
                    requires_approval="fix" in self.require_approval_for,
                    metadata={"fix": mem["metadata"]["fix"], "task_id": task_id},
                )

        # Default: escalate if not sure
        return ActionDecision(
            action_type="escalate",
            confidence=0.6,
            reasoning=f"Unknown error type: {error_msg}",
            requires_approval=False,
            metadata={"task_id": task_id, "error": error_msg},
        )

    def _assess_fix_action(
        self, finding: str, severity_score: int, data: Dict[str, Any]
    ) -> Optional[ActionDecision]:
        """Assess whether to auto-fix a finding"""
        if severity_score >= self.auto_fix_threshold:
            return ActionDecision(
                action_type="fix",
                confidence=severity_score / 10.0,
                reasoning=f"High severity ({severity_score}) finding requires fix",
                requires_approval="fix" in self.require_approval_for,
                metadata={"finding": finding, "severity": severity_score},
            )

        return None

    def _execute_action_decision(
        self, decision: ActionDecision, task_id: Optional[str] = None
    ) -> None:
        """Execute an action decision"""
        action_type = decision.action_type

        # Check if approval required
        if decision.requires_approval:
            logger.info(f"Action '{action_type}' requires approval, skipping")
            # In a real system, this would send notification
            return

        logger.info(f"Executing action: {action_type} - {decision.reasoning}")

        # Record action
        with self._lock:
            self._action_history.append(
                {
                    "action": action_type,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning,
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        self.stats["actions_taken"] += 1

        # Execute based on action type
        if action_type == "retry":
            self._execute_retry(task_id, decision.metadata)

        elif action_type == "fix":
            self._execute_fix(decision.metadata)

        elif action_type == "escalate":
            self._execute_escalation(task_id, decision.metadata)

    def _execute_retry(
        self, task_id: Optional[str], metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Execute retry action"""
        if task_id:
            self._retry_counts[task_id] = self._retry_counts.get(task_id, 0) + 1
            self.stats["retries_performed"] += 1

            # Use browser agent if available
            if self.browser and task_id:
                try:
                    # Try to extract task info
                    result = self.browser.get_task_history()
                    logger.info(
                        f"Retry attempt {self._retry_counts[task_id]} for {task_id}"
                    )
                except Exception as e:
                    logger.error(f"Browser agent retry failed: {e}")

    def _execute_fix(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Execute fix action"""
        self.stats["fixes_applied"] += 1

        # Get fix from metadata or search memory
        fix = None
        if metadata and "fix" in metadata:
            fix = metadata["fix"]
        else:
            # Search for similar fixes in memory
            query = metadata.get("finding") or metadata.get("error", "")
            similar = self.memory.search(query, user_id="orchestrator", limit=1)
            if similar and similar[0].get("metadata", {}).get("fix"):
                fix = similar[0]["metadata"]["fix"]

        if fix:
            logger.info(f"Applying fix: {fix}")
            # Publish fix event
            self.event_bus.publish(
                "fix.applied",
                {"fix": fix, "source": "orchestrator"},
                source="orchestrator",
            )
        else:
            logger.warning("No fix available")

    def _execute_escalation(
        self, task_id: Optional[str], metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Execute escalation action"""
        self.stats["escalations"] += 1

        issue = metadata.get("error") or metadata.get("finding", "unknown")
        logger.warning(f"Escalating issue: {issue}")

        # Publish escalation event
        self.event_bus.publish(
            "action.escalated",
            {"task_id": task_id, "issue": issue, "requires_human_intervention": True},
            source="orchestrator",
        )

    def _retry_task(self, task_id: str, data: Dict[str, Any]) -> None:
        """Retry a failed task"""
        self._retry_counts[task_id] = self._retry_counts.get(task_id, 0) + 1
        self.stats["retries_performed"] += 1

        # Publish retry event
        self.event_bus.publish(
            "action.retried",
            {
                "task_id": task_id,
                "attempt": self._retry_counts[task_id],
                "max_attempts": self.max_auto_retries,
            },
            source="orchestrator",
        )

    def _escalate_issue(self, task_id: str, error: str, data: Dict[str, Any]) -> None:
        """Escalate an issue to human attention"""
        self.stats["escalations"] += 1

        self.event_bus.publish(
            "action.escalated",
            {
                "task_id": task_id,
                "error": error,
                "attempts": self._retry_counts.get(task_id, 0),
                "requires_human_intervention": True,
            },
            source="orchestrator",
        )

    def _extract_lessons(self, data: Dict[str, Any]) -> List[str]:
        """Extract lessons from completed task"""
        lessons = []

        task_id = data.get("task_id", "unknown")
        duration = data.get("duration", 0)

        # Lesson about successful patterns
        if duration < 5:
            lessons.append(
                f"Task {task_id} completed quickly (<5s), indicating efficient pattern"
            )

        # Lesson about successful approaches
        approach = data.get("approach")
        if approach:
            lessons.append(f"Approach '{approach}' worked successfully for {task_id}")

        # Check for any custom lessons in metadata
        if "lessons" in data:
            lessons.extend(data["lessons"])

        return lessons

    def _learn_fix_pattern(
        self, issue: str, solution: str, data: Dict[str, Any]
    ) -> None:
        """Learn from applied fix"""
        # Update memory with the fix
        memory_text = f"Issue: {issue}. Solution: {solution}"

        self.memory.add(
            memory_text,
            user_id="orchestrator",
            memory_type="lesson",
            metadata={"fix": solution, "issue": issue, "type": "fix_pattern"},
        )

        # Track learning pattern
        with self._lock:
            # Check if we've seen this pattern before
            for pattern in self._learning_patterns:
                if pattern.pattern == solution:
                    pattern.applications += 1
                    pattern.last_applied = datetime.now().isoformat()
                    break
            else:
                # New pattern
                self._learning_patterns.append(
                    LearningEntry(
                        lesson=memory_text,
                        pattern=solution,
                        success_rate=1.0,
                        applications=1,
                        last_applied=datetime.now().isoformat(),
                    )
                )

    def _get_severity_score(self, severity: str) -> int:
        """Convert severity string to numeric score"""
        scores = {"low": 3, "medium": 5, "high": 8, "critical": 10}
        return scores.get(severity.lower(), 5)

    def _is_retryable_error(self, error_msg: str, source: str) -> bool:
        """Check if error is retryable"""
        retryable_patterns = [
            "timeout",
            "connection",
            "network",
            "temporary",
            "rate limit",
            "busy",
        ]

        error_lower = error_msg.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        with self._lock:
            action_history_summary = {
                "total_actions": len(self._action_history),
                "by_type": {},
            }
            for action in self._action_history:
                action_type = action.get("action", "unknown")
                action_history_summary["by_type"][action_type] = (
                    action_history_summary["by_type"].get(action_type, 0) + 1
                )

            learning_summary = {
                "patterns_learned": len(self._learning_patterns),
                "top_patterns": [
                    {"pattern": p.pattern, "applications": p.applications}
                    for p in sorted(
                        self._learning_patterns,
                        key=lambda x: x.applications,
                        reverse=True,
                    )[:5]
                ],
            }

        return {
            **self.stats,
            "action_history": action_history_summary,
            "learning_patterns": learning_summary,
            "retry_counts": dict(self._retry_counts),
        }

    def get_action_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent action history"""
        with self._lock:
            return self._action_history[-limit:]

    def clear_history(self) -> None:
        """Clear action history and reset counters"""
        with self._lock:
            self._action_history.clear()
            self._retry_counts.clear()
            self._learning_patterns.clear()

        # Reset stats but keep counts
        for key in self.stats:
            self.stats[key] = 0

        logger.info("Orchestrator history cleared")


def create_orchestrator(
    event_bus: Any,
    memory: Any,
    browser: Optional[Any] = None,
    config_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> SelfOrchestrator:
    """
    Factory function to create SelfOrchestrator instance

    Args:
        event_bus: EventBus instance
        memory: DispatchMemory instance
        browser: Optional DispatchBrowserAgent instance
        config_path: Path to config JSON file (optional)
        config: Direct config dictionary (optional)

    Returns:
        SelfOrchestrator instance
    """
    if config is None and config_path:
        try:
            with open(config_path) as f:
                config = json.load(f)
        except Exception:
            config = {}

    return SelfOrchestrator(
        event_bus=event_bus, memory=memory, browser=browser, config=config
    )


if __name__ == "__main__":
    # Example usage
    import sys
    from dispatch.event_bus import EventBus, EventTypes
    from dispatch.memory_store import DispatchMemory
    from dispatch.browser_agent import DispatchBrowserAgent

    print("Self-Acting Orchestrator - Autonomous Module Coordination\n")
    print("=" * 60)

    # Create components
    event_bus = EventBus()
    memory = DispatchMemory({"enabled": False})  # Disabled for demo
    browser = None  # Optional

    # Create orchestrator
    orchestrator = SelfOrchestrator(
        event_bus=event_bus,
        memory=memory,
        browser=browser,
        config={
            "enabled": True,
            "auto_fix_threshold": 7,
            "max_auto_retries": 3,
            "escalate_after": 5,
            "learning_enabled": True,
            "require_approval_for": ["fix"],
        },
    )

    # Simulate events
    print("\nSimulating events...\n")

    # Error event
    event_bus.publish(
        EventTypes.ERROR_DETECTED,
        {
            "error": "Connection timeout while accessing API",
            "source": "browser_agent",
            "task_id": "S01",
        },
    )

    # Finding event
    event_bus.publish(
        EventTypes.FINDING_FOUND,
        {
            "finding": "Hardcoded API key detected",
            "severity": "critical",
            "file": "config.py",
            "line": 42,
        },
    )

    # Task completion
    event_bus.publish(
        EventTypes.TASK_COMPLETED,
        {
            "task_id": "S00",
            "duration": 3.5,
            "outcome": "success",
            "approach": "async pattern",
        },
    )

    # Wait for processing
    import time

    time.sleep(0.5)

    # Show stats
    print("\n" + "=" * 60)
    print("Orchestrator Statistics:")
    print(json.dumps(orchestrator.get_stats(), indent=2))

    print("\nAction History:")
    for action in orchestrator.get_action_history():
        print(f"  {action['timestamp']}: {action['action']} - {action['reasoning']}")

    print("\n" + "=" * 60)
    print("Demo complete!")
