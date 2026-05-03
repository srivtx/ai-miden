# What is Tool Use?

## 1. Why it exists (THE PROBLEM)
LLMs are text-in, text-out systems. They cannot do math reliably, access the internet, query databases, or interact with the physical world. If you ask GPT-4 "What is the weather in Tokyo right now?", it hallucinates because it has no real-time data. Tool Use solves this by giving the model a way to call external functions, APIs, or programs to get real information and then use that information to answer.

## 2. Definition
Tool Use (also called function calling or tool calling) is the capability of an LLM to generate a structured request (usually JSON) to invoke an external function, receive the result, and incorporate it into its response.

## 3. Real-life analogy
A doctor diagnosing a patient. The doctor (LLM) knows medicine but cannot see inside your body. They write a referral (tool call) to a radiologist (external tool) for an X-ray. The radiologist returns the scan (observation). The doctor then reads the scan and gives a final diagnosis.

## 4. Tiny numeric example
Prompt: "What is 128 * 456?"
The LLM cannot compute this accurately in its head. Instead, it emits:
```json
{"tool": "calculator", "arguments": {"a": 128, "b": 456}}
```
The calculator returns `58368`. The LLM then answers: "128 * 456 = 58,368."

## 5. Common confusion
- **"Tool use is the same as RAG."** No. RAG retrieves documents; tool use executes code or calls APIs.
- **"The model runs the tool itself."** No. The model only generates the *request* to run the tool; the host system executes it.
- **"Any model can do tool use out of the box."** No. The model must be trained or fine-tuned to emit structured tool calls.
- **"Tool use is only for APIs."** No. It can call local scripts, databases, calculators, or even robotics controllers.
- **"Tool use makes the model omniscient."** No. It only knows what the tool returns; garbage in, garbage out.
- **"You only need one tool."** No. Complex agents use many specialized tools.
- **"Tool use is slow because the model is slow."** The latency is often dominated by the tool execution (e.g., web search), not the model.

## 6. Where it is used in our code
In `src/phase72/phase72_real_agents.py`, the simulated agent decides whether to use the `calculator` or `search` tool based on the input query. In `src/phase72/phase72_real_agents_colab.py`, we define real tool schemas (`calculator`, `web_search`, `weather`) and the agent emits JSON to call them during the ReAct loop.
