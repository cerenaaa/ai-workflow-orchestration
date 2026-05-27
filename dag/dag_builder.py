"""Fluent DAG builder API."""
from __future__ import annotations
from orchestrator.workflow import WorkflowEngine, Task


class DAGBuilder:
    def __init__(self):
        self.engine = WorkflowEngine()

    def add(self, task_id: str, fn, inputs: dict = None, depends_on: list = None, max_retries: int = 1):
        self.engine.add_task(Task(
            task_id=task_id, fn=fn,
            inputs=inputs or {},
            depends_on=depends_on or [],
            max_retries=max_retries,
        ))
        return self

    def run(self, context: dict = None) -> dict:
        return self.engine.run(context)

    def build(self) -> WorkflowEngine:
        return self.engine
