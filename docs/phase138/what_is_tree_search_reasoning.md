## What Is Tree Search Reasoning?

---

### The Problem

A language model answering a complex math problem generates text one token at a time, left to right. If it makes a mistake in step 3 of a 10-step proof, it cannot go back. The error propagates, and the final answer is wrong. Human mathematicians do not work this way. They sketch multiple approaches, backtrack when a lemma fails, and explore branches selectively. How do you make a language model reason like a tree instead of a line?

---

### Definition

**Tree search reasoning** is the construction of a search tree where each node represents a partial reasoning step, and edges represent transitions to the next step. The model explores multiple reasoning paths simultaneously, evaluates the quality of partial solutions, and prunes branches that are unlikely to lead to a correct final answer. It turns linear chain-of-thought into a branching, backtracking, evaluative process.

**How it works:**
```
Problem: "A train travels 60 km/h for 2 hours, then 40 km/h for 3 hours. Total distance?"

Linear chain-of-thought:
  "60 * 2 = 120. Then 40 * 3 = 120. Then 120 + 120 = 240. Answer: 240 km."
  (One mistake anywhere ruins everything.)

Tree search reasoning:
  Root: "A train travels..."
  ├── Branch A: "First segment: 60 * 2 = 120 km"       (value: 0.9)
  │   ├── A1: "Second segment: 40 * 3 = 120 km"       (value: 0.9)
  │   │   └── A1a: "Total: 120 + 120 = 240 km"        (value: 1.0)  ← correct
  │   └── A2: "Second segment: 40 + 3 = 43 km"        (value: 0.1)  ← pruned
  └── Branch B: "First segment: 60 + 2 = 62 km"       (value: 0.1)  ← pruned early
```

**Key concepts:**
- **Partial solution node:** a reasoning chain that is not yet complete. It has a value estimate predicting the likelihood of eventual success.
- **Value function:** estimates the quality of a partial solution. It can be a trained model, a heuristic, or a process reward model.
- **Branching factor:** how many next steps are generated at each expansion. High branching gives better coverage but costs more compute.
- **Pruning:** removing low-value branches to focus compute on promising paths.

**Why this matters:**
- Complex reasoning is rarely linear. Tree search captures the exploratory nature of human problem-solving.
- It enables recovery from early mistakes. A bad first step does not doom the entire answer if other branches are explored.
- It provides an explicit structure for process supervision: each node can be evaluated, not just the final output.

---

### Real-Life Analogy

Solving a maze with a pen and paper.
- **Linear generation (greedy decoding):** You walk through the maze without looking ahead. At every intersection, you turn left. If that path leads to a dead end, you are stuck. You cannot backtrack because you already committed.
- **Best-of-N:** You make N photocopies of yourself. Each copy takes random turns. One copy might find the exit by luck. The other 49 walk into dead ends. You pick the winner, but you wasted 49 full walks.
- **Tree search reasoning:** You stand at the entrance with a map. At each intersection, you send scouts down 2-3 paths for a short distance. The scouts report back: "This path hits a wall in 10 meters," "This path looks promising." You invest your walking time in the promising path. You never complete a full dead-end walk.

---

### Tiny Numeric Example

**Problem:** "Find a path from (0,0) to (2,2) on a 3x3 grid. You can move up or right."

**Tree after 3 expansions (branching factor 2):**
```
Root: (0,0)  value=0.5
├── Child 1: (0,1)  value=0.6  (move up)
│   ├── Grandchild 1: (0,2)  value=0.7
│   └── Grandchild 2: (1,1)  value=0.8  ← promising
└── Child 2: (1,0)  value=0.6  (move right)
    ├── Grandchild 3: (1,1)  value=0.8
    └── Grandchild 4: (2,0)  value=0.4
```

**Value estimates:** Manhattan distance heuristic (closer to goal = higher value).
- (2,2) is the goal. (1,1) is 2 steps away → value 0.8. (2,0) is 2 steps away but only up moves left → value 0.4 (lower because of risk of boundary).

**Pruning:** After 3 expansions, we might prune (2,0) because its value is low and its branch looks unpromising. We invest more expansions in the (1,1) branches.

---

### Common Confusion

1. **"Tree search reasoning is just chain-of-thought with retries."** No. Chain-of-thought is a single linear path. Tree search maintains multiple parallel paths, evaluates them, and prunes. It is a structural difference, not just a repetition difference.

2. **"The value function must be a separate trained model."** Not necessarily. You can use heuristics (e.g., distance to goal), self-consistency (majority vote among rollouts), or even the LLM's own confidence scores. A trained value model is best but not required.

3. **"Tree search guarantees a correct answer."** No. It improves the probability of finding a correct answer by exploring more efficiently, but if the model's policy is systematically wrong, the tree will still fail. It is a search improvement, not a correctness guarantee.

4. **"Tree search is only for math and code."** It is easiest to apply where answers are verifiable, but the concept generalizes to any multi-step decision: planning a trip, writing a structured argument, designing a molecule. Any task with intermediate choices benefits from branching and backtracking.

5. **"A larger branching factor is always better."** Each expansion costs compute. A branching factor of 8 with 20 iterations explores 160 nodes. A branching factor of 2 with 20 iterations explores 40 nodes but can go deeper. The optimal branching factor depends on the problem depth and the quality of the value function.

6. **"Tree search replaces the need for a strong base model."** No. A weak base model produces weak nodes. Tree search amplifies a model's capability by using compute more efficiently, but it cannot fix fundamental misunderstandings. A model that does not know the order of operations will not magically learn it through tree search.

7. **"The tree must be built breadth-first."** MCTS builds the tree selectively, not level by level. It might explore one branch to depth 5 while another branch is still at depth 1, depending on value estimates. This selective depth is a feature, not a bug.

---

### Where It Is Used in Our Code

`src/phase138/phase138_mcts_concepts.py` — We build a toy search tree for a grid-path problem. Each node stores a partial path and a value estimate. We expand high-value nodes, prune low-value branches, and visualize how the tree grows unevenly, with deeper exploration in promising regions.

`src/phase138/phase138_mcts_colab.py` — We construct a reasoning tree for GSM8K math problems using Qwen2.5-3B. Each node is a partial reasoning chain. We use a correctness checker as a weak value function and show how tree search finds correct answers more efficiently than linear greedy decoding.
