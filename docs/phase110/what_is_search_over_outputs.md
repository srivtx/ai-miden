## What Is Search Over Outputs?

---

### The Problem

Language models generate text autoregressively, one token at a time. A single sampled path through the token space may miss better answers that diverge at an early token. A wrong arithmetic step at position 3 can doom an entire mathematical proof. A vague topic sentence at the start can derail an essay. How do you explore the output space systematically rather than gambling on one path?

---

### Definition

**Search Over Outputs** is the practice of generating multiple candidate outputs and using a search or selection algorithm to find or construct the best one. Methods include best-of-N sampling, beam search, tree-of-thoughts, and Monte Carlo Tree Search applied to reasoning steps.

**How it works:**
```
Prompt → Generate multiple candidate outputs
Verifier scores each candidate
Search algorithm: expand promising partial solutions, prune bad branches
Return highest-scoring complete output
Result: higher-quality solutions by exploring the output distribution
```

**Key techniques:**
- **Best-of-N:** sample N full outputs independently, pick the best via a verifier
- **Beam search:** maintain K partial sequences, expand the top candidates at each step
- **Tree-of-thoughts / MCTS:** explore reasoning steps as nodes in a search tree with expansion and backpropagation

**Why this matters:**
- Finds answers that a single greedy or sampled path would miss
- Enables structured reasoning by treating steps as nodes in a search tree
- Central to competitive math, coding, and scientific discovery systems

---

### Real-Life Analogy

Search over outputs is like navigating a maze by sending out multiple explorers. Instead of picking one path and hoping it leads to the exit, you dispatch several teams with different strategies. Each reports back what they found, and you choose the path with the best outcome. Some explorers hit dead ends; others find shortcuts you would never have discovered alone.

The trade-off is resources. Sending ten explorers costs ten times as much as sending one. Search over outputs is sending those explorers into the space of possible answers, and the cost is compute. A team of one might get lucky; a team of ten is more likely to find the exit but requires ten times the food, water, and time. The same applies to language generation: exploring more candidates requires more inference compute.

---

### Tiny Numeric Example

**Math problem:** "What is 17 * 23?"

**Greedy decoding (single path):**
```
Output: "17 * 20 = 340, plus 17 * 3 = 51, total = 381"
Answer: 381 (wrong, arithmetic error)
Confidence: 0.72
```

**Beam search (K=3):**
```
Path A: "17*20=340, +51=381"     → verifier score 0.3
Path B: "17*23=391"              → verifier score 0.9
Path C: "10*23=230, 7*23=161, 230+161=391" → verifier score 0.95
Selected: Path C (step-by-step with correct arithmetic)
```

**Best-of-N (N=8):**
```
Outputs: [381, 391, 391, 390, 392, 391, 391, 381]
Verifier (exact match to known answer):
  391 → score 1.0
  others → score 0.0
Selected: 391 (5 out of 8 candidates correct)
Accuracy: 62.5% vs 37.5% for single sample
```

**Search improves accuracy by exploring paths that greedy decoding would prune.**

---

### Common Confusion

1. **"Search over outputs is just generating more samples."** It requires a scoring or verification mechanism to discriminate good outputs from bad; random sampling without selection does not reliably improve quality.

2. **"Beam search is always better than sampling."** Beam search often produces generic, high-probability text. Diverse sampling with a strong verifier can outperform beam search on creative or complex reasoning tasks.

3. **"Tree-of-thoughts requires a special model architecture."** It is primarily an inference algorithm; any model that generates text can be used with tree-of-thoughts prompting and search.

4. **"Search eliminates the need for a good base model."** A weak model generates mostly wrong candidates, and even a perfect verifier cannot fix a pool that contains zero correct answers.

5. **"MCTS is too slow for language generation."** With efficient pruning and small branching factors, MCTS has been used at 10-100 reasoning steps per second in practice.

6. **"Search over outputs is only for text."** It applies to any generative model, including code, protein structures, robot trajectories, molecular designs, and image generation.

7. **"A verifier must be a separate trained model."** Verifiers can be rule-based checkers, execution environments, unit tests, or even the same model prompted to evaluate its own output.

---

### Where It Is Used in Our Code

`src/phase110/phase110_test_time_compute.py` — We implement best-of-N sampling where a verifier scores each candidate output. We sweep N from 1 to 128 and show how a strong verifier achieves steep accuracy gains while a weak verifier plateaus early. The accuracy versus N curve is saved as `src/phase110/best_of_n_tradeoff.png`.
