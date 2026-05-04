## What Is MCTS for LLMs?

---

### The Problem

Best-of-N sampling improves output quality by generating N candidates and picking the best one. But it is wasteful: if the first 10 tokens of a generation are obviously bad, best-of-N still completes all N sequences before discarding them. A human writer does not do this. If the first sentence of an essay is nonsense, they stop and try a different opening. How do you make a language model explore the output space strategically, abandoning bad branches early and investing compute where it matters?

---

### Definition

**Monte Carlo Tree Search (MCTS) for LLMs** is a tree search algorithm adapted for discrete text generation. It builds a search tree where each node is a partial sequence of tokens. The algorithm repeatedly selects promising nodes, expands them by generating the next token, simulates a full completion from that point, scores the result with a reward model or verifier, and backpropagates the score to update value estimates up the tree. It replaces blind sampling with directed exploration.

**How it works:**
```
Root: "Solve: 24 / (8 - 2) = "

Iteration 1:
  Select root (only node)
  Expand: generate 4 candidate next tokens: "4", "3", "6", "Let's"
  Simulate: complete each to a full answer with greedy decoding
  Score:  "4" → correct (1.0)
          "3" → incorrect (0.0)
          "6" → incorrect (0.0)
          "Let's" → incorrect (0.0)
  Backprop: update value estimates. "4" now has value 1.0.

Iteration 2:
  Select root again (UCB1 balances exploration)
  Expand a new child (or re-simulate existing)
  ...

After 20 iterations:
  The path "4" has been visited most and has highest value.
  Final answer: "4"
```

**The four MCTS phases:**
- **Selection:** traverse the tree from root to leaf using the UCB1 formula, which balances exploitation (high-value nodes) with exploration (under-sampled nodes).
- **Expansion:** at the selected leaf, generate K candidate next tokens, creating new child nodes.
- **Simulation (rollout):** from each new child, complete the sequence to a final answer using a fast policy (e.g., greedy or temperature sampling).
- **Backpropagation:** score the completed sequence and update the visit counts and value estimates of all ancestors.

**Why this matters:**
- MCTS prunes bad branches after a few tokens instead of after a full generation, saving compute
- It finds answers that best-of-N misses because best-of-N cannot backtrack after choosing a bad first token
- It is the core algorithm behind AlphaGo and has been adapted for code generation, math reasoning, and theorem proving

---

### Real-Life Analogy

Writing an essay with an outline and draft feedback.
- **Best-of-N:** You write 20 complete essays, read all of them, and pick the best one. If the first paragraph of 19 essays is terrible, you wasted 19 full essays' worth of effort.
- **MCTS:** You write the first sentence of 4 different openings. A teacher (the reward model) grades each sentence. One is promising. You expand that opening into a full paragraph and grade it. Another branch looks weak after two sentences, so you abandon it and try a different path. You invest your writing effort where the feedback is positive.
- **The advantage:** You never finish a bad essay. You explore promising openings deeply and kill bad ones early. With the same total word count, you produce a better final essay than best-of-N.

---

### Tiny Numeric Example

**Task:** Solve "What is 15 - 3 * 2?"
**Correct answer:** 9 (not 24).

**Greedy decoding:**
```
Generation: "15 - 3 = 12, 12 * 2 = 24. The answer is 24."
Score: 0.0 (incorrect)
```

**Best-of-8:**
```
Sample 1: "24" → 0.0
Sample 2: "9"  → 1.0   (found by luck)
Sample 3: "24" → 0.0
...
Sample 8: "6"  → 0.0
Best answer: "9" (1/8 correct)
```

**MCTS (4 iterations, 2 children per expansion):**
```
Root: "What is 15 - 3 * 2?"

Iter 1: expand "15" and "3"
  Rollout from "15": "15 - 3 = 12, 12 * 2 = 24" → 0.0
  Rollout from "3":  "3 * 2 = 6, 15 - 6 = 9"   → 1.0
  Backprop: "3" gets value 1.0

Iter 2: UCB1 selects "3" (high value)
  Expand "3 *" and "3 -"
  Rollout from "3 *": "3 * 2 = 6, 15 - 6 = 9" → 1.0
  Rollout from "3 -": "3 - 2 = 1, 15 * 1 = 15" → 0.0
  Backprop: "3 *" gets value 1.0

Iter 3-4: tree converges on "3 * 2 = 6, 15 - 6 = 9"
Final selected path: "9"
```

MCTS finds the correct answer by exploring the operator order, not by random luck. With 4 iterations it achieves what best-of-8 does with random sampling.

---

### Common Confusion

1. **"MCTS is just beam search."** No. Beam search keeps the top-k partial sequences at every step based on local probability. MCTS uses a value function that estimates final quality, and it balances exploration via UCB1. Beam search is greedy and local; MCTS is global and exploratory.

2. **"MCTS requires a perfect reward model."** A perfect reward model helps, but MCTS still outperforms best-of-N with a noisy reward model because it allocates more compute to promising branches. The reward model only needs to be directionally correct on average.

3. **"MCTS is too slow for real-time applications."** It is slower than greedy decoding, but the cost is comparable to best-of-N when configured with the same total compute budget. The key advantage is efficiency: MCTS spends less compute on obviously bad paths.

4. **"The simulation step must use the same model as expansion."** Not necessarily. You can use a smaller, faster model for rollouts (the "policy network") and a larger model for expansion (the "value network"). This is common in game-playing MCTS and is being adapted for LLMs.

5. **"MCTS only works for tasks with verifiable answers."** It works best when the reward model can score completions (math, code, logic puzzles). For open-ended creative writing, defining a reward is harder, though human preference models can still provide weak rewards.

6. **"More iterations always means better answers."** Diminishing returns set in after the tree covers the most promising paths. If the reward model is poor, additional iterations just reinforce bad paths. There is an optimal iteration count for each task and model.

7. **"MCTS finds the globally optimal answer."** No. MCTS is a heuristic search. It finds good answers efficiently but does not guarantee optimality. In practice, it finds better answers than greedy or best-of-N with the same budget, but not necessarily the best possible answer.

---

### Where It Is Used in Our Code

`src/phase138/phase138_mcts_concepts.py` — We simulate MCTS on a toy grid-path problem. We build a search tree, implement UCB1 selection, run rollouts with random policies, backpropagate rewards, and compare the solution quality against random search and beam search. We visualize tree growth and value estimates over iterations.

`src/phase138/phase138_mcts_colab.py` — We implement MCTS for math word problems using `Qwen/Qwen2.5-3B-Instruct` on a T4 GPU. Each node is a partial reasoning chain. We expand nodes by generating the next reasoning step, simulate completions with greedy decoding, score them with a correctness checker, and backpropagate. We compare MCTS (20 iterations) against greedy decoding and best-of-8 sampling.
