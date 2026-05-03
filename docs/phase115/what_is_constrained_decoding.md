## What Is Constrained Decoding?

---

### The Problem

An API receives thousands of requests per second. Each request asks the LLM to return JSON with specific fields. Without constraints, the model sometimes outputs markdown fences, trailing commas, or prose explanations before the JSON. Post-processing parsers fail, retries burn money, and downstream systems crash. Prompt engineering helps, but it is probabilistic: the model can still deviate because the next-token sampler sees the full vocabulary at every step. How do you guarantee syntactic validity at the token level instead of hoping the prompt is followed?

---

### Definition

**Constrained Decoding** is the technique of restricting the model's next-token distribution to only those tokens that keep the partial output compliant with a formal grammar or schema. Instead of asking the model to behave, the decoder masks out invalid options before sampling.

**How it works:**
```
Base generation: sample from full vocabulary (50,000 tokens)
Constrained generation: at each step, compute valid token subset (e.g., 12 tokens)
Mask: set probability of invalid tokens to zero, renormalize
Result: every emitted token preserves grammatical validity
```

**Key techniques:**
- Finite-state machine (FSM) tracking of grammar state
- Token-vocabulary intersection with grammar transitions
- Dynamic token masking at each generation step
- Integration with beam search or greedy decoding

**Why this matters:**
- A finance API cannot afford a malformed JSON response
- SQL generation must be syntactically valid before execution
- Retry loops add latency and cost; masking eliminates retries
- Temperature greater than 0 with constraints still guarantees validity

---

### Real-Life Analogy

A crossword puzzle with a strict dictionary.
- **Unconstrained decoding:** You write any letters that come to mind. Sometimes you make up words that look right but are not in the puzzle's dictionary. The crossword checker rejects them, and you erase and try again, wasting time.
- **Constrained decoding:** At every blank, you are only allowed to write letters that form valid words with the intersecting clues. You never write an invalid letter because the option is physically removed. The puzzle is guaranteed to be correct as you fill it.
- **The trade-off:** Checking the dictionary at every step takes extra time. Generation is slightly slower because the decoder must compute the valid subset, but the result is correct on the first try. The trade-off is latency for reliability.

---

### Tiny Numeric Example

**Vocabulary (toy):** `{ "name", ":", "\"Alice\"", ",", "\"age\"", "25", "}", "invalid", "bad" }`

**Prompt:** `{"name":`

**Without constrained decoding:**
```
Next-token probabilities:
  "\"Alice\"" → 0.45
  "\"age\""   → 0.30
  "}"         → 0.15
  ","         → 0.10
```
Sampled token: `"age"` → Output: `{"name":"age` (invalid JSON)

**With constrained decoding (JSON string value expected):**
```
Valid tokens: {"\"Alice\""}
Invalid tokens: {"\"age\"", "}", ","}
Next-token probabilities (after mask):
  "\"Alice\"" → 1.00
```
Sampled token: `"Alice"` → Output: `{"name":"Alice"` (valid so far)

**Probability mass redistribution:**
```
Before mask: valid mass = 0.45, invalid mass = 0.55
After mask:  valid mass = 1.00, invalid mass = 0.00
The 0.55 mass was redistributed to the only valid token.
```

---

### Common Confusion

1. **"Constrained decoding is the same as prompt engineering."** Prompt engineering asks the model to behave. Constrained decoding forces the behavior by removing invalid options at the token level.

2. **"It works by validating after generation."** Post-hoc validation rejects bad outputs and retries. Constrained decoding prevents invalid tokens from being emitted in the first place.

3. **"You need a special model."** Most open-weight models (Llama, Qwen, Mistral) support constrained decoding through inference engines like vLLM, llama.cpp, or Outlines. The base model stays the same.

4. **"Constraints hurt output quality."** Constraints only affect syntactic form, not semantic content. The model still chooses among all valid tokens, so meaning remains unconstrained.

5. **"It only works for JSON."** Constrained decoding works for any context-free grammar: SQL, regex, Python code, chemical formulas, and custom domain-specific languages.

6. **"Greedy decoding is enough for structured output."** Greedy decoding without constraints still samples from the full vocabulary. A high-probability invalid token can still be chosen.

7. **"Masking is done once at the start."** The valid token set changes at every step as the grammar state evolves. After a `{`, the valid tokens are different from after a `,`.

---

### Where It Is Used in Our Code

`src/phase115/phase115_constrained_concepts.py` — We simulate a toy vocabulary and a tiny JSON grammar. We show how a dynamic mask is built at each step, how greedy decoding with the mask produces only valid sequences, and how invalid probability mass is redistributed to valid tokens.
