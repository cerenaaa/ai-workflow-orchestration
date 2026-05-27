# AI Workflow Orchestration

[![CI](https://github.com/cerenaaa/ai-workflow-orchestration/actions/workflows/ci.yml/badge.svg)](https://github.com/cerenaaa/ai-workflow-orchestration/actions)

Multi-step AI workflow orchestration: DAG-based task execution, parallel LLM calls, conditional branching, retries, and result aggregation.

## Patterns implemented

| Pattern | Use case |
|---|---|
| **Sequential chain** | Each step feeds into the next |
| **Parallel fan-out** | Run N LLM calls concurrently, aggregate results |
| **Map-reduce** | Process chunks in parallel, merge outputs |
| **Conditional branching** | Route to different agents based on output |
| **Retry with backoff** | Resilient execution with exponential backoff |

## Structure
```
ai-workflow-orchestration/
├── orchestrator/
│   ├── workflow.py       # DAG workflow definition and execution engine
│   └── executor.py       # Parallel task executor with retry logic
├── tasks/
│   ├── base_task.py      # Base task class
│   └── llm_tasks.py      # Common LLM task implementations
├── dag/
│   └── dag_builder.py    # Fluent DAG builder API
└── run_workflow.py
```

## Quickstart
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python run_workflow.py --workflow summarize_and_classify
```
