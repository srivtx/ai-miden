### 1. Why it exists (THE PROBLEM first)
Language models have knowledge cutoff dates and cannot perform precise calculations, access real-time information, or interact with private databases. Asking a model to compute "the 47th Fibonacci number" or "today's stock price" from memory leads to hallucination. Tools extend the model's capabilities beyond its training data.

### 2. Definition (very simple)
Tool Use is the ability of an AI agent to call external functions, APIs, or programs during inference. The model decides which tool to call, formats the arguments correctly, receives the output, and incorporates it into its reasoning.

### 3. Real-life analogy
A chef can estimate temperature by touch, but for precision they use a thermometer. The thermometer is a tool that extends the chef's natural ability. Similarly, a calculator extends a language model's math ability, and a search engine extends its knowledge beyond the training cutoff.

### 4. Tiny numeric example
The model is asked: "What is 12345 x 67890?"

Without a tool:
"12345 x 67890 is approximately 837 million." (Wrong. Actual: 838,102,050.)

With a calculator tool:
1. Model decides: "This requires precise multiplication. I will use the calculator tool."
2. Model outputs tool call: `calculator.multiply(12345, 67890)`
3. Tool returns: `838102050`
4. Model answers: "12345 x 67890 = 838,102,050."

The model did not compute the answer itself. It delegated to a tool that is guaranteed to be correct.

### 5. Common confusion
- **Tool use is not retrieval-augmented generation (RAG).** RAG feeds documents into the context before generation. Tool use calls live functions during generation. They can be combined: a search tool retrieves documents, then the model reads them.
- **The model does not execute the tool.** It generates a JSON or function call. External code actually runs the tool and returns the result. The model is the caller, not the runner.
- **Tool descriptions matter.** The model chooses tools based on their names and descriptions. A poorly described tool will never be called even when it is exactly what is needed.
- **Not all models support tool use natively.** Some models must be fine-tuned to output structured function calls. Others use prompting tricks to simulate tool use.
- **Tools can be chained.** The output of one tool can become the input to the next. For example: search → read webpage → summarize → write email.

### 6. Where it is used in our code
`src/phase27/phase27_agentic_ai.py` registers two tools (calculator and search) and shows how the model selects the right tool based on the problem type, formats arguments, and uses the returned result.
