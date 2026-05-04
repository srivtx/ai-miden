## What Is the ReAct Pattern?

**The Problem:**
If you ask a model to answer a question directly, it must do all reasoning internally. It cannot look up facts, run code, or check its work. If you ask it to use tools without reasoning, it calls tools randomly without a plan. How do you combine step-by-step reasoning with tool use so the model thinks before it acts?

**Definition:**
**ReAct** (Reasoning + Acting) is a prompting pattern where a language model interleaves reasoning traces (Thought) with actions (Action) and observations (Observation) to solve tasks. The model thinks about what it needs, takes an action, observes the result, and thinks again.

**Real-life analogy:**
ReAct is like a detective solving a case. The detective thinks: "The suspect was seen at the bank at 3 PM. I need to check the bank's security footage." (Thought) They drive to the bank and request the footage. (Action) The footage shows the suspect withdrew $10,000. (Observation) They think: "A large withdrawal suggests premeditation. I need to check their financial records." (Thought) And so on. The detective does not just guess the solution. They reason, act, observe, and reason again.

**Tiny numeric example:**
```
Question: What is 15 squared plus 23?
Thought: I need to compute 15^2 first, then add 23.
Action: calculator(15**2)
Observation: 225
Thought: Now I need to add 23 to 225.
Action: calculator(225 + 23)
Observation: 248
Final Answer: 248
```

**Common confusion:**
- **"ReAct is an algorithm."** It is a prompting pattern, not an algorithm. The model generates the reasoning and actions via prompting.
- **"ReAct only works with function-calling models."** Any model can use ReAct with proper prompt engineering. Function-calling models make it more reliable.
- **"ReAct always solves the problem."** No. ReAct can get stuck in loops, call the wrong tools, or fail to recognize when it has enough information.
- **"The observation comes from the model."** No. The observation comes from the tool or environment. The model only generates Thoughts and Actions.
- **"ReAct is the same as chain-of-thought."** Chain-of-thought only reasons. ReAct reasons AND acts. CoT is "show your work." ReAct is "show your work AND use tools."
- **"ReAct requires training."** The original ReAct paper used few-shot prompting without any fine-tuning. Fine-tuning improves reliability but is not required.

**Where it appears in our code:**
`src/phase156/phase156_multi_tool_agent.py` — The `ReActAgent.run()` method implements the full loop: think → parse action → execute tool → observe → repeat until max steps or final answer.
