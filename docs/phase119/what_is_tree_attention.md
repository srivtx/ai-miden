## What Is Tree Attention?

---

### The Problem

In speculative decoding, the draft model generates a linear chain of candidate tokens: [t+1, t+2, t+3, t+4]. The target model verifies them one by one. If token t+2 is rejected, tokens t+3 and t+4 are discarded even though some of them might have been correct. Worse, when using multiple Medusa heads, each head proposes an independent token at a different depth, creating not a chain but a tree of possibilities. How do we verify all these branches without running a separate forward pass for each one?

---

### Definition

**Tree Attention** is a mechanism that verifies multiple speculative token sequences simultaneously by structuring the attention mask as a tree rather than a linear chain. Each node in the tree represents a token, and edges represent draft hypotheses. The target model processes the entire tree in a single forward pass, computing attention only along valid parent-child paths. After the forward pass, each branch is checked for acceptance independently, and the longest valid prefix is kept.

**How it works:**
```
Linear speculative decoding (inefficient):
  Draft: A → B → C → D
  Verify A: accepted
  Verify B: rejected
  Result: discard C and D, even if they were correct
  Wasted work: C and D were computed for nothing

Tree attention (efficient):
  Tree structure:
        [ROOT]
       /   |   \
      A    E    F
     / \   |
    B   G  H
   /
  C
  |
  D

  Forward pass: compute attention for ALL nodes at once
  Attention mask ensures C only attends to B, B only to A, A only to ROOT
  After forward pass:
    Branch A-B-C-D: accept A, reject B → discard C, D
    Branch A-G:     accept A, accept G → keep G
    Branch E-H:     accept E, accept H → keep H
    Branch F:       accept F → keep F
  Result: keep the longest valid prefix from each branch
```

**Key techniques:**
- **Tree-structured attention mask:** a position can only attend to its ancestors in the tree, not to siblings or unrelated branches
- **Parallel verification:** all nodes in the tree are processed in one forward pass, regardless of depth or branching factor
- **Branch-wise acceptance:** each path is checked independently; acceptance on one branch does not affect others
- **Optimal tree construction:** the best tree balances breadth (many branches) and depth (long chains) based on draft confidence

**Why this matters:**
- Linear verification wastes compute on tokens that get discarded because an earlier token was rejected
- Tree attention verifies exponentially more hypotheses per forward pass
- A tree with 4 branches of depth 3 verifies 12 tokens in one pass vs. 4 tokens in linear mode
- Critical for Medusa and advanced EAGLE variants where multiple draft paths exist naturally

---

### Real-Life Analogy

Imagine proofreading a choose-your-own-adventure book.
- **Linear verification:** You read page 1, then page 2, then page 3. If page 2 has a typo, you throw away the entire book and start over. But page 3 might have been correct. You never know because you discarded it along with page 2. You can only verify one path at a time.
- **Tree verification:** You lay out all possible story branches on a large table. Page 1 is in the center. From it, three branches lead to pages 2A, 2B, and 2C. From 2A, two branches lead to 3A and 3B. You read all pages simultaneously, checking each branch independently. If 2A has a typo, you mark that branch dead but keep reading 2B and 2C. At the end, you know exactly which paths are clean and can publish the longest valid ones.
- **The trade-off:** Laying out the entire tree takes more table space (memory) than a single linear path. But the time saved is enormous because you only read page 1 once, not once per branch. For a thick book with many branches, tree proofreading is the only practical approach.

---

### Tiny Numeric Example

**Linear chain verification (4 tokens):**
```
Draft: ["The", "cat", "sat", "down"]

Forward pass 1: verify "The"
  Target prob: 0.90, Draft prob: 0.85
  Acceptance threshold: min(1, 0.90/0.85) = 1.0
  Result: ACCEPTED

Forward pass 2: verify "cat" (given "The")
  Target prob: 0.70, Draft prob: 0.60
  Acceptance threshold: min(1, 0.70/0.60) = 1.0
  Result: ACCEPTED

Forward pass 3: verify "sat" (given "The cat")
  Target prob: 0.40, Draft prob: 0.65
  Acceptance threshold: min(1, 0.40/0.65) = 0.62
  Roll u=0.75: 0.75 > 0.62
  Result: REJECTED
  
Tokens accepted: 2 ("The", "cat")
Forward passes used: 3
Effective tokens per pass: 0.67
```

**Tree verification (same 4 tokens with 2 branches):**
```
Tree:
  Root
   ├── "The" (branch 1)
   │    ├── "cat"
   │    │    ├── "sat"
   │    │    └── "jumped"
   │    └── "dog"
   │         └── "ran"
   └── "A" (branch 2)
        └── "bird"
             └── "flew"

Single forward pass computes probabilities for ALL nodes.
Attention mask ensures "sat" only sees "cat" and "The",
"jumped" only sees "cat" and "The", etc.

Verification results:
  Branch 1a (The-cat-sat):    accept "The", accept "cat", reject "sat"
  Branch 1b (The-cat-jumped): accept "The", accept "cat", accept "jumped"
  Branch 1c (The-dog-ran):    accept "The", reject "dog"
  Branch 2 (A-bird-flew):     reject "A"

Longest valid paths kept: "The cat jumped" (3 tokens)
Forward passes used: 1
Effective tokens per pass: 3.0 (vs. 0.67 in linear mode)
```

---

### Common Confusion

1. **"Tree attention means the model generates a tree of text."** No. The output is still a single linear sequence of tokens. The tree is only an internal structure used during verification to explore multiple draft hypotheses in parallel.

2. **"Tree attention breaks causal masking."** No. Causal masking is preserved perfectly. Each node can only attend to its ancestors in the tree. The difference from linear attention is that siblings cannot attend to each other, which is exactly what we want.

3. **"Any rejected node invalidates its entire subtree."** Yes, that is correct and by design. If "cat" is rejected, then "sat" (which depends on "cat") is also invalid, even if the target model might have generated "sat" after some other token. This preserves the exact output distribution of autoregressive sampling.

4. **"Tree attention is slower than linear attention."** The single forward pass of tree attention is slightly slower than a single linear forward pass because the sequence is longer. But it replaces multiple linear forward passes, so the total time is dramatically lower.

5. **"The optimal tree is always a complete binary tree."** No. The optimal structure depends on the draft model's confidence distribution. If the draft is very confident about the first token but uncertain about later ones, a deep narrow tree is better. If confidence is uniform, a broad shallow tree wins.

6. **"Tree attention only works with Medusa."** Tree attention is a general verification technique. It can be used with any speculative decoding system: classical draft models, EAGLE, or Medusa. Medusa simply makes the tree structure natural because each head proposes a different branch.

7. **"Tree attention increases memory usage quadratically."** The attention matrix does grow with the number of nodes, but modern implementations use sparse attention or block-diagonal masks to keep memory linear in the number of branches. The key insight is that nodes in different branches do not attend to each other.

---

### Where It Is Used in Our Code

`src/phase119/phase119_speculative_concepts.py` — We construct a token tree with multiple branches and verify all paths in a single simulated forward pass. We compute acceptance probabilities along each branch, keep the longest valid prefix, and compare the expected tokens per forward pass against linear speculative decoding.

`src/phase119/phase119_speculative_colab.py` — We demonstrate tree verification using real LLaMA models by drafting multiple token candidates and verifying them in one batched forward pass. We measure the speedup from parallel verification and show that the output distribution matches standard greedy decoding exactly.
