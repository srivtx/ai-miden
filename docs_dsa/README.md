# DSA Intuition Maps

> **Goal:** Not to memorize 250 solutions, but to build automatic pattern recognition so you see a problem and your brain immediately knows which archetype to use.
>
> **Philosophy:** Every problem is a variation of ~108 core archetypes across 18 patterns. Master the archetype, and 250 problems become obvious.
>
> **Read this first:** [MASTER_PLAN.md](MASTER_PLAN.md) — The complete architecture of the system.

---

## How This Works

Instead of solving problems one-by-one in isolation, we build **intuition maps**.

For every pattern:
1. **The Trigger** — What words in the problem statement make your brain scream "THIS PATTERN"?
2. **The Core Insight** — The ONE idea that unlocks every problem in this family.
3. **The Mental Model** — A picture or analogy that lives in your head forever.
4. **The Decision Tree** — "If they ask for X, the answer is always Y."
5. **The Template** — Skeleton code. You fill in the blanks.
6. **The Problem Family** — Problems ordered by difficulty, all drilling the same muscle.
7. **The Traps** — How interviewers twist the pattern to trick you.

---

## The 18 Patterns (NeetCode Order)

| # | Pattern | Core Muscle | When You See... |
|---|---|---|---|
| 01 | Arrays & Hashing | O(1) lookup trade-offs | "Find", "count", "duplicate", "unique", "frequency" |
| 02 | Two Pointers | Converging from both ends | "Sorted array", "pair with sum", "palindrome", "merge" |
| 03 | Stack | Last-in-first-out tracking | "Valid parentheses", "next greater", "history", "undo" |
| 04 | Binary Search | Divide search space in half | "Sorted", "find in O(log n)", "minimum/maximum where condition changes" |
| 05 | Sliding Window | Subarray/substring of variable size | "Subarray", "substring", "consecutive", "at most K" |
| 06 | Linked List | Pointer manipulation & traversal | "List", "reverse", "cycle", "merge sorted lists" |
| 07 | Trees | Recursion & hierarchical traversal | "Binary tree", "root-to-leaf", "level order", "LCA" |
| 08 | Heap / Priority Queue | Always access the extreme | "K largest/smallest", "merge K sorted", "scheduling" |
| 09 | Backtracking | Explore all possibilities with pruning | "All combinations", "permutations", "subsets", "sudoku", "N-queens" |
| 10 | Tries | Prefix-based storage & search | "Auto-complete", "prefix", "word search", "longest common prefix" |
| 11 | Graphs | BFS/DFS on relationships | "Network", "connected", "path", "shortest", "dependencies" |
| 12 | Advanced Graphs | Shortest path & spanning trees | "Minimum cost", "shortest path", "MST", "network delay" |
| 13 | 1-D DP | Optimal substructure on a line | "Maximize", "minimize", "ways to reach", "decision at each step" |
| 14 | 2-D DP | Optimal substructure on a grid or two sequences | "Grid path", "edit distance", "LCS", "knapsack" |
| 15 | Greedy | Local optimal leads to global optimal | "Minimum intervals", "maximum non-overlapping", "always pick cheapest" |
| 16 | Intervals | Merge, insert, or find gaps in ranges | "Overlapping", "schedule", "meeting rooms", "merge intervals" |
| 17 | Math & Geometry | Number theory & spatial reasoning | "GCD", "LCM", "prime", "area", "overlap", "matrix rotation" |
| 18 | Bit Manipulation | Operating at the bit level | "Single number", "power of two", "subset enumeration", "XOR" |

---

## Study Order

**Phase 1: Pattern Recognition (Weeks 1-3)**
- Read each pattern doc WITHOUT solving problems first.
- Focus on The Trigger and The Decision Tree.
- Quiz yourself: "Given this problem statement, which pattern?"

**Phase 2: Muscle Building (Weeks 4-8)**
- Solve the Problem Family for each pattern.
- Start with the easiest warm-up, end with the hardest twist.
- After each problem, ask: "What pattern muscle did I just flex?"

**Phase 3: Pattern Blending (Weeks 9-12)**
- Solve mixed problem sets.
- The first 30 seconds of every problem: identify the pattern.
- Speed matters more than perfection.

**Phase 4: Interview Simulation (Weeks 13+)**
- Timed solves.
- Talk out loud using the pattern language.
- If stuck for 2 minutes, re-read the trigger for that pattern.

---

## File Structure

```
docs_dsa/
├── README.md                  # This file
├── patterns/                  # Pattern intuition docs
│   ├── 01_arrays_and_hashing.md
│   ├── 02_two_pointers.md
│   └── ... (18 total)
├── problems/                  # Problem write-ups with pattern DNA
│   ├── 001_two_sum.md
│   ├── 217_contains_duplicate.md
│   └── ... (150 total, linked from pattern docs)
└── intuition_maps/            # Quick-reference cheat sheets
    ├── pattern_triggers.md    # One-page trigger guide
    └── time_space_cheat_sheet.md
```

---

## The Golden Rule

> If you solve a problem and cannot explain WHICH pattern it uses and WHY that pattern fits, you have memorized a solution, not built intuition.
>
> The goal is: read the problem → 10 seconds → "This is a sliding window with variable size and a hash map for character counts" → write the template.

---

*Start with Pattern 01: Arrays & Hashing.*
