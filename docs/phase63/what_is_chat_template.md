## What Is a Chat Template?

---

### The Problem

A language model only understands sequences of tokens. It has no built-in concept of "user" and "assistant." How do you format a multi-turn conversation so the model knows who said what, where the user's turn ends, and where the assistant's response begins?

---

### Definition

A **chat template** is a string formatting pattern that wraps conversation turns with special tokens, teaching the model the structure of dialogue: who is speaking, when a turn starts, and when the assistant should generate a response.

**Llama-3 chat template:**
```
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

What is 2+2?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

4<|eot_id|>
```

**Key components:**
- **Role tokens:** `<|user|>`, `<|assistant|>`, `<|system|>` — identify who is speaking
- **Header markers:** `<|start_header_id|>`, `<|end_header_id|>` — delimit the role from the content
- **Turn separators:** `<|eot_id|>` (end of turn) — marks where one turn ends and the next begins
- **System prompt:** Optional instructions given before the conversation starts

**Why this matters:**
- Without a template, the model cannot distinguish user input from assistant output
- Different models use different templates (Llama, GPT, Mistral, Gemma all differ)
- The tokenizer's `apply_chat_template` function handles this automatically

---

### Real-Life Analogy

A play script.
- **Without template:** "Hello. How are you? I am fine. What is the weather? It is sunny."
- **With template:**
  ```
  [USER]: Hello.
  [ASSISTANT]: How are you?
  [USER]: I am fine. What is the weather?
  [ASSISTANT]: It is sunny.
  ```
- **The actors (model)** need stage directions to know who speaks when. The chat template is the script formatting.

Different theaters (models) use different conventions: some use `[CHARACTER]`, others use `CHARACTER:`, others use XML tags. The chat template is the specific convention your model was trained with.

---

### Tiny Numeric Example

**Conversation:**
```
System: "You are a helpful math tutor."
User: "What is 2+2?"
Assistant: "4"
```

**Without template (just concatenated):**
```
You are a helpful math tutor. What is 2+2? 4
```
The model might generate: "8, 16, 32..." because it thinks this is a counting exercise.

**With Llama-3 template:**
```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful math tutor.<|eot_id|><|start_header_id|>user<|end_header_id|>

What is 2+2?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

4<|eot_id|>
```

**Tokenized (simplified, token IDs):**
```
[128000, 128006,   9125, 128007,   271,   9906,   596,   645,
  358,  9867,   284,   433, 128009, 128006,   882, 128007,
  271,   3923,   374,   220,  1417,   30, 128009, 128006,
  78191, 128007,   271,    19, 128009]
```

The model sees the structure. It learns: after `<|start_header_id|>assistant<|end_header_id|>`, I should generate the answer until `<|eot_id|>`.

---

### Common Confusion

1. **"All models use the same chat template."** No. Llama uses `<|start_header_id|>`. Mistral uses `[INST]` and `[/INST]`. GPT uses a JSON format. Using the wrong template breaks the model.

2. **"Chat templates are just for pretty printing."** No. They are structural. The model was trained on them. Removing the template is like removing punctuation from English — the model becomes confused.

3. **"You can invent your own template."** Only if you train the model from scratch with it. For pre-trained models, you MUST use the template they were trained with.

4. **"The system prompt is optional."** Technically yes, but it dramatically changes behavior. "You are a helpful assistant" vs "You are a pirate" produce completely different outputs.

5. **"Chat templates waste tokens."** They do add overhead (~10-30 tokens per turn). But without them, the model cannot function as a chatbot. The overhead is necessary.

---

### Where It Is Used in Our Code

`src/phase63/phase63_dataset_curation.py` — We implement a simplified chat template parser that wraps raw conversation turns with role tokens and turn separators, showing how unstructured text becomes structured training data.
