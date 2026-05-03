## What Is Grammar-Based Generation?

---

### The Problem

A developer wants an LLM to output a nested JSON object with specific fields and array types. She writes a detailed prompt, but the model sometimes omits required keys, uses wrong types, or inserts prose explanations. She tries post-processing with regex, but nested structures break her regex. She needs a way to bake the schema into the generation process itself so the model cannot violate it.

---

### Definition

**Grammar-Based Generation** is the practice of compiling a formal grammar (such as a JSON Schema, EBNF, or regex) into a finite-state machine (FSM) or pushdown automaton that guides the LLM's token sampler. At each generation step, only tokens that advance the FSM to a valid next state are permitted.

**How it works:**
```
JSON Schema → Grammar (EBNF) → FSM / Pushdown Automaton
At each step:
  1. FSM reads the partial output string
  2. FSM computes the set of allowed next characters
  3. Inference engine maps characters to token IDs
  4. Mask blocks every token ID not in the allowed set
  5. Model samples from masked distribution
```

**Key techniques:**
- JSON Schema to EBNF conversion (Outlines, XGrammar)
- Character-level FSM intersection with token vocabulary
- Precomputed token-to-character transition tables
- Pushdown automata for nested structures (parentheses, arrays)
- llama.cpp grammar mode (GBNF)

**Why this matters:**
- A schema guarantees field presence and type correctness
- Without grammar guidance, schema compliance is probabilistic
- API consumers depend on exact field names and types
- Nested objects and arrays are impossible to enforce with regex alone

---

### Real-Life Analogy

An assembly line with custom jigs.
- **Prompt-only generation:** A worker assembles furniture from a text description. They might skip a screw, use the wrong panel, or add decorative parts not in the instructions. Quality control catches errors at the end, requiring disassembly and rework.
- **Grammar-based generation:** Each workstation on the assembly line has a physical jig that only accepts the correct part. The worker cannot insert a long screw where a short one belongs because the jig blocks it. The furniture is guaranteed to match the blueprint at every stage.
- **The trade-off:** Designing and machining the jigs takes upfront engineering effort. Similarly, converting a schema to a token-level mask requires preprocessing. For simple schemas the overhead is small; for complex nested grammars it can be significant. The trade-off is setup cost for perfect compliance.

---

### Tiny Numeric Example

**Schema:** `{"name": string, "age": int}`

**Grammar states (simplified):**
```
State 0: expect '{'
State 1: expect '"name"'
State 2: expect ':'
State 3: expect string literal
State 4: expect ','
State 5: expect '"age"'
State 6: expect ':'
State 7: expect integer
State 8: expect '}'
```

**Partial output:** `{"name":"Alice",`
Current state: State 4 (after comma)
Allowed next tokens: only those starting with `"age"` (e.g., token `"age"`)

**If model logits favor `"name"` (0.6) and `"age"` (0.4):**
```
Before mask:
  "name" → 0.60
  "age"  → 0.40

After mask (state 4 only allows "age"):
  "name" → 0.00
  "age"  → 1.00
```

---

### Common Confusion

1. **"Grammar-based generation requires retraining the model."** No. The model weights are frozen. Only the inference-time sampler is modified.

2. **"Any tokenizer works equally well."** Byte-level tokenizers make grammar intersection easier because tokens map cleanly to characters. BPE tokenizers can split single characters into subword pieces, complicating the FSM.

3. **"The FSM operates on tokens directly."** The FSM typically operates on characters or bytes. The inference engine computes which tokens are prefixes of valid continuations.

4. **"Outlines and XGrammar do the same thing."** They share the goal but differ in implementation. XGrammar compiles to efficient GPU kernels; Outlines uses Python-based FSM intersection.

5. **"Grammar-based generation is slower because the model is smaller."** The model is the same size. Overhead comes from FSM state tracking and mask computation, not from the forward pass.

6. **"If a token is partially valid, it is allowed."** A token is only allowed if every possible completion of that token leads to a valid string. Partial validity is insufficient.

7. **"You can express any constraint with a regex."** Regex cannot match nested brackets or enforce field ordering. Context-free grammars are required for JSON and SQL.

---

### Where It Is Used in Our Code

`src/phase115/phase115_constrained_concepts.py` — We define a tiny grammar for JSON with string keys and integer values. We show how each grammar state restricts the next token, and we visualize the token mask at each decoding step.
