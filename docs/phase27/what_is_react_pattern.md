### 1. Why it exists (THE PROBLEM first)
If an agent plans everything upfront before acting, it cannot adapt to unexpected results. If it acts without planning, it wanders aimlessly. Real-world problem solving requires interleaving reasoning and action: think a little, act a little, observe the result, then think again.

### 2. Definition (very simple)
The ReAct pattern (Reasoning + Acting) is an agent architecture that alternates between generating reasoning steps ("Thought:") and taking actions ("Action:"). After each action, the agent observes the result ("Observation:") and uses it to inform the next thought. This loop continues until the task is complete.

### 3. Real-life analogy
A detective solving a case does not write the entire investigation plan on day one and blindly follow it. They think: "The suspect was at the cafe at 9 PM." Then act: "Check the cafe's security footage." Then observe: "The footage shows someone matching the suspect's description." Then think again: "This confirms the alibi is false." ReAct is exactly this cycle.

### 4. Tiny numeric example
Task: "Find the population of the capital of France."

ReAct trace:
```
Thought 1: I need to find the capital of France first, then its population.
Action 1: search("capital of France")
Observation 1: Paris

Thought 2: Now I need the population of Paris.
Action 2: search("population of Paris")
Observation 2: 2.1 million (city proper), 12.4 million (metro area)

Thought 3: The user probably wants the city proper population.
Action 3: calculator("2.1")
Observation 3: 2.1

Thought 4: I have the answer.
Final Answer: The population of Paris is approximately 2.1 million.
```

Each thought is based on the previous observation. The agent does not pre-plan; it reacts to new information.

### 5. Common confusion
- **ReAct is not reinforcement learning.** The "Act" in ReAct means calling a tool, not taking an action in an RL environment. There is no reward signal or policy gradient.
- **The loop can be infinite.** If the agent keeps searching without converging, you need a max-iteration limit or a stopping criterion.
- **ReAct works best with structured output.** The model must reliably output "Thought:", "Action:", and "Observation:" in a parseable format. JSON mode or fine-tuning helps.
- **It is not the only agent pattern.** Other patterns include Plan-and-Execute (plan everything first, then execute) and Reflexion (the agent critiques its own past actions).
- **ReAct can be slow.** Each action requires an API call or tool execution, which adds latency. For simple tasks, a single-shot answer is faster.

### 6. Where it is used in our code
`src/phase27/phase27_agentic_ai.py` implements a full ReAct loop where the agent alternates between thinking, acting with tools, and observing results to solve multi-step problems.
