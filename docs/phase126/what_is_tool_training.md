## What Is Tool Training?

---

### The Problem

You have defined three tools — calculator, weather, and search — and written detailed schemas describing their parameters. You put these schemas into the system prompt and ask the model to use them. Sometimes it works. Sometimes the model invents a tool name that does not exist. Sometimes it passes a string where a number is required. Sometimes it calls the calculator for "What is 2+2?" and sometimes it answers directly. The behavior is inconsistent because the model has never seen structured tool-use demonstrations during its pre-training. It is guessing at the format based on a few sentences of instructions. How do you make tool use reliable and reproducible?

---

### Definition

**Tool training** is supervised fine-tuning on conversations that demonstrate the full tool-use trajectory: user query → model reasoning → tool call (with correct parameters) → tool result → model final answer. By training on hundreds or thousands of these complete demonstrations, the model internalizes the tool schema, learns when to call versus when to answer directly, and produces parseable outputs with high consistency.

**How it works:**
```
Single training example (synthetic):

  System prompt:
    "You have access to tools. Use them when needed.
     Tools:
     - calculator(expression: str)
     - weather(location: str)
     - search(query: str)"

  User: "What is the square root of 1764?"

  Assistant (reasoning): 
    "The user asks for an exact mathematical result.
     I should use the calculator tool to ensure accuracy."

  Assistant (tool call):
    <tool_call>
      <name>calculator</name>
      <parameters>{"expression": "sqrt(1764)"}</parameters>
    </tool_call>

  Tool result: "42.0"

  Assistant (final answer):
    "The square root of 1764 is 42."

Training loss is computed on:
  - The reasoning tokens (teaches when to use tools)
  - The tool call tokens (teaches format and parameter extraction)
  - The final answer tokens (teaches integration of tool results)
```

**Key components:**
- **Trajectory completeness:** every example must show the full loop, not just the tool call. Partial examples teach the model to stop mid-trajectory.
- **Negative examples:** queries that should NOT use tools ("What is the capital of Italy?") must be included so the model learns the decision boundary.
- **Format consistency:** all tool calls must use the exact same XML/JSON schema. Mixed formats confuse the model.
- **Parameter diversity:** training data must cover edge cases — empty strings, special characters, nested expressions — so the model learns robust extraction.

**Why this matters:**
- Prompting achieves 60-70% tool call accuracy; training achieves 90-95%
- Training reduces hallucinated tool names from 15% to <1%
- Training teaches the model to handle tool errors gracefully (retry, reformat, apologize)
- A model trained on 500 examples generalizes to new tools with similar schemas

---

### Real-Life Analogy

Imagine teaching a new employee to use a company phone system.

- **Prompting only:** You hand the employee a 3-page manual and say "figure it out." They sometimes dial the right extension, sometimes call the wrong department, and sometimes just shout across the office instead of using the phone. Results are unpredictable.
- **Tool training:** You shadow the employee through 500 real calls. For each call, you show them: (1) listen to the request, (2) decide if the phone is needed, (3) dial the exact extension, (4) relay the answer back. After 500 shadowed calls, the employee rarely makes mistakes. They have internalized the decision tree and the dialing patterns.
- **Why 500?** Fewer than 100 and the employee still guesses. More than 1000 and improvements plateau because the core patterns are already learned. The quality of examples matters more than the count — one confusing example does more harm than ten good ones.

---

### Tiny Numeric Example

**Training dataset composition (500 examples):**
```
Category          | Count | Purpose
------------------|-------|---------------------------------
Calculator needed | 150   | Math, unit conversion, formulas
Weather needed    | 100   | Current conditions, forecasts
Search needed     | 100   | Recent events, obscure facts
Direct answer     | 150   | General knowledge, opinions, greetings

Format: XML tool tags (consistent across all examples)
<tool_call><name>TOOL</name><parameters>JSON</parameters></tool_call>
```

**Training dynamics:**
```
Step 0 (untrained model):
  Tool selection accuracy: 45% (random among 4 options)
  Parameter extraction: 30% (often invents wrong keys)
  Direct answer accuracy: 70% (base model is already decent)

Step 25:
  Tool selection accuracy: 72%
  Parameter extraction: 58%
  Direct answer accuracy: 75%

Step 50:
  Tool selection accuracy: 86%
  Parameter extraction: 79%
  Direct answer accuracy: 82%

Step 100:
  Tool selection accuracy: 93%
  Parameter extraction: 91%
  Direct answer accuracy: 88%

Key observation: direct answer improves alongside tool use
  because the model learns a clearer decision boundary.
```

**Loss breakdown by token type:**
```
At step 100, average cross-entropy loss:
  Reasoning tokens:        0.42
  Tool name tokens:        0.18  (easiest: small closed vocabulary)
  Parameter JSON tokens:   0.55  (hardest: open-ended strings)
  Final answer tokens:     0.38
  Overall:                 0.41

The model masters tool names quickly but needs more steps
to learn precise parameter extraction for complex expressions.
```

---

### Common Confusion

1. **"Tool training is the same as instruction fine-tuning."** Instruction fine-tuning teaches the model to follow user instructions in natural language. Tool training is a specialized subset that teaches structured function calling, parameter extraction, and result integration. A model can be instruction-tuned without knowing tools, but tool training assumes instruction-following as a prerequisite.

2. **"You need real API calls to generate training data."** Synthetic data is the standard. You write templates that generate plausible queries and predetermined tool outputs. The model never executes tools during training; it only learns to generate the right text. Live APIs are only needed for evaluation.

3. **"Tool training makes the model dependent on specific tools."** The model learns a meta-pattern: "when you see a schema like this, emit a call like this." A model trained on calculator/weather/search can often generalize to a new "translate" tool with minimal examples because the structural pattern transfers.

4. **"All training examples must use tools."** No. A substantial fraction (30-40%) should be direct-answer examples. Without negative examples, the model calls tools for everything, including "Hello" and "Thank you."

5. **"Tool training requires full fine-tuning of all parameters."** LoRA works excellently for tool training because the task is about output formatting and decision boundaries, not deep semantic changes. A rank-16 LoRA on attention layers achieves 90%+ of full fine-tuning quality with <1% trainable parameters.

6. **"The model learns to execute tools during training."** The model learns to generate text that looks like a tool call. It has no knowledge of what the tool actually does. If you swap calculator for a random number generator, the model will still emit calculator calls because it learned the pattern, not the semantics.

7. **"Tool training hurts the model's general capabilities."** With proper data mixing (70% tool data, 30% general conversation) and small learning rates, general capabilities are preserved. The model simply gains a new mode of operation. Catastrophic forgetting only occurs if you over-train on a narrow tool dataset.

---

### Where It Is Used in Our Code

`src/phase126/phase126_tool_concepts.py` — We simulate the tool training data format and train a tiny classifier to distinguish tool-requiring queries from direct-answer queries. We demonstrate how ReAct trajectories are structured and why completeness matters.

`src/phase126/phase126_tool_colab.py` — We generate 500 synthetic tool-use training examples for calculator, weather, and search tools, format them with Qwen2.5's chat template, and fine-tune the model for 100 steps. We measure tool selection accuracy, parameter extraction accuracy, and direct-answer accuracy at each checkpoint, showing the training dynamics of tool specialization.
