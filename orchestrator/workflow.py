"""
DAG-based workflow engine.
Nodes are tasks, edges are dependencies. Executes tasks in topological order,
running independent tasks in parallel.
"""
from __future__ import annotations
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class TaskResult:
    task_id: str
    output: Any
    success: bool
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class Task:
    task_id: str
    fn: Callable
    inputs: dict = field(default_factory=dict)   # static inputs
    depends_on: list[str] = field(default_factory=list)
    max_retries: int = 2
    retry_delay: float = 1.0


class WorkflowEngine:
    """
    Executes a DAG of tasks.
    Tasks with no unmet dependencies run in parallel.
    Outputs of upstream tasks are passed as inputs to downstream tasks.
    """

    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.tasks: dict[str, Task] = {}

    def add_task(self, task: Task):
        self.tasks[task.task_id] = task
        return self

    def _topo_sort(self) -> list[list[str]]:
        """Return tasks grouped into execution waves (each wave can run in parallel)."""
        in_degree = {tid: 0 for tid in self.tasks}
        for task in self.tasks.values():
            for dep in task.depends_on:
                in_degree[task.task_id] = in_degree.get(task.task_id, 0) + 1

        waves, ready = [], deque(tid for tid, d in in_degree.items() if d == 0)
        remaining_deps = {tid: set(t.depends_on) for tid, t in self.tasks.items()}

        while ready:
            wave = list(ready)
            waves.append(wave)
            ready.clear()
            for tid in wave:
                for other_tid, deps in remaining_deps.items():
                    if tid in deps:
                        deps.discard(tid)
                        if not deps:
                            ready.append(other_tid)
        return waves

    def _run_task(self, task: Task, context: dict) -> TaskResult:
        merged = {**task.inputs, **{dep: context[dep] for dep in task.depends_on if dep in context}}
        t0 = time.perf_counter()
        for attempt in range(task.max_retries + 1):
            try:
                output = task.fn(**merged)
                return TaskResult(task.task_id, output, True, duration_ms=(time.perf_counter()-t0)*1000)
            except Exception as e:
                if attempt < task.max_retries:
                    time.sleep(task.retry_delay * (2 ** attempt))
                else:
                    return TaskResult(task.task_id, None, False, str(e), (time.perf_counter()-t0)*1000)

    def run(self, initial_context: dict = None) -> dict[str, TaskResult]:
        context = dict(initial_context or {})
        results: dict[str, TaskResult] = {}
        waves = self._topo_sort()

        for wave_idx, wave in enumerate(waves):
            print(f"  Wave {wave_idx+1}: {wave}")
            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                futures = {pool.submit(self._run_task, self.tasks[tid], context): tid for tid in wave}
                for future in as_completed(futures):
                    result = future.result()
                    results[result.task_id] = result
                    context[result.task_id] = result.output
                    status = "✓" if result.success else "✗"
                    print(f"    {status} {result.task_id} ({result.duration_ms:.0f}ms)")

        return results
