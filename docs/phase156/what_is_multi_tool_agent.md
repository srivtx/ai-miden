## What Is a Real Multi-Tool Agent?

**The Problem:**
A language model can write essays and answer trivia, but it cannot calculate square roots, look up current facts, or run code. When you ask "What is the population of France divided by the area of Germany?" the model hallucinates a number because it has no calculator. When you ask "Who won the Nobel Prize in Physics last year?" it answers with outdated information because it has no access to current data. How do you give a model real capabilities beyond text generation?

**Definition:**
A **multi-tool agent** is a system that interleaves reasoning (planning what to do) with action (calling external tools like calculators, search engines, and code interpreters) to solve complex problems that require more than text generation alone.

**Real-life analogy:**
A multi-tool agent is like a research assistant with a desk full of resources. When you ask them a question, they do not just guess. They grab a calculator for math, open an encyclopedia for facts, run a Python script for data analysis, and check their notes from previous research (memory). They think about what they need, use the right tool, observe the result, and think again. A human researcher does not rely on memory alone. Neither should an AI.

**Tiny numeric example:**
Query: "What is the population of Japan divided by the area of Germany?"
- Step 1 (Think): I need two facts: Japan's population and Germany's area.
- Step 2 (Action): Wikipedia search for "Japan"
- Step 3 (Observation): Japan population: ~125 million
- Step 4 (Think): Now I need Germany's area.
- Step 5 (Action): Wikipedia search for "Germany"
- Step 6 (Observation): Germany area: ~357,000 km²
- Step 7 (Think): Now I need to divide 125,000,000 by 357,000.
- Step 8 (Action): Calculator(125000000 / 357000)
- Step 9 (Observation): 350.14
- Step 10 (Final Answer): Approximately 350 people per km²

**Common confusion:**
- **"A tool agent is just RAG."** No. RAG retrieves documents. Tool agents execute code, call APIs, and perform computations. RAG is one possible tool among many.
- **"More tools is always better."** Each tool adds latency and error modes. A good agent has 3-5 well-chosen tools, not 50 rarely-used ones.
- **"The LLM executes the tools."** No. The LLM decides which tool to call and with what arguments. The agent framework executes the tool and returns the result to the LLM.
- **"Tool use requires fine-tuning."** Function-calling models are fine-tuned for tool use, but any model can use tools via prompt engineering (ReAct pattern).
- **"Agents are autonomous."** Current agents are not autonomous. They execute a fixed loop (think → act → observe) for a bounded number of steps. True autonomy is an active research area.
- **"Memory is just chat history."** Vector memory retrieves semantically similar past interactions, not just the recent conversation. It lets the agent recall facts from 100 turns ago.

**Where it appears in our code:**
`src/phase156/phase156_multi_tool_agent.py` — ReAct agent with calculator, Python executor, Wikipedia search, and vector memory. Solves multi-step problems by interleaving reasoning and action.
