### 1. Why it exists (THE PROBLEM first)
A single agent trying to do everything — research, write, edit, code, test — becomes a bottleneck. Different tasks require different expertise. Just as humans work in teams, multiple specialized agents can collaborate to solve complex problems faster and better than one generalist agent.

### 2. Definition (very simple)
A Multi-Agent System is a group of AI agents, each with a specialized role, that communicate and collaborate to achieve a shared goal. One agent might research facts, another might write a draft, and a third might review and edit.

### 3. Real-life analogy
A research team has a data scientist who crunches numbers, a writer who drafts the report, and an editor who checks for errors. They pass work back and forth: the scientist gives findings to the writer, the writer produces a draft for the editor, and the editor returns corrections. No single person does everything, but together they produce a polished paper.

### 4. Tiny numeric example
Goal: "Write a blog post about the latest Mars rover findings."

Single agent:
- Tries to research, write, and edit all alone.
- May miss recent news or make factual errors because it is juggling too many roles.

Multi-agent team:
- **Researcher Agent:** Searches NASA website. Returns: "Perseverance found organic molecules in Jezero Crater on Sol 450."
- **Writer Agent:** Receives the research. Drafts: "In a groundbreaking discovery, NASA's Perseverance rover..."
- **Fact-Checker Agent:** Verifies the draft against the research. Flags: "The Sol number is 450, not 455."
- **Editor Agent:** Fixes the error and polishes the prose.
- Final output is accurate, well-written, and verified by specialists.

### 5. Common confusion
- **Multi-agent is not just parallel processing.** The agents interact — one agent's output becomes another's input. It is a pipeline or a conversation, not just running the same task on multiple machines.
- **Communication overhead is real.** Agents must agree on message formats and handoff protocols. Poor communication causes errors, just like in human teams.
- **Not every problem needs multiple agents.** For simple tasks, the overhead of coordinating agents is worse than doing it alone. Use multi-agent only when roles are genuinely different.
- **Agents can disagree.** If the writer and editor have conflicting instructions, they might loop forever arguing. Clear roles and a manager agent help prevent this.
- **Frameworks exist.** AutoGen, CrewAI, and LangGraph are popular libraries for building multi-agent systems with pre-built communication patterns.

### 6. Where it is used in our code
`src/phase27/phase27_agentic_ai.py` demonstrates a simple two-agent system: a Researcher and a Writer who pass information back and forth to produce a verified answer.
