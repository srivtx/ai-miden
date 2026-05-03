## What Is Tool Use?

---

### The Problem

A language model knows a lot, but it cannot calculate 34789 * 9823 reliably, it cannot check today's weather, and it cannot search the live internet. When a user asks "What is 34789 times 9823?", the model either hallucinates a wrong answer or refuses. When a user asks "Will it rain in Tokyo tomorrow?", the model can only guess based on its training data cutoff. The model is a text predictor, not a calculator, not a browser, not an API client. How do you give the model access to real-world capabilities without rebuilding it from scratch?

---

### Definition

**Tool use** is the capability of a language model to recognize when a user query requires external computation or data, generate a structured function call with correct parameters, receive the tool's output, and incorporate that output into a natural-language response. It transforms the model from a closed text generator into an orchestrator that delegates subtasks to specialized systems.

**How it works:**
```
Standard model (no tools):
  User: "What is 34789 * 9823?"
  Model: "34789 multiplied by 9823 is approximately 341,700,000"
  Reality: wrong answer (actual is 341,700,347)

Tool-enabled model:
  User: "What is 34789 * 9823?"
  Model thinks: "This requires exact arithmetic. I should use the calculator tool."
  Model outputs: <tool_call>
                  <name>calculator</name>
                  <parameters>{"expression": "34789 * 9823"}</parameters>
                </tool_call>
  
  Tool executes: calculator("34789 * 9823") → 341700347
  
  Model receives: <tool_result>341700347</tool_result>
  Model answers: "34789 multiplied by 9823 is exactly 341,700,347."
```

**Key concepts:**
- **Tool definition schema:** JSON or XML description of each tool's name, parameters, and purpose. The model sees this schema in its context window and learns to emit matching calls.
- **Function calling format:** structured output (JSON, XML, or special tokens) that a parser can extract and execute. Different models use different formats.
- **Direct answer vs. tool call:** the model must learn to judge whether its parametric knowledge is sufficient or whether external help is needed.
- **ReAct pattern:** Reasoning + Action. The model thinks step by step, decides to use a tool, observes the result, then reasons again. This enables multi-step problem solving.

**Why this matters:**
- Tool use eliminates arithmetic hallucinations by delegating to a calculator
- Tool use gives the model access to real-time data (weather, stock prices, search)
- Tool use enables actions (send email, book flight, query database)
- A 3B model with tools can outperform a 70B model without tools on tasks requiring factual accuracy

---

### Real-Life Analogy

Imagine a brilliant but isolated professor locked in a library with no windows, no phone, and no internet. The professor has read every book up to 2023.

- **No tools:** A student asks "What is the current temperature in Paris?" The professor guesses based on climate averages from books. "Probably around 15 degrees Celsius in spring." The student gets a plausible but potentially wrong answer.
- **With tools:** The professor has a phone on their desk with three speed-dial numbers: a weather hotline, a calculator, and a research librarian. When asked about Paris weather, the professor dials the weather hotline, gets the live reading, and reports it exactly. When asked to multiply large numbers, they use the calculator. When asked about a recent discovery, they call the librarian who searches current journals.
- **The skill:** The professor must learn (a) when to use the phone versus answering from memory, (b) which number to dial, (c) how to phrase the question so the other party understands, and (d) how to translate the answer back into a helpful explanation. That is tool use.

---

### Tiny Numeric Example

**Tool selection decision boundaries (simplified):**
```
Model sees a query and must choose one of:
  A) Direct answer (parametric knowledge)
  B) Calculator tool
  C) Weather tool
  D) Search tool

Query: "What is the capital of France?"
  Model confidence (internal logit distribution):
    A) 0.92   ← high confidence, general knowledge
    B) 0.03
    C) 0.03
    D) 0.02
  Decision: direct answer → "Paris"

Query: "What is 23456789 * 98765432?"
  Model confidence:
    A) 0.15   ← low confidence, large numbers hallucinate easily
    B) 0.78   ← calculator is the right tool
    C) 0.04
    D) 0.03
  Decision: calculator → expression="23456789 * 98765432"

Query: "What is the weather in Seattle right now?"
  Model confidence:
    A) 0.20   ← training data is stale
    B) 0.05
    C) 0.72   ← weather tool needed
    D) 0.03
  Decision: weather → location="Seattle"
```

**Parameter extraction accuracy:**
```
User: "Calculate the square root of 144 plus 25"
Correct tool call: calculator(expression="sqrt(144) + 25")

Common extraction errors:
  - Missing parentheses: "sqrt 144 + 25" → evaluates as sqrt(169) = 13
  - Wrong parameter name: expr instead of expression → tool rejects
  - Extra text: "Let me calculate sqrt(144) + 25 for you" → parser fails

After tool-use training:
  Parameter extraction accuracy: 94%
  Before training (prompting only): 62%
```

---

### Common Confusion

1. **"Tool use is just prompt engineering."** Prompting can elicit tool-like behavior in large models, but it is brittle and format-sensitive. Training on tool-use demonstrations teaches the model the exact schema, timing, and parameter extraction patterns. A trained 3B model outperforms a prompted 7B model on tool tasks.

2. **"The model executes the tool itself."** No. The model generates a text representation of a function call. A separate execution layer parses that text, validates parameters, runs the tool, and feeds the result back into the model. The model is the orchestrator, not the executor.

3. **"Tool use only works for factual queries."** Tools can also be creative: image generation APIs, code interpreters, music composition engines. Any external system with a defined interface can be a tool. The model's job is to decide when to invoke it and how to use the result.

4. **"One tool call is enough for every query."** Complex queries need multi-step ReAct loops. "What was the weather in the capital of France on the day the Eiffel Tower opened?" requires: (1) search Eiffel Tower opening date, (2) search capital of France, (3) weather lookup for that date and city. Each step feeds into the next.

5. **"Tool definitions must be hard-coded in the system prompt."** They are passed in the context window, but they can be dynamic. A system can add or remove tools per conversation. The model only knows about the tools currently in its context.

6. **"Tool use training requires real API calls during training."** Not necessarily. Most training uses synthetic data where tool outputs are pre-generated or simulated. The model learns to emit the right call format; it does not need live APIs during gradient descent.

7. **"Smaller models cannot use tools effectively."** False. A 1B model with proper tool-use training achieves >90% tool selection accuracy. The challenge is not model size but training data quality and format consistency. Smaller models may struggle with multi-step reasoning but excel at single-step tool calls.

---

### Where It Is Used in Our Code

`src/phase126/phase126_tool_concepts.py` — We simulate a toy tool-use environment where a tiny classifier must choose between "direct answer" and "use calculator" based on query features. We demonstrate the ReAct loop: reasoning → action → observation → final answer, showing how multi-step tool use chains together.

`src/phase126/phase126_tool_colab.py` — We fine-tune a real Qwen2.5-3B-Instruct model on 500 synthetic tool-use conversations involving calculator, weather, and search tools. We evaluate tool selection accuracy, parameter extraction accuracy, and direct-answer accuracy on held-out test queries, demonstrating that training dramatically outperforms prompting.
