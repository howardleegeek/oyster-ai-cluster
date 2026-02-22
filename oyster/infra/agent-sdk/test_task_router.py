import pytest
from agent_sdk.models import SubTask, TaskDAG, TaskStatus
from agent_sdk.task_router import TaskRouter


class TestTaskRouter:
    def test_parse_simple_task(self):
        router = TaskRouter()
        dag = router.parse_and_decompose("Get user information")
        
        assert len(dag.tasks) == 1
        assert dag.tasks[0].name == "Execute Task"
        assert dag.tasks[0].status == TaskStatus.PENDING

    def test_parse_medium_task(self):
        router = TaskRouter()
        dag = router.parse_and_decompose("Create a new user profile")
        
        assert len(dag.tasks) == 2
        assert dag.tasks[0].name == "Analyze Requirements"
        assert dag.tasks[1].name == "Execute Task"
        assert dag.tasks[1].dependencies[0] == dag.tasks[0].id

    def test_parse_complex_task(self):
        router = TaskRouter()
        dag = router.parse_and_decompose("Build and deploy a new microservice")
        
        assert len(dag.tasks) == 4
        assert dag.tasks[0].name == "Analyze Requirements"
        assert dag.tasks[1].name == "Plan Execution"
        assert dag.tasks[2].name == "Execute Task"
        assert dag.tasks[3].name == "Verify Result"

    def test_parse_with_context(self):
        router = TaskRouter()
        context = {"user_id": "123", "environment": "production"}
        dag = router.parse_and_decompose("Update configuration", context)
        
        assert len(dag.tasks) >= 1


class TestTaskDAG:
    def test_get_ready_tasks_all_pending(self):
        from uuid import uuid4
        
        task1 = SubTask(id=uuid4(), name="Task 1", description="Desc 1")
        task2 = SubTask(id=uuid4(), name="Task 2", description="Desc 2")
        
        dag = TaskDAG(tasks=[task1, task2])
        
        ready = dag.get_ready_tasks()
        assert len(ready) == 2

    def test_get_ready_tasks_with_dependencies(self):
        from uuid import uuid4
        
        task1 = SubTask(id=uuid4(), name="Task 1", description="Desc 1")
        task2 = SubTask(
            id=uuid4(),
            name="Task 2",
            description="Desc 2",
            dependencies=[task1.id],
        )
        
        dag = TaskDAG(tasks=[task1, task2])
        
        ready = dag.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == task1.id

    def test_get_ready_tasks_after_completion(self):
        from uuid import uuid4
        
        task1 = SubTask(
            id=uuid4(),
            name="Task 1",
            description="Desc 1",
            status=TaskStatus.COMPLETED,
        )
        task2 = SubTask(
            id=uuid4(),
            name="Task 2",
            description="Desc 2",
            dependencies=[task1.id],
        )
        
        dag = TaskDAG(tasks=[task1, task2])
        
        ready = dag.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == task2.id
