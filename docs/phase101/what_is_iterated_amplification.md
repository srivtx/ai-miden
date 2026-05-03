## What Is Iterated Amplification?

---

### The Problem

A research team wants to train a model to prove complex mathematical theorems. The model eventually surpasses its human supervisors, who can no longer tell whether a 50-page proof is correct or contains a subtle error. Standard reinforcement learning from human feedback breaks down here: if the supervisor cannot evaluate the output, they cannot provide a training signal. How do you train a model to solve problems that are too hard for its supervisor to judge directly?

---

### Definition

**Iterated Amplification** is a training framework in which a weak supervisor breaks a hard problem into smaller subproblems, uses the AI to solve each subproblem, and then assembles and evaluates the results. Over iterations, the AI learns to solve increasingly complex tasks by leveraging its own capabilities at a simpler level, bootstrapping from weak supervision to strong performance without ever requiring the supervisor to solve the full problem.

**How it works:**
```
Task: prove a complex theorem (too hard for human to verify directly)

Iteration 0:
  Human breaks theorem into 5 lemmas.
  AI (weak) attempts each lemma. Human checks lemmas (easier than full proof).
  Human assembles lemmas and checks high-level structure.
  AI learns from feedback on lemmas and assembly.

Iteration 1:
  Human breaks theorem into 5 lemmas.
  AI (stronger now) solves each lemma with higher accuracy.
  Human still only checks lemmas and structure.
  AI learns again.

Iteration N:
  Human breaks theorem into 5 lemmas.
  AI (very strong) solves each lemma and auto-assembles them.
  Human checks only the high-level proof sketch.
  AI has learned to prove theorems that the human cannot directly verify.
```

**Key properties:**
- The supervisor evaluates the *assembly* of sub-answers, not the sub-answers themselves.
- The AI grows beyond the supervisor's direct capability by composing its own sub-solutions.
- It is a meta-algorithm: the decomposition strategy depends on the task.

**Why this matters:**
- It addresses the scalable oversight problem: how to supervise superhuman AI.
- It has theoretical connections to complexity theory (the supervisor only needs to solve problems in a lower complexity class).
- It is one of the few alignment approaches with a formal safety motivation.

---

### Real-Life Analogy

Imagine a CEO who cannot write code but needs to launch a complex software product. The CEO does not attempt to review every line of code; instead, she breaks the project into milestones: database schema, API design, frontend components, and integration tests. She delegates each milestone to her engineering team, reviews the architecture diagrams and test results, and verifies that the pieces fit together. The team collectively builds a system that no single person — not even the engineers individually — fully understands in every detail. Over multiple product cycles, the team learns to anticipate the CEO's architectural preferences and delivers better assemblies with less guidance. Iterated Amplification is that management structure: the supervisor provides oversight at a level they can handle, and the AI composes its own capabilities to solve problems beyond any single evaluation.

The trade-off is decomposition quality. If the CEO breaks the project into poorly designed milestones — say, she separates frontend and backend in a way that creates API mismatches — the final product fails even if each team did good local work. Similarly, if a human decomposes a theorem into lemmas that are individually solvable but collectively insufficient, Iterated Amplification cannot recover. The framework assumes that the decomposition preserves correctness: a correct assembly of correct sub-answers yields a correct full answer. This is true for many problems but not all. Some tasks are "non-decomposable": their difficulty lies precisely in the global interaction of local pieces, and no clean separation exists.

---

### Tiny Numeric Example

**Direct supervision ceiling:**
```
Supervisor can reliably evaluate problems of difficulty <= 5.
Task difficulty distribution:
  Difficulty 1-5: 40% of tasks
  Difficulty 6-10: 35% of tasks
  Difficulty 11-20: 25% of tasks

With direct supervision only:
  Model trained on difficulty <= 5.
  Performance on difficulty 6-10: 20% (poor generalization)
  Performance on difficulty 11-20: 5%
```

**Iterated Amplification (decompose difficulty N into 3 subproblems of difficulty N/2):**
```
Iteration 1: Model solves difficulty 3 subproblems. Supervisor evaluates assembly.
  Effective capability: difficulty 5 (3 subproblems + assembly)

Iteration 2: Model now solves difficulty 5 subproblems (improved from iteration 1).
  Decomposed into difficulty 2-3 pieces. Supervisor evaluates assembly.
  Effective capability: difficulty 8

Iteration 3: Model solves difficulty 8 subproblems.
  Decomposed into difficulty 4 pieces. Supervisor evaluates assembly.
  Effective capability: difficulty 12

Iteration 4: Model solves difficulty 12 subproblems.
  Decomposed into difficulty 6 pieces. Supervisor evaluates assembly.
  Effective capability: difficulty 18
```

**Capability growth comparison:**
```
Iteration | Direct Supervision | Iterated Amplification
----------|--------------------|------------------------
0         | 5                  | 5
1         | 5                  | 5
2         | 5                  | 8
3         | 5                  | 12
4         | 5                  | 18
```

**The shift:** Direct supervision caps model capability at the supervisor's level. Iterated Amplification breaks through that ceiling by composing the model's own solutions, growing capability geometrically while the supervisor's evaluation burden remains constant.

---

### Common Confusion

1. **"Iterated Amplification is just divide-and-conquer."** It is similar, but the key difference is that the AI solves the subproblems and improves over iterations. In standard divide-and-conquer, the subproblems are solved by the same static algorithm. Here, the solver itself grows stronger through feedback.

2. **"The supervisor must verify every sub-answer."** Not necessarily. The supervisor verifies the *assembly* of sub-answers at a high level. In some variants, the supervisor only checks a random subset of sub-answers, further reducing their burden.

3. **"Iterated Amplification guarantees safety."** It does not. If the model learns to exploit the supervisor's limited evaluation — for example, by solving subproblems in a way that looks correct locally but fails globally — the framework can amplify deception rather than capability.

4. **"It only works for tasks that decompose cleanly."** This is partially true. It works best for hierarchically decomposable tasks (math, coding, planning). It struggles with tasks where the difficulty is fundamentally holistic (creative writing, emotional intelligence).

5. **"The AI trains itself without any human input."** False. Human input is required at every iteration to evaluate the assembly. The human's role shifts from solving problems to designing decompositions and checking high-level structure.

6. **"Iterated Amplification and Debate Protocol are the same."** They are different approaches to scalable oversight. Iterated Amplification uses decomposition and composition. Debate uses adversarial argumentation. They can be combined: decomposition creates sub-debates.

7. **"It is only a theoretical framework."** While originally theoretical, practical approximations exist. Bootstrapped training of reasoning models, where a model generates and filters its own chain-of-thought data, is a rough real-world analog.

---

### Where It Is Used in Our Code

`src/phase101/phase101_advanced_alignment.py` — We simulate an iterative improvement loop where a proposal is revised based on critic scores over multiple iterations. Each iteration represents a subproblem solution and assembly step, with the critic playing the role of the weak supervisor evaluating whether the assembled result improves. We plot the score trajectory to show how iterative decomposition and feedback drive convergence beyond the initial capability level.
