#!/usr/bin/env python3
"""
Task Decomposer - AI-driven task decomposition for Agent Teams

This module uses AI to analyze task specifications and decompose complex tasks
into smaller, manageable subtasks with appropriate model assignments.
"""

import json
import os
import re
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class SubTask:
    """Represents a decomposed subtask"""
    task: str
    model: str
    priority: int
    estimated_minutes: Optional[int] = None
    depends_on: Optional[List[str]] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}


class TaskDecomposer:
    """AI-driven task decomposer for complex specifications"""

    # Model names supported by Claude
    MODELS = {
        "haiku": "claude-haiku-4-20250514",
        "sonnet": "claude-sonnet-4-5-20250929",
        "opus": "claude-opus-4-6-20250929"
    }

    # Complexity thresholds
    COMPLEXITY_THRESHOLDS = {
        "simple": 500,      # < 500 characters
        "medium": 2000,     # 500-2000 characters
        "complex": float('inf')  # > 2000 characters
    }

    # Complexity to model mapping
    COMPLEXITY_TO_MODEL = {
        "simple": "haiku",
        "medium": "sonnet",
        "complex": "opus"
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TaskDecomposer

        Args:
            api_key: Anthropic API key. If None, tries to read from environment.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def _estimate_complexity(self, spec_content: str) -> str:
        """
        Estimate task complexity based on spec content

        Args:
            spec_content: Task specification content

        Returns:
            Complexity level: "simple", "medium", or "complex"
        """
        # Count characters
        char_count = len(spec_content)

        # Count sections (headers, bullet points, code blocks)
        sections = len(re.findall(r'^#{1,6}\s+', spec_content, re.MULTILINE))
        code_blocks = len(re.findall(r'```', spec_content)) // 2
        bullet_points = len(re.findall(r'^\s*[-*]\s+', spec_content, re.MULTILINE))

        # Base complexity on character count
        if char_count < self.COMPLEXITY_THRESHOLDS["simple"]:
            complexity = "simple"
        elif char_count < self.COMPLEXITY_THRESHOLDS["medium"]:
            complexity = "medium"
        else:
            complexity = "complex"

        # Adjust complexity based on structure
        if sections > 5 or code_blocks > 3 or bullet_points > 10:
            # Upgrade complexity if highly structured
            if complexity == "simple":
                complexity = "medium"
            elif complexity == "medium":
                complexity = "complex"

        return complexity

    def _select_model(self, complexity: str, task_type: str = "general") -> str:
        """
        Select appropriate model based on complexity and task type

        Args:
            complexity: Complexity level ("simple", "medium", "complex")
            task_type: Type of task ("general", "code_review", "retry")

        Returns:
            Model name ("haiku", "sonnet", or "opus")
        """
        # Override for specific task types
        if task_type == "retry":
            return "haiku"
        if task_type == "code_review":
            return "sonnet"

        # Default complexity-based selection
        return self.COMPLEXITY_TO_MODEL.get(complexity, "sonnet")

    def _build_decomposition_prompt(self, spec_content: str) -> str:
        """
        Build prompt for AI decomposition

        Args:
            spec_content: Task specification content

        Returns:
            Formatted prompt for Claude
        """
        return f"""Analyze the following task specification and decompose it into smaller, actionable subtasks.

Task Specification:
---
{spec_content}
---

Instructions:
1. Break down the task into 2-5 logical subtasks
2. Each subtask should be independent or clearly dependent on others
3. Assign a priority (1 = highest) to each subtask
4. Estimate execution time for each subtask (in minutes)
5. Identify dependencies between subtasks if any

Respond in JSON format only, with this structure:
{{
    "subtasks": [
        {{
            "task": "Specific subtask description",
            "model": "haiku|sonnet|opus",
            "priority": 1-5,
            "estimated_minutes": 10,
            "depends_on": ["task_id_of_dependency"] or null,
            "description": "Brief explanation of what this subtask accomplishes"
        }}
    ]
}}

Model selection guidelines:
- haiku: Simple tasks, retries, documentation updates, < 500 chars
- sonnet: Code implementation, code review, 500-2000 chars, medium complexity
- opus: Complex architecture, research, > 2000 chars, high complexity
"""

    def _call_claude(self, prompt: str, model: str = "sonnet") -> str:
        """
        Call Claude API for task decomposition

        Args:
            prompt: The prompt to send
            model: Model to use

        Returns:
            Claude's response text
        """
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        model_name = self.MODELS.get(model, model)

        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Failed to call Claude API: {e}")

    def decompose(self, spec_content: str, use_ai: bool = False) -> List[Dict[str, Any]]:
        """
        Decompose a task specification into subtasks

        Args:
            spec_content: Task specification content
            use_ai: If True, use Claude AI for intelligent decomposition.
                     If False, use heuristic-based decomposition.

        Returns:
            List of subtask dictionaries with structure:
            [
                {
                    "task": "task description",
                    "model": "model_name",
                    "priority": 1,
                    "estimated_minutes": 10,
                    "depends_on": ["task_id"] or None,
                    "description": "explanation"
                },
                ...
            ]
        """
        if use_ai:
            return self._ai_decompose(spec_content)
        else:
            return self._heuristic_decompose(spec_content)

    def _ai_decompose(self, spec_content: str) -> List[Dict[str, Any]]:
        """
        Use AI to decompose the task

        Args:
            spec_content: Task specification content

        Returns:
            List of subtask dictionaries
        """
        # Determine complexity for model selection
        complexity = self._estimate_complexity(spec_content)
        model = self._select_model(complexity, task_type="general")

        # Build and send prompt
        prompt = self._build_decomposition_prompt(spec_content)
        response = self._call_claude(prompt, model=model)

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group(1))
            else:
                # Try to parse as pure JSON
                response_data = json.loads(response.strip())

            subtasks = response_data.get("subtasks", [])

            # Convert to SubTask objects
            result = []
            for idx, st in enumerate(subtasks):
                subtask = SubTask(
                    task=st.get("task", ""),
                    model=st.get("model", "sonnet"),
                    priority=st.get("priority", idx + 1),
                    estimated_minutes=st.get("estimated_minutes"),
                    depends_on=st.get("depends_on"),
                    description=st.get("description")
                )
                result.append(subtask.to_dict())

            return result

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse AI response as JSON: {e}\nResponse: {response}")

    def _heuristic_decompose(self, spec_content: str) -> List[Dict[str, Any]]:
        """
        Use heuristic rules to decompose the task (fallback when AI not available)

        Args:
            spec_content: Task specification content

        Returns:
            List of subtask dictionaries
        """
        complexity = self._estimate_complexity(spec_content)
        model = self._select_model(complexity)

        # Extract task name/ID from spec
        task_match = re.search(r'task_id:\s*(\S+)', spec_content)
        task_id = task_match.group(1) if task_match else "unknown"

        # Check for common patterns
        has_code = bool(re.search(r'```', spec_content))
        has_tests = bool(re.search(r'test|spec|coverage', spec_content, re.IGNORECASE))
        has_docs = bool(re.search(r'docs?|readme|documentation', spec_content, re.IGNORECASE))

        subtasks = []

        # Implementation task (always)
        subtasks.append(SubTask(
            task=f"Implement {task_id}",
            model=model,
            priority=1,
            estimated_minutes=self._estimate_time(complexity, "implementation"),
            description="Core implementation of the task"
        ))

        # Testing task (if mentioned or complex)
        if has_tests or complexity in ["medium", "complex"]:
            subtasks.append(SubTask(
                task=f"Write tests for {task_id}",
                model="sonnet",
                priority=2,
                estimated_minutes=self._estimate_time(complexity, "testing"),
                depends_on=[f"implement-{task_id}"],
                description="Write unit and integration tests"
            ))

        # Documentation task (if mentioned)
        if has_docs or complexity == "complex":
            subtasks.append(SubTask(
                task=f"Update documentation for {task_id}",
                model="haiku",
                priority=3,
                estimated_minutes=10,
                depends_on=[f"implement-{task_id}"],
                description="Update documentation and README"
            ))

        # Code review task (always for production)
        subtasks.append(SubTask(
            task=f"Code review for {task_id}",
            model="sonnet",
            priority=4,
            estimated_minutes=5,
            depends_on=[f"implement-{task_id}"],
            description="Review implementation for quality"
        ))

        return [st.to_dict() for st in subtasks]

    def _estimate_time(self, complexity: str, task_type: str) -> int:
        """
        Estimate execution time based on complexity and task type

        Args:
            complexity: Complexity level
            task_type: Type of task ("implementation", "testing", "documentation")

        Returns:
            Estimated minutes
        """
        base_times = {
            "simple": {"implementation": 10, "testing": 5, "documentation": 5},
            "medium": {"implementation": 30, "testing": 15, "documentation": 10},
            "complex": {"implementation": 60, "testing": 30, "documentation": 15}
        }

        return base_times.get(complexity, {}).get(task_type, 15)

    def calculate_cost(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate estimated cost for subtasks

        Args:
            subtasks: List of subtask dictionaries

        Returns:
            Cost breakdown dictionary
        """
        # Estimated costs per million tokens (USD) - approximate
        COST_PER_1M_TOKENS = {
            "haiku": {"input": 0.25, "output": 1.25},
            "sonnet": {"input": 3.00, "output": 15.00},
            "opus": {"input": 15.00, "output": 75.00}
        }

        # Estimated tokens per task (very rough estimate)
        ESTIMATED_TOKENS = {
            "input": 2000,
            "output": 500
        }

        total_cost = 0.0
        task_costs = []

        for task in subtasks:
            model = task.get("model", "sonnet")
            pricing = COST_PER_1M_TOKENS.get(model, COST_PER_1M_TOKENS["sonnet"])

            input_cost = (ESTIMATED_TOKENS["input"] / 1_000_000) * pricing["input"]
            output_cost = (ESTIMATED_TOKENS["output"] / 1_000_000) * pricing["output"]
            task_cost = input_cost + output_cost

            total_cost += task_cost
            task_costs.append({
                "task": task.get("task"),
                "model": model,
                "cost": round(task_cost, 4)
            })

        return {
            "total_cost_usd": round(total_cost, 4),
            "task_breakdown": task_costs
        }


def create_task_decomposer(api_key: Optional[str] = None) -> TaskDecomposer:
    """
    Factory function to create TaskDecomposer instance

    Args:
        api_key: Anthropic API key

    Returns:
        TaskDecomposer instance
    """
    return TaskDecomposer(api_key=api_key)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 task_decomposer.py <spec_file> [--ai]")
        sys.exit(1)

    spec_file = sys.argv[1]
    use_ai = "--ai" in sys.argv

    with open(spec_file) as f:
        spec_content = f.read()

    decomposer = TaskDecomposer()
    subtasks = decomposer.decompose(spec_content, use_ai=use_ai)

    print(f"\nDecomposed {len(subtasks)} subtasks:\n")
    for idx, task in enumerate(subtasks, 1):
        print(f"{idx}. {task['task']}")
        print(f"   Model: {task['model']}")
        print(f"   Priority: {task['priority']}")
        if task.get('estimated_minutes'):
            print(f"   Estimated time: {task['estimated_minutes']} minutes")
        if task.get('depends_on'):
            print(f"   Depends on: {', '.join(task['depends_on'])}")
        if task.get('description'):
            print(f"   Description: {task['description']}")
        print()

    # Calculate cost
    cost_report = decomposer.calculate_cost(subtasks)
    print(f"\nCost Report:")
    print(f"Total estimated cost: ${cost_report['total_cost_usd']}")
    print("\nBreakdown:")
    for tc in cost_report['task_breakdown']:
        print(f"  - {tc['task']}: ${tc['cost']} ({tc['model']})")
