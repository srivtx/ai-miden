# Phase 72: Real Agents with Tool Use — Summary

Phase 72 bridges the gap between "chatbot" and "agent." Students learn that an LLM alone is a passive text generator; to become an agent it needs:

1. **Tool Use** — the ability to call external calculators, search engines, and APIs.
2. **Function Calling** — structured JSON output so the host system can reliably execute those calls.
3. **ReAct** — a loop of Thought → Action → Observation that lets the agent reason step-by-step.
4. **Multi-Turn State** — memory and planning across turns so the agent handles complex, evolving tasks.

The NumPy demo (`src/phase72/phase72_real_agents.py`) simulates these concepts without requiring GPU or API keys, making the mechanics transparent. The Colab script (`src/phase72/phase72_real_agents_colab.py`) shows how the same patterns map to a real open-source LLM, with heavy comments explaining the design choices.

Key takeaway: An agent is not a smarter model; it is a model wrapped in a control loop with tools and memory.
