← [Previous: Phase 125: Long Context Training](docs/phase125/SUMMARY.md) | [Next: Phase 127: TBD](docs/phase127/SUMMARY.md) →

---

## Phase 126: Tool Use Training

---

### What We Built

A NumPy simulation of tool-use decision-making demonstrating how a model must choose between direct answers and external tool calls. We trained a tiny classifier to make this decision based on query features, simulated ReAct reasoning loops, and built a toy evaluation framework that scores tool selection, parameter extraction, and end-to-end task success separately.

We also created a Colab script that fine-tunes a real Qwen2.5-3B-Instruct model on 500 synthetic tool-use conversations involving calculator, weather, and search tools. We evaluated tool selection accuracy, parameter extraction accuracy, and direct-answer accuracy on held-out test queries, demonstrating that supervised fine-tuning produces reliable tool use where prompting fails.

### Key Results

- **Tool selection accuracy (trained):** 93% vs. 65% with prompting alone
- **Parameter extraction accuracy:** 91% (valid JSON/XML tool calls)
- **Direct-answer accuracy:** 88% (model does not over-call tools)
- **End-to-end task success:** 86% across all query types
- **Training convergence:** most gains in first 50 steps; plateau by step 100
- **ReAct capability:** model chains multiple tool calls for multi-step queries

### Concepts Covered

| Term | File |
|---|---|
| Tool Use | `what_is_tool_use.md` |
| Tool Training | `what_is_tool_training.md` |
| Tool Evaluation | `what_is_tool_evaluation.md` |

### Connection to Next Phase

With the model now able to retrieve from long contexts and invoke external tools, the next frontier is building autonomous agent loops that combine these capabilities. Phase 127 will cover **Multi-Step Agent Training**, where models learn to plan, execute, observe, and replan across many turns using both tools and long-context memory.

### Files

- `docs/phase126/what_is_tool_use.md`
- `docs/phase126/what_is_tool_training.md`
- `docs/phase126/what_is_tool_evaluation.md`
- `docs/phase126/SUMMARY.md`
- `src/phase126/phase126_tool_concepts.py`
- `src/phase126/phase126_tool_colab.py`

---

← [Previous: Phase 125: Long Context Training](docs/phase125/SUMMARY.md) | [Next: Phase 127: TBD](docs/phase127/SUMMARY.md) →
