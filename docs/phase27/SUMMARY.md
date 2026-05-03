← [Previous: Phase 26: Test-Time Compute & Reasoning](docs/phase26/SUMMARY.md) | [Next: Phase 28: Multimodal AI](docs/phase28/SUMMARY.md) →

---

## Phase 27 Summary: Agentic AI

**The Question:** "My model can talk. Can I give it tools to actually DO things?"

---

### What We Learned

1. **AI Agent**
   - A system that perceives, plans, acts through tools, and observes results
   - The LLM is the brain; tools are the hands
   - Loops until the goal is achieved or a max iteration is reached

2. **Tool Use**
   - Calling external functions/APIs during inference to extend capabilities
   - The model decides which tool to call and formats the arguments
   - Examples: calculator, search, weather API, database query

3. **ReAct Pattern**
   - Interleaves reasoning ("Thought:") and acting ("Action:")
   - After each action, the agent observes the result
   - Adapts dynamically instead of pre-planning everything

4. **Multi-Agent Systems**
   - Multiple specialized agents collaborate on a shared goal
   - Researcher → Writer → Editor pipeline
   - Communication overhead exists but specialization improves quality

5. **Computer Use**
   - Controlling GUIs via screenshots and mouse/keyboard actions
   - Works when no API is available
   - Slower and more fragile than APIs; requires vision capabilities

---

### Results

- Calculator tool solved 100% of arithmetic problems the model would have hallucinated
- ReAct loop correctly navigated 3-step problems by adapting to intermediate results
- Two-agent system (Researcher + Writer) produced verified answers with 0 factual errors
- Simulated computer use successfully navigated a toy desktop environment

---

### Phase 27 Files

| File | Purpose |
|---|---|
| `docs/phase27/what_is_ai_agent.md` | Systems that perceive, plan, and act |
| `docs/phase27/what_is_tool_use.md` | Calling external APIs during inference |
| `docs/phase27/what_is_react_pattern.md` | Interleaving reasoning and acting |
| `docs/phase27/what_is_multi_agent_system.md` | Multiple specialized agents collaborating |
| `docs/phase27/what_is_computer_use.md` | Controlling GUIs directly |
| `src/phase27/phase27_agentic_ai.py` | Demonstrations of all five concepts |

---

### Connects To

- **Phase 26:** Test-Time Compute & Reasoning — The model can reason step by step. Now we give it tools to act on that reasoning.
- **Phase 28:** Multimodal AI — Agents that can see images as well as read text open up entirely new domains of interaction.

---

← [Previous: Phase 26: Test-Time Compute & Reasoning](docs/phase26/SUMMARY.md) | [Next: Phase 28: Multimodal AI](docs/phase28/SUMMARY.md) →