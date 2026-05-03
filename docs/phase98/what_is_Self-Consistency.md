## What Is Self-Consistency?

---

### The Problem

A language model answers a multi-step math problem by generating a single chain of reasoning. Even if the model is generally capable, one unlucky early mistake — a flipped sign, a miscounted step — propagates through the rest of the chain and yields a wrong final answer. There is no mechanism to catch or recover from that mistake because the model committed to one path and never looked back. How do you make reasoning robust against the noise of a single sampled chain?

---

### Definition

**Self-Consistency** is an inference-time technique where multiple independent reasoning chains are sampled from the same model for the same prompt, and the final answer is chosen by majority vote among the chains. It turns one noisy draw into an ensemble of paths, allowing correct reasoning to outvote isolated errors.

**How it works:**
```
Prompt: "Roger has 5 tennis balls. He buys 2 more cans of 3 balls each. How many does he have now?"
Chain 1: 5 + 2*3 = 11  -> answer: 11
Chain 2: 5 + 2 = 7, 7 + 3 = 10  -> answer: 10 (wrong)
Chain 3: 5 + (2*3) = 11  -> answer: 11
Chain 4: 2 cans * 3 = 6, 6 + 5 = 11  -> answer: 11
Chain 5: 5 + 2 = 7, 7 * 3 = 21  -> answer: 21 (wrong)
Majority vote: 11 appears 3 times -> final answer: 11
```

**Key properties:**
- Purely a test-time strategy; no training changes are required.
- Compute cost scales linearly with the number of sampled chains.
- Works best when errors are uncorrelated across samples.

**Why this matters:**
- A single chain might achieve 60% accuracy on grade-school math; self-consistency with 10 samples can push that to 80%.
- It is one of the cheapest ways to boost reasoning without modifying the model weights.
- It provides a natural uncertainty estimate: a split vote signals low confidence.

---

### Real-Life Analogy

Imagine a panel of twelve jurors deliberating a complex case. Each juror reviews the evidence independently and reaches a verdict. No single juror is infallible — some may misremember a witness statement, others may overvalue a piece of circumstantial evidence. But when all twelve vote, the random errors of individuals tend to cancel out, and the consensus converges on the correct outcome far more often than any one juror alone. Self-consistency is that jury: it replaces a single judgment with an independent ensemble.

The trade-off is cost and time. A jury of twelve takes twelve times longer to hear a case than a single judge. Similarly, sampling ten reasoning chains costs ten times the compute of one chain. For simple questions, the overhead is wasteful. For high-stakes reasoning — medical diagnosis, legal analysis, engineering calculations — the cost is justified by the reliability gain. There is also a subtle risk: if the model has a systematic bias (for example, it consistently mishandles a particular type of word problem), all twelve jurors may share that bias, and the majority vote will reinforce the error rather than cancel it.

---

### Tiny Numeric Example

**Single-chain accuracy on an 8-step reasoning task:**
```
Per-step correctness probability: 0.85
Probability all 8 steps are correct: 0.85^8 = 0.272
Single-chain accuracy: 27.2%
```

**Self-consistency with 10 sampled chains:**
```
Probability a single chain is fully correct: 0.272
Probability at least 6 out of 10 chains are correct (majority vote wins):
  Sum from k=6 to 10 of C(10,k) * 0.272^k * (1-0.272)^(10-k)
  = 0.156 + 0.058 + 0.014 + 0.002 + 0.0002
  = 0.230
```

Wait — that seems worse. The key insight is that **even incorrect chains often agree by chance** on the final answer. Let us refine with a more realistic assumption: 40% of chains are fully correct, 30% make an independent error that still lands on the correct answer, and 30% make an error that lands on a wrong answer.

```
Effective "correct answer" rate per chain: 70%
Self-consistency accuracy (majority of 10, p=0.70):
  P(at least 6 agree on correct answer) = 0.850
```

**Accuracy comparison table:**
```
Method                   | Accuracy | Compute (relative)
-------------------------|----------|-------------------
Single chain             | 40.0%    | 1x
Self-consistency (5)     | 68.4%    | 5x
Self-consistency (10)    | 85.0%    | 10x
Self-consistency (20)    | 92.4%    | 20x
```

**The shift:** Majority voting extracts signal from noisy samples. Diminishing returns set in after roughly ten chains, but the first few samples provide the largest accuracy gains.

---

### Common Confusion

1. **"Self-consistency is a training technique."** It is not. It operates entirely at inference time. The model weights are frozen; only the sampling and voting strategy changes.

2. **"Self-consistency is the same as model ensembling."** Model ensembling combines predictions from multiple different models. Self-consistency uses the same model sampled multiple times. The diversity comes from stochastic decoding, not from architectural differences.

3. **"More samples always help."** Not beyond a point. Once the majority vote stabilizes, additional samples waste compute. Gains are typically sharpest between 3 and 10 samples, then flatten.

4. **"Self-consistency fixes systematic errors."** No. If every sampled chain repeats the same flawed reasoning pattern, the majority will simply be confidently wrong. It only helps with uncorrelated noise.

5. **"You need a complex voting mechanism."** A simple majority vote on the final answer is usually sufficient. Weighted votes or semantic similarity clustering help in niche cases but are not required.

6. **"Self-consistency only works for math."** It works for any task with a verifiable final answer: code generation, logical deduction, factual question answering, and even multiple-choice classification.

7. **"It is the same as Chain-of-Thought."** Chain-of-Thought is the structure of the reasoning steps. Self-consistency is the aggregation strategy applied to multiple CoT samples. They are complementary, not interchangeable.

---

### Where It Is Used in Our Code

`src/phase98/phase98_system2_reasoning.py` — We simulate an 8-step reasoning chain where each step is correct with probability 0.85. We compare single-chain accuracy against self-consistency accuracy across varying per-step correctness probabilities and chain lengths, and we plot the accuracy curves to show where self-consistency provides the largest gains.
