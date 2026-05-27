"""Demo workflows."""
import argparse, os

def demo_without_api():
    """Shows DAG structure without making API calls."""
    from orchestrator.workflow import WorkflowEngine, Task
    engine = WorkflowEngine()

    def step_a(text): return f"[A processed] {text[:30]}"
    def step_b(text): return f"[B processed] {text[:30]}"
    def step_c(step_a, step_b): return f"[C merged] {step_a} + {step_b}"
    def step_d(step_c): return f"[D final] {step_c}"

    engine.add_task(Task("step_a", step_a, {"text": "Hello world input text"}))
    engine.add_task(Task("step_b", step_b, {"text": "Hello world input text"}))
    engine.add_task(Task("step_c", step_c, depends_on=["step_a", "step_b"]))
    engine.add_task(Task("step_d", step_d, depends_on=["step_c"]))

    print("Running demo DAG (no API key needed):")
    results = engine.run()
    for tid, r in results.items():
        print(f"  {tid}: {r.output}")

def demo_with_api(text: str):
    from dag.dag_builder import DAGBuilder
    from tasks.llm_tasks import summarize, classify, extract_keywords
    dag = (DAGBuilder()
        .add("summarize", summarize, {"text": text, "max_words": 50})
        .add("classify", classify, depends_on=["summarize"])
        .add("keywords", extract_keywords, {"text": text, "n": 5}))
    results = dag.run()
    for tid, r in results.items():
        print(f"  {tid}: {r.output}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", default="demo")
    args = parser.parse_args()
    if os.environ.get("ANTHROPIC_API_KEY") and args.workflow != "demo":
        demo_with_api("Artificial intelligence is transforming industries from healthcare to finance.")
    else:
        demo_without_api()

if __name__ == "__main__":
    main()
