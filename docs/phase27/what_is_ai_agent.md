### 1. Why it exists (THE PROBLEM first)
Language models can generate text, but text alone cannot book flights, run code, query databases, or control physical devices. Real-world tasks require taking actions in external systems. An AI that only talks is like a consultant who never picks up the phone — full of advice but unable to execute.

### 2. Definition (very simple)
An AI Agent is a system that combines a language model with the ability to perceive its environment, make plans, take actions through tools or APIs, and observe the results — looping until a goal is achieved.

### 3. Real-life analogy
A consultant is given a laptop, a phone, a budget, and a mandate: "Reduce our shipping costs." They do not just write a memo. They research carriers (perceive), compare rates (plan), call the cheapest one (act), check the contract (observe), and iterate until the deal is signed. The consultant is the brain; the phone and laptop are their tools.

### 4. Tiny numeric example
Goal: "What is the square root of 144 plus the temperature in Paris?"

A plain LLM might hallucinate: "The square root of 144 is 12. The temperature in Paris is probably around 15 degrees Celsius. Total: 27."

An AI Agent:
1. **Plan:** I need two pieces of information: sqrt(144) and current temperature in Paris.
2. **Act:** Call calculator tool with "sqrt(144)" → returns 12.0
3. **Act:** Call weather API with "Paris" → returns 18°C
4. **Observe:** I have 12.0 and 18.
5. **Act:** Call calculator with "12.0 + 18" → returns 30.0
6. **Final Answer:** 30.0

The agent did not guess. It used tools to get exact values.

### 5. Common confusion
- **An agent is not just a chatbot.** A chatbot only generates text. An agent can call APIs, run code, and modify state in the world.
- **The LLM is the brain, not the whole agent.** The agent also needs a tool registry, a loop controller, and memory of past actions.
- **Agents can fail too.** If a tool is down or returns bad data, the agent must handle errors and retry — just like a human would.
- **Not every task needs an agent.** If the answer is in the model's training data, a simple response is faster and cheaper.
- **Safety is critical.** An agent with a code-execution tool can accidentally delete files or make unwanted purchases. Tool permissions must be carefully controlled.

### 6. Where it is used in our code
`src/phase27/phase27_agentic_ai.py` implements a toy agent with a calculator tool and a search tool, showing how the agent loops between reasoning and acting to solve problems it cannot answer from memory alone.
