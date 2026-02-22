import re
from uuid import UUID, uuid4

from agent_sdk.models import SubTask, TaskDAG


class TaskRouter:
    def __init__(self):
        self.complexity_keywords = {
            "simple": ["get", "fetch", "read", "list", "show", "display"],
            "medium": ["create", "update", "modify", "process", "analyze"],
            "complex": ["build", "deploy", "migrate", "transform", "integrate"],
        }

    def parse_and_decompose(self, description: str, context: dict = None) -> TaskDAG:
        context = context or {}
        dag = TaskDAG()
        
        keywords = self._extract_keywords(description.lower())
        complexity = self._determine_complexity(keywords)
        
        if complexity == "simple":
            task = SubTask(
                id=uuid4(),
                name="Execute Task",
                description=description,
            )
            dag.tasks.append(task)
        
        elif complexity == "medium":
            sub_tasks = self._create_medium_tasks(description, context)
            dag.tasks.extend(sub_tasks)
        
        else:
            sub_tasks = self._create_complex_tasks(description, context)
            dag.tasks.extend(sub_tasks)
        
        return dag

    def _extract_keywords(self, text: str) -> list[str]:
        words = re.findall(r'\b\w+\b', text)
        return words

    def _determine_complexity(self, keywords: list[str]) -> str:
        score = 0
        for keyword in keywords:
            for level, level_keywords in self.complexity_keywords.items():
                if keyword in level_keywords:
                    if level == "simple":
                        score -= 1
                    elif level == "medium":
                        score += 1
                    elif level == "complex":
                        score += 2
        
        if score <= 0:
            return "simple"
        elif score <= 3:
            return "medium"
        else:
            return "complex"

    def _create_medium_tasks(self, description: str, context: dict) -> list[SubTask]:
        tasks = []
        
        analyze_task = SubTask(
            id=uuid4(),
            name="Analyze Requirements",
            description=f"Analyze: {description}",
        )
        tasks.append(analyze_task)
        
        execute_task = SubTask(
            id=uuid4(),
            name="Execute Task",
            description=description,
            dependencies=[analyze_task.id],
        )
        tasks.append(execute_task)
        
        return tasks

    def _create_complex_tasks(self, description: str, context: dict) -> list[SubTask]:
        tasks = []
        
        analyze_task = SubTask(
            id=uuid4(),
            name="Analyze Requirements",
            description=f"Analyze: {description}",
        )
        tasks.append(analyze_task)
        
        plan_task = SubTask(
            id=uuid4(),
            name="Plan Execution",
            description=f"Plan for: {description}",
            dependencies=[analyze_task.id],
        )
        tasks.append(plan_task)
        
        execute_task = SubTask(
            id=uuid4(),
            name="Execute Task",
            description=description,
            dependencies=[plan_task.id],
        )
        tasks.append(execute_task)
        
        verify_task = SubTask(
            id=uuid4(),
            name="Verify Result",
            description=f"Verify: {description}",
            dependencies=[execute_task.id],
        )
        tasks.append(verify_task)
        
        return tasks

    def decompose(self, request) -> TaskDAG:
        return self.parse_and_decompose(request.description, getattr(request, 'context', None))

    def _is_simple_task(self, description: str) -> bool:
        return not any(keyword in description for keyword in ["and", "then", "after", "before"])

    def _create_simple_dag(self, request) -> TaskDAG:
        task = SubTask(
            id=uuid4(),
            name="Execute Task",
            description=request.description,
            dependencies=[],
        )
        return TaskDAG(tasks=[task])

    def _create_compound_dag(self, request) -> TaskDAG:
        parts = self._split_description(request.description)
        tasks = []
        
        for i, part in enumerate(parts):
            dependencies = []
            if i > 0:
                dependencies.append(tasks[i - 1].id)
            
            task = SubTask(
                id=uuid4(),
                name=f"Task {i+1}",
                description=part.strip(),
                dependencies=dependencies,
            )
            tasks.append(task)
        
        return TaskDAG(tasks=tasks)

    def _split_description(self, description: str) -> list[str]:
        separators = [" and ", " then ", " after ", " before "]
        
        for sep in separators:
            if sep in description.lower():
                parts = description.lower().split(sep)
                return [p.strip() for p in parts if p.strip()]
        
        return [description]

    def estimate_complexity(self, description: str) -> int:
        score = 0
        desc_lower = description.lower()
        
        for keyword in ["and", "then", "after", "before"]:
            if keyword in desc_lower:
                score += 1
        
        if "pipeline" in desc_lower:
            score += 2
        if "workflow" in desc_lower:
            score += 2
            
        return min(score + 1, 10)
