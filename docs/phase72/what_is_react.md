# What is ReAct?

## 1. Why it exists (THE PROBLEM)
A single prompt-response cycle is often insufficient for complex tasks. If you ask an agent "What is the population of the capital of France?", a one-shot answer might hallucinate. You need a loop: think about what you need, take an action (e.g., search), observe the result, and then think again. ReAct formalizes this loop so the agent can reason step-by-step and act on the world.

## 2. Definition
ReAct (Reasoning + Acting) is a prompting / agent architecture where an LLM alternates between generating a reasoning trace (Thought) and performing an action (Action), then observing the result (Observation), repeating until the task is complete.

## 3. Real-life analogy
A detective solving a case. The detective thinks: "The suspect was seen at the airport." (Thought). They drive to the airport and check security footage. (Action). The footage shows the suspect boarding a flight to Berlin. (Observation). They think again: "I need to contact Berlin police..." and so on.

## 4. Tiny numeric example
Task: Find the square root of 144 plus 10.
- Turn 1 Thought: I need to compute sqrt(144) first.
- Turn 1 Action: calculator(tool="sqrt", x=144)
- Turn 1 Observation: 12.0
- Turn 2 Thought: Now add 10 to 12.0.
- Turn 2 Action: calculator(tool="add", a=12.0, b=10)
- Turn 2 Observation: 22.0
- Turn 3 Thought: I have the final answer.
- Turn 3 Action: finish(answer=22.0)

## 5. Common confusion
- **"ReAct is a specific model."** No. It is an architecture / prompting pattern, not a model weights file.
- **"ReAct means the model reasons like a human."** No. It generates text that looks like reasoning; it is not conscious.
- **"ReAct always needs tools."** You can use ReAct with pure text reasoning (e.g., chain-of-thought), but it is most powerful with tools.
- **"More turns always mean better answers."** No. Agents can loop infinitely or get stuck if not bounded.
- **"ReAct is the same as Chain-of-Thought."** Chain-of-Thought only reasons; ReAct adds acting on the environment.
- **"The observation comes from the model itself."** No. Observations come from the external world (tool outputs).
- **"You need a massive model for ReAct."** Smaller models can work if fine-tuned for the format.

## 6. Where it is used in our code
`src/phase72/phase72_real_agents.py` implements a full ReAct loop: at each turn the agent prints a Thought, chooses an Action (tool call), receives an Observation, and updates its state. `src/phase72/phase72_real_agents_colab.py` extends this with a real LLM generating the Thought/Action pairs.
