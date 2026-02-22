#!/usr/bin/env python3
"""
Agent Teams Bridge - Connects dispatch to Claude Code Agent Teams

This module provides a bridge between the dispatch scheduling system and
Claude Code's Agent Teams functionality, enabling intelligent task decomposition,
dynamic replanning, and cross-agent communication.
"""

import json
import os
import uuid
import subprocess
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import threading


class TeamStatus(Enum):
    """Status of an agent team"""
    SPAWNING = "spawning"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    SHUTDOWN = "shutdown"


class AgentStatus(Enum):
    """Status of an individual agent/teammate"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Teammate:
    """Represents a single agent/teammate in a team"""
    id: str
    name: str
    model: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    assigned_subtasks: List[str] = field(default_factory=list)
    completed_subtasks: List[str] = field(default_factory=list)
    failed_subtasks: List[str] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result["status"] = self.status.value
        return result


@dataclass
class Team:
    """Represents an agent team"""
    id: str
    task_id: str
    status: TeamStatus = TeamStatus.SPAWNING
    teammates: List[Teammate] = field(default_factory=list)
    spawned_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_cost_usd: float = 0.0
    budget_usd: float = 10.0
    auto_reallocate: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result["status"] = self.status.value
        result["teammates"] = [t.to_dict() for t in self.teammates]
        return result


class AgentTeamsBridge:
    """
    Bridge between dispatch and Claude Code Agent Teams

    This class manages the lifecycle of agent teams, monitors their progress,
    handles failures with reallocation, and provides cost tracking.
    """

    # Environment variable for enabling Agent Teams
    ENV_ENABLED = "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Agent Teams Bridge

        Args:
            config_path: Path to agent_teams_config.json. If None, uses default location.
        """
        self.config_path = config_path or self._find_config()
        self.config = self.load_config()

        # Team storage
        self._teams: Dict[str, Team] = {}
        self._lock = threading.Lock()

        # Monitoring threads
        self._monitor_threads: Dict[str, threading.Thread] = {}
        self._running = True

    def _find_config(self) -> str:
        """
        Find agent_teams_config.json in the project

        Returns:
            Path to config file
        """
        # Start from script location and search upwards
        current = Path(__file__).resolve().parent

        while current != current.parent:
            config_path = current / "agent_teams_config.json"
            if config_path.exists():
                return str(config_path)
            current = current.parent

        # Fallback: create default config
        default_path = Path(__file__).resolve().parent / "agent_teams_config.json"
        self._create_default_config(default_path)
        return str(default_path)

    def _create_default_config(self, config_path: Path):
        """Create default configuration file"""
        default_config = {
            "enabled": False,
            "threshold_complexity": 5,
            "model_mapping": {
                "complex": "claude-opus",
                "medium": "claude-sonnet",
                "simple": "claude-haiku"
            },
            "max_teammates": 5,
            "auto_reallocate": True,
            "cost_budget_per_task": 10.0,
            "cost_strategy": {
                "simple_threshold_chars": 500,
                "complex_threshold_chars": 2000,
                "retry_model": "haiku",
                "code_review_model": "sonnet"
            }
        }

        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file

        Returns:
            Configuration dictionary
        """
        with open(self.config_path) as f:
            return json.load(f)

    def reload_config(self):
        """Hot reload configuration"""
        self.config = self.load_config()

    def is_enabled(self) -> bool:
        """
        Check if Agent Teams is enabled

        Returns:
            True if enabled via config or environment variable
        """
        # Environment variable takes precedence
        env_enabled = os.environ.get(self.ENV_ENABLED, "").lower() in ("1", "true", "yes")
        if env_enabled:
            return True

        # Fall back to config
        return self.config.get("enabled", False)

    def get_complexity_threshold(self) -> int:
        """
        Get complexity threshold for enabling Agent Teams

        Returns:
            Number of subtasks needed to trigger Agent Teams
        """
        return self.config.get("threshold_complexity", 5)

    def get_max_teammates(self) -> int:
        """
        Get maximum number of teammates per team

        Returns:
            Maximum teammates
        """
        return self.config.get("max_teammates", 5)

    def get_cost_budget(self) -> float:
        """
        Get cost budget per task

        Returns:
            Budget in USD
        """
        return self.config.get("cost_budget_per_task", 10.0)

    def spawn_team(self, task: Dict[str, Any], subtasks: List[Dict[str, Any]]) -> str:
        """
        Spawn an agent team for a complex task

        Args:
            task: Parent task dictionary with 'id', 'project', etc.
            subtasks: List of subtask dictionaries from TaskDecomposer

        Returns:
            Team ID

        Raises:
            RuntimeError: If Agent Teams is not enabled or budget exceeded
        """
        if not self.is_enabled():
            raise RuntimeError("Agent Teams is not enabled")

        # Check if complex enough
        num_subtasks = len(subtasks)
        if num_subtasks < self.get_complexity_threshold():
            raise RuntimeError(
                f"Task {task['id']} has only {num_subtasks} subtasks, "
                f"below threshold {self.get_complexity_threshold()}"
            )

        # Check cost budget
        from .task_decomposer import TaskDecomposer
        decomposer = TaskDecomposer()
        cost_report = decomposer.calculate_cost(subtasks)
        if cost_report["total_cost_usd"] > self.get_cost_budget():
            raise RuntimeError(
                f"Estimated cost ${cost_report['total_cost_usd']:.4f} "
                f"exceeds budget ${self.get_cost_budget():.2f}"
            )

        # Create team
        team_id = f"team-{task['id']}-{uuid.uuid4().hex[:8]}"
        teammates = self._create_teammates(subtasks)

        team = Team(
            id=team_id,
            task_id=task["id"],
            teammates=teammates,
            budget_usd=self.get_cost_budget(),
            auto_reallocate=self.config.get("auto_reallocate", True),
            total_cost_usd=cost_report["total_cost_usd"]
        )

        with self._lock:
            self._teams[team_id] = team

        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self._monitor_team_loop,
            args=(team_id,),
            daemon=True
        )
        monitor_thread.start()
        self._monitor_threads[team_id] = monitor_thread

        print(f"[AgentTeams] Spawned team {team_id} with {len(teammates)} teammates")
        print(f"[AgentTeams] Estimated cost: ${cost_report['total_cost_usd']:.4f}")

        return team_id

    def _create_teammates(self, subtasks: List[Dict[str, Any]]) -> List[Teammate]:
        """
        Create teammates from subtasks

        Args:
            subtasks: List of subtask dictionaries

        Returns:
            List of Teammate objects
        """
        teammates = []
        max_teammates = self.get_max_teammates()

        for i, subtask in enumerate(subtasks[:max_teammates]):
            teammate_id = f"agent-{i+1}-{uuid.uuid4().hex[:6]}"
            teammate = Teammate(
                id=teammate_id,
                name=f"Agent {i+1}",
                model=subtask.get("model", "sonnet")
            )
            teammates.append(teammate)

        # Assign subtasks to teammates (round-robin)
        for i, subtask in enumerate(subtasks):
            teammate = teammates[i % len(teammates)]
            teammate.assigned_subtasks.append(subtask["task"])

        return teammates

    def _monitor_team_loop(self, team_id: str):
        """
        Background thread to monitor team status

        Args:
            team_id: Team ID to monitor
        """
        while self._running:
            with self._lock:
                team = self._teams.get(team_id)
                if not team or team.status in (TeamStatus.COMPLETED, TeamStatus.FAILED, TeamStatus.SHUTDOWN):
                    break

            # Check status and handle failures
            self._check_and_handle_failures(team_id)

            # Update status
            self._update_team_status(team_id)

            # Sleep before next check
            time.sleep(5)

    def monitor_team(self, team_id: str) -> Dict[str, Any]:
        """
        Get current status of a team

        Args:
            team_id: Team ID

        Returns:
            Team status dictionary

        Raises:
            KeyError: If team ID not found
        """
        with self._lock:
            team = self._teams.get(team_id)
            if not team:
                raise KeyError(f"Team {team_id} not found")

            return team.to_dict()

    def _check_and_handle_failures(self, team_id: str):
        """
        Check for failed tasks and handle reallocation

        Args:
            team_id: Team ID to check
        """
        with self._lock:
            team = self._teams.get(team_id)
            if not team or not team.auto_reallocate:
                return

        for teammate in team.teammates:
            if teammate.status == AgentStatus.FAILED and teammate.failed_subtasks:
                # Reallocate failed subtasks
                for failed_task in teammate.failed_subtasks:
                    self.reallocate(team_id, failed_task)

    def reallocate(self, team_id: str, failed_task: str):
        """
        Reallocate a failed task to another teammate

        Args:
            team_id: Team ID
            failed_task: Task description that failed

        Raises:
            KeyError: If team ID not found
            RuntimeError: If no available teammates
        """
        with self._lock:
            team = self._teams.get(team_id)
            if not team:
                raise KeyError(f"Team {team_id} not found")

            # Find available teammate
            available_teammate = None
            for teammate in team.teammates:
                if teammate.status in (AgentStatus.IDLE, AgentStatus.COMPLETED):
                    available_teammate = teammate
                    break

            if not available_teammate:
                raise RuntimeError(f"No available teammates to reallocate task: {failed_task}")

            # Reassign task
            available_teammate.assigned_subtasks.append(failed_task)
            available_teammate.status = AgentStatus.WORKING
            available_teammate.current_task = failed_task

            print(f"[AgentTeams] Reallocated '{failed_task}' to {available_teammate.name}")

    def _update_team_status(self, team_id: str):
        """
        Update overall team status based on teammates

        Args:
            team_id: Team ID to update
        """
        with self._lock:
            team = self._teams.get(team_id)
            if not team:
                return

            if team.status == TeamStatus.SPAWNING:
                team.status = TeamStatus.RUNNING
                team.started_at = datetime.now().isoformat()

            # Check if all teammates completed
            all_completed = all(
                t.status == AgentStatus.COMPLETED
                for t in team.teammates
            )

            any_failed = any(
                t.status == AgentStatus.FAILED
                for t in team.teammates
            )

            if all_completed:
                team.status = TeamStatus.COMPLETED
                team.completed_at = datetime.now().isoformat()
            elif any_failed and team.status != TeamStatus.RUNNING:
                team.status = TeamStatus.FAILED

    def get_all_teams(self) -> List[Dict[str, Any]]:
        """
        Get status of all teams

        Returns:
            List of team status dictionaries
        """
        with self._lock:
            return [team.to_dict() for team in self._teams.values()]

    def shutdown_team(self, team_id: str):
        """
        Shutdown a team and release resources

        Args:
            team_id: Team ID to shutdown

        Raises:
            KeyError: If team ID not found
        """
        with self._lock:
            team = self._teams.get(team_id)
            if not team:
                raise KeyError(f"Team {team_id} not found")

            team.status = TeamStatus.SHUTDOWN

        # Stop monitoring thread
        if team_id in self._monitor_threads:
            thread = self._monitor_threads[team_id]
            if thread.is_alive():
                # Thread will exit on next loop iteration
                pass

        print(f"[AgentTeams] Shutdown team {team_id}")

    def get_cost_report(self, team_id: str) -> Dict[str, Any]:
        """
        Generate cost report for a team

        Args:
            team_id: Team ID

        Returns:
            Cost report dictionary
        """
        with self._lock:
            team = self._teams.get(team_id)
            if not team:
                raise KeyError(f"Team {team_id} not found")

        # Calculate per-teammate costs
        teammate_costs = []
        for teammate in team.teammates:
            cost = self._estimate_teammate_cost(teammate)
            teammate_costs.append({
                "name": teammate.name,
                "model": teammate.model,
                "tasks_completed": len(teammate.completed_subtasks),
                "estimated_cost_usd": cost
            })

        return {
            "team_id": team_id,
            "task_id": team.task_id,
            "budget_usd": team.budget_usd,
            "total_estimated_cost_usd": team.total_cost_usd,
            "teammate_breakdown": teammate_costs,
            "status": team.status.value
        }

    def _estimate_teammate_cost(self, teammate: Teammate) -> float:
        """
        Estimate cost for a teammate

        Args:
            teammate: Teammate object

        Returns:
            Estimated cost in USD
        """
        # Approximate costs per million tokens
        COST_PER_1M_TOKENS = {
            "haiku": 0.5,
            "sonnet": 9.0,
            "opus": 90.0
        }

        # Rough estimate: each task ~2500 tokens total
        tokens_per_task = 2500
        num_tasks = len(teammate.completed_subtasks) + len(teammate.assigned_subtasks)

        model_cost = COST_PER_1M_TOKENS.get(teammate.model, 9.0)
        total_tokens = num_tasks * tokens_per_task

        return (total_tokens / 1_000_000) * model_cost

    def shutdown_all(self):
        """Shutdown all teams and stop monitoring"""
        self._running = False

        team_ids = list(self._teams.keys())
        for team_id in team_ids:
            try:
                self.shutdown_team(team_id)
            except KeyError:
                pass

        # Wait for threads to finish
        for thread in self._monitor_threads.values():
            if thread.is_alive():
                thread.join(timeout=2)

        self._teams.clear()
        self._monitor_threads.clear()

        print("[AgentTeams] Shutdown all teams")


def create_agent_teams_bridge(config_path: Optional[str] = None) -> AgentTeamsBridge:
    """
    Factory function to create AgentTeamsBridge instance

    Args:
        config_path: Path to config file

    Returns:
        AgentTeamsBridge instance
    """
    return AgentTeamsBridge(config_path=config_path)


if __name__ == "__main__":
    # Example usage
    import sys

    # Enable Agent Teams for testing
    os.environ["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = "true"

    # Create bridge
    bridge = AgentTeamsBridge()

    print(f"Agent Teams Enabled: {bridge.is_enabled()}")
    print(f"Complexity Threshold: {bridge.get_complexity_threshold()}")
    print(f"Max Teammates: {bridge.get_max_teammates()}")
    print(f"Cost Budget: ${bridge.get_cost_budget():.2f}")

    # Example task and subtasks
    example_task = {
        "id": "example-task",
        "project": "test-project"
    }

    example_subtasks = [
        {"task": "Implement feature X", "model": "sonnet", "priority": 1},
        {"task": "Write tests", "model": "sonnet", "priority": 2},
        {"task": "Update docs", "model": "haiku", "priority": 3},
        {"task": "Code review", "model": "sonnet", "priority": 4},
        {"task": "Deploy", "model": "haiku", "priority": 5}
    ]

    try:
        team_id = bridge.spawn_team(example_task, example_subtasks)
        print(f"\nSpawned team: {team_id}")

        # Check status
        time.sleep(1)
        status = bridge.monitor_team(team_id)
        print(f"\nTeam Status: {json.dumps(status, indent=2)}")

        # Get cost report
        cost_report = bridge.get_cost_report(team_id)
        print(f"\nCost Report: {json.dumps(cost_report, indent=2)}")

        # Cleanup
        bridge.shutdown_team(team_id)

    except Exception as e:
        print(f"Error: {e}")
