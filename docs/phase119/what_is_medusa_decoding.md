## What Is Medusa Decoding?

---

### The Problem

Even with EAGLE's hidden-state conditioning, speculative decoding still requires a separate draft model. That means two models in memory, two forward passes to coordinate, and engineering complexity to keep them synchronized. For production systems already running at memory capacity, loading a second model is expensive. Is there a way to generate draft tokens without any separate model at all?

---

### Definition

**Medusa Decoding** is a speculative decoding method that adds multiple extra decoding heads directly onto the base (target) model itself. Each head predicts a token at a future time step: head 1 predicts t+1, head 2 predicts t+2, head 3 predicts t+3, and so on. No separate draft model is needed. During inference, all heads fire in parallel, producing a draft sequence that the base model then verifies in a single forward pass using tree attention.

**How it works:**
```
Standard autoregressive generation:
  Step 1: model(token_t) → token_t+1
  Step 2: model(token_t+1) → token_t+2
  Step 3: model(token_t+2) → token_t+3
  Total: 3 forward passes for 3 tokens

Medusa generation:
  Step 1: model(token_t) → token_t+1 (base head)
                          → draft_t+2 (Medusa head 1)
                          → draft_t+3 (Medusa head 2)
                          → draft_t+4 (Medusa head 3)
  Step 2: verify [draft_t+2, draft_t+3, draft_t+4] in ONE forward pass
          using tree attention
  Total: 2 forward passes for up to 4 tokens
```

**Key techniques:**
- **Multiple decoding heads:** each head is a small linear projection from the base model's hidden states to vocabulary logits
- **Head training:** heads are trained on the base model's own training data or generated outputs, learning to predict future tokens
- **Tree attention verification:** instead of verifying a linear draft chain, Medusa verifies a tree of possible token sequences in parallel
- **No separate model:** everything lives in the base model's parameter set

**Why this matters:**
- Medusa eliminates the memory and complexity cost of a separate draft model
- Typical speedups of 1.5-2.5x on language generation tasks
- The base model itself learns to "look ahead" multiple tokens
- Training the heads is cheap: they are small linear layers trained with standard cross-entropy

---

### Real-Life Analogy

Imagine a professional typist reading from a script.
- **Standard generation:** The typist reads one word, types it, reads the next word, types it. Each word requires a separate look-read-type cycle. Even though the typist is fast, the constant switching between reading and typing limits throughput.
- **Medusa:** The typist glances ahead and predicts the next three words while typing the current one. The typist's brain maintains a small "lookahead buffer" that guesses upcoming words based on context. After typing the current word, the typist verifies: "Did I guess the next three words correctly?" If yes, those words are already typed. If not, the typist backtracks to the first wrong word and resumes normal one-word-at-a-time typing from there.
- **The trade-off:** The typist must train their lookahead skill. At first, the guesses are poor and most get rejected. But after practice, the typist learns common phrases and sentence structures, making the lookahead buffer highly accurate. The cost is a small amount of extra mental effort (the extra heads) that pays off massively during long typing sessions.

---

### Tiny Numeric Example

**Base model with single head (standard):**
```
Forward pass at position t:
  Hidden state h_t = Transformer(token_0...token_t)
  Head 0 (base):  logits_0 = W_0 * h_t
  Next token: sample from softmax(logits_0)
  
Tokens per forward pass: 1
```

**Base model with Medusa heads (4 heads):**
```
Forward pass at position t:
  Hidden state h_t = Transformer(token_0...token_t)
  Head 0 (base):  logits_0 = W_0 * h_t  → predicts token_t+1
  Head 1:         logits_1 = W_1 * h_t  → predicts token_t+2
  Head 2:         logits_2 = W_2 * h_t  → predicts token_t+3
  Head 3:         logits_3 = W_3 * h_t  → predicts token_t+4

Draft sequence: [token_t+1, token_t+2, token_t+3, token_t+4]

Verification forward pass:
  Target model sees [token_0...token_t, token_t+1, token_t+2, token_t+3, token_t+4]
  Computes true distributions for positions t+1 through t+4
  Accepts tokens where draft matches target criteria

If all 4 accepted: 5 tokens in 2 forward passes (2.5x speedup)
If 2 accepted:     3 tokens in 2 forward passes (1.5x speedup)
```

**Training the Medusa heads:**
```
Training data: the base model's own training corpus
For each position t in a sequence:
  Loss_1 = cross_entropy(Head_1(h_t), token_t+2)
  Loss_2 = cross_entropy(Head_2(h_t), token_t+3)
  Loss_3 = cross_entropy(Head_3(h_t), token_t+4)
  Total loss = Loss_1 + Loss_2 + Loss_3
  
Only head weights are updated; base model stays frozen.
Heads are tiny (vocab_size x hidden_dim each) vs. base model (billions).
```

---

### Common Confusion

1. **"Medusa changes the base model weights."** No. The base model remains frozen. Only the small additional linear heads are trained. The base model's behavior is unchanged when the heads are removed.

2. **"Medusa heads are as large as the base model."** No. Each head is typically a single linear layer: hidden_dim -> vocab_size. For a 7B model with 4096 hidden dims and 32000 vocab, each head is only ~131M parameters. Four heads together are still tiny compared to the base.

3. **"Medusa and EAGLE are the same thing."** They share the goal of speculative decoding but differ in mechanism. EAGLE uses a separate draft model conditioned on hidden states. Medusa attaches draft heads directly to the base model with no separate model at all.

4. **"Medusa heads can predict arbitrarily far into the future."** In practice, accuracy drops sharply after 3-4 tokens. Most Medusa implementations use 4-5 heads because prediction quality degrades exponentially with lookahead distance.

5. **"Tree attention is unique to Medusa."** Tree attention is a general verification technique that can be used with any speculative method (EAGLE, Medusa, or classical draft models). Medusa popularized it because verifying multiple head predictions naturally forms a tree structure.

6. **"Medusa requires retraining the entire model."** No. The heads are trained in a separate phase after base model training. You can add Medusa heads to any existing pretrained model without touching its original weights.

7. **"Medusa only works for greedy decoding."** Medusa works with any sampling strategy (temperature, top-p, top-k). The verification step respects the target model's sampling distribution regardless of how the draft tokens were generated.

---

### Where It Is Used in Our Code

`src/phase119/phase119_speculative_concepts.py` — We simulate Medusa by attaching 4 heads to a base model. Each head predicts a future token, and we verify all predictions in parallel. We compare the expected tokens per forward pass against greedy and basic speculative decoding, showing the memory and coordination savings of not needing a separate draft model.

`src/phase119/phase119_speculative_colab.py` — While we do not train real Medusa heads (that requires a training loop on large data), we demonstrate the verification principle using real LLaMA models. We show how multiple draft tokens can be verified in a single forward pass and measure the theoretical speedup from in-model speculation.
