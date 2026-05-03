# What is Function Calling?

## 1. Why it exists (THE PROBLEM)
LLMs output unstructured text. If you want an agent to reliably trigger a specific piece of code—like `send_email(to, subject, body)`—parsing free-form text is fragile and error-prone. One time it returns "Email sent to Bob," another time "I sent it." Function Calling forces the model to output a predictable, machine-readable structure (JSON) that maps exactly to your code's signature.

## 2. Definition
Function Calling is a model capability where the LLM is given a list of available functions (with JSON schemas describing their names, parameters, and types) and outputs a JSON object representing which function to call and with what arguments.

## 3. Real-life analogy
A restaurant waiter taking an order. The menu lists dishes with descriptions (schemas). You (the model) do not walk into the kitchen and cook; you write the order on a ticket (JSON) with item codes and modifications. The kitchen (host system) reads the ticket and prepares the meal.

## 4. Tiny numeric example
Available function schema:
```json
{
  "name": "multiply",
  "parameters": {
    "type": "object",
    "properties": {
      "x": {"type": "number"},
      "y": {"type": "number"}
    },
    "required": ["x", "y"]
  }
}
```
Prompt: "Multiply 7 by 8."
Model output:
```json
{"name": "multiply", "arguments": {"x": 7, "y": 8}}
```
System executes `multiply(7, 8)` → `56`.

## 5. Common confusion
- **"Function calling is just JSON mode."** JSON mode forces JSON; function calling forces a specific schema tied to a named function.
- **"The model validates the JSON schema."** No. The host system must validate arguments before executing.
- **"Function calling only works with OpenAI."** No. Many open models (Llama, Mistral, Qwen) support it via fine-tuning or prompt templates.
- **"You must have a real function with that name in code."** You do, but the model does not know your internal code; it only knows the schema you provide.
- **"Function calling guarantees correct arguments."** No. The model can hallucinate values or types; always validate.
- **"It is only for simple functions."** Schemas can be nested and complex, describing rich APIs.
- **"Function calling replaces prompt engineering."** You still need good prompts and system messages to guide the model.

## 6. Where it is used in our code
In `src/phase72/phase72_real_agents_colab.py`, we define three function schemas (`calculator`, `web_search`, `weather`). The mock LLM inspects these schemas and generates a JSON tool call. The host parser validates the JSON and dispatches to the corresponding Python function.
