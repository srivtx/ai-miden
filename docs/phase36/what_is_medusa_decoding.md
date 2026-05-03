## What Is Medusa Decoding?

---

### The Problem

Speculative decoding requires two models: a draft and a target. Loading two models doubles memory. Keeping their KV caches synchronized is complex. Can we get speculative speedup without a separate draft model?

---

### Definition

**Medusa** is a speculative decoding method that adds multiple prediction heads directly to the target model. Instead of a separate draft model, the target model itself predicts future tokens.

**Architecture:**
- Head 0 (standard): predict token t+1
- Head 1: predict token t+2
- Head 2: predict token t+3
- ... up to K heads

All heads share the same backbone. During training, all heads are trained jointly on next-token prediction. At inference:
1. Run one forward pass through the backbone
2. All K heads generate K candidate tokens simultaneously
3. The standard head (Head 0) verifies the candidates
4. Accept/reject using the same acceptance sampling as speculative decoding

**Advantages:**
- No separate model to load or maintain
- No KV cache synchronization between two models
- Heads are small (just linear layers on top of hidden states)
- Can be trained on the same data as the base model

---

### Real-Life Analogy

A chess player who, during each turn, not only decides their current move but also thinks ahead: "If I move my knight here, they will likely respond with their bishop, then I can castle, then they might push a pawn..." The player generates a candidate sequence of moves in their head.

Then they evaluate the entire candidate sequence: "Is my knight move good? Given that, is their bishop response likely? Given both, is my castle still strong?" They accept the line until they find a move they disagree with, then they rethink from that position.

Medusa is the same idea: the model predicts its own future and then verifies its own predictions.

---

### Tiny Numeric Example

**Hidden state:** h = [1.0, 0.5, -0.3]

**Head 0 (next token):**
```
W0 = [[0.2, 0.1, 0.5],
      [0.3, 0.4, 0.1],
      [0.1, 0.2, 0.3]]

logits_0 = h @ W0 = [0.25, 0.52, 0.02]
probs_0 = softmax([0.25, 0.52, 0.02]) = [0.32, 0.55, 0.13]
→ Predict token B (55% probability)
```

**Head 1 (token after next):**
```
W1 = [[0.1, 0.3, 0.2],
      [0.4, 0.1, 0.5],
      [0.2, 0.3, 0.1]]

logits_1 = h @ W1 = [0.21, 0.60, 0.22]
probs_1 = softmax([0.21, 0.60, 0.22]) = [0.28, 0.52, 0.20]
→ Predict token B (52% probability)
```

**At inference:**
- Head 0 says: next token is B
- Head 1 says: token after that is also B
- Candidate sequence: [B, B]
- Verify: run target on prefix + [B, B]
- If both accepted, we generated 2 tokens in 1 forward pass

---

### Common Confusion

1. **"Medusa changes the model architecture permanently."** Yes, but minimally. You add K small linear heads to the existing model. The backbone is unchanged. You can still use the model without Medusa heads by ignoring them.

2. **"Medusa heads are as good as a separate draft model."** Typically, Medusa achieves 50–70% acceptance rate, while a well-matched separate draft model achieves 70–85%. Medusa trades some acceptance rate for the convenience of not needing a second model.

3. **"Training Medusa heads requires new data."** No. You can train them on the exact same next-token prediction data used for the base model. The heads just have different targets: head k predicts the token k steps ahead.

4. **"Medusa only works for language models.""** The concept applies to any autoregressive model. Medusa-style heads have been explored for image generation (predicting future latent tokens) and speech.

5. **"All Medusa heads predict independently."** They share the same backbone representation, so their predictions are conditioned on the same context. However, head k does NOT see the prediction from head k-1 — it predicts purely from the original hidden state.

---

### Where It Is Used in Our Code

`src/phase36/phase36_speculative_decoding_colab.py` — A simplified Medusa-style multi-head prediction in PyTorch. Shows how multiple heads generate candidates and the base head verifies them.
