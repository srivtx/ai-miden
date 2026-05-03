# DSA Learning Roadmap: Prerequisites & Dependencies

> **How to use this:** Start at Pattern 01. Master it before moving to Patterns 02 or 05. Follow the arrows. Do not skip prerequisites.

---

## Visual Roadmap

```
START HERE
    |
    v
PATTERN 01: Arrays & Hashing (Foundation of ALL)
    |
    +---> PATTERN 02: Two Pointers
    |         |
    |         +---> PATTERN 05: Sliding Window
    |         |         |
    |         |         +---> PATTERN 06: Linked List (optional after 02)
    |         |
    |         +---> PATTERN 06: Linked List
    |
    +---> PATTERN 03: Stack
    |         |
    |         +---> PATTERN 07: Trees (DFS uses stack)
    |         |         |
    |         |         +---> PATTERN 10: Tries (tree structure)
    |         |         |
    |         |         +---> PATTERN 11: Graphs (tree is graph)
    |         |
    |         +---> PATTERN 08: Heap
    |
    +---> PATTERN 04: Binary Search
    |         |
    |         +---> PATTERN 08: Heap (median finding)
    |         |
    |         +---> PATTERN 12: Advanced Graphs (Dijkstra uses heap + binary search concepts)
    |         |
    |         +---> PATTERN 17: Math & Geometry (coordinate BS)
    |
    +---> PATTERN 06: Linked List (can start after 01)
          |
          +---> PATTERN 07: Trees (similar pointer manipulation)

PATTERN 07: Trees
    |
    +---> PATTERN 09: Backtracking (DFS is backtracking)
    |         |
    |         +---> PATTERN 10: Tries (word search II uses both)
    |
    +---> PATTERN 10: Tries
    |         |
    |         +---> PATTERN 11: Graphs (word ladder)
    |
    +---> PATTERN 11: Graphs
          |
          +---> PATTERN 12: Advanced Graphs

PATTERN 05: Sliding Window
    |
    +---> PATTERN 13: 1-D DP (window problems often need DP optimization)

PATTERN 04: Binary Search
    |
    +---> PATTERN 14: 2-D DP (answer-space search)

PATTERN 11: Graphs
    |
    +---> PATTERN 12: Advanced Graphs

PATTERN 08: Heap
    |
    +---> PATTERN 12: Advanced Graphs (Dijkstra, Prim's)

PATTERN 09: Backtracking
    |
    +---> PATTERN 13: 1-D DP (memoization is DP)
    |
    +---> PATTERN 14: 2-D DP (interval DP)

PATTERN 13: 1-D DP
    |
    +---> PATTERN 14: 2-D DP
    |         |
    |         +---> PATTERN 15: Greedy (some DP problems have greedy alternatives)

PATTERN 15: Greedy
    |
    +---> PATTERN 16: Intervals (scheduling is greedy)
    |
    +---> PATTERN 08: Heap (scheduling with heap)

PATTERN 16: Intervals
    |
    +---> PATTERN 12: Advanced Graphs (MST is interval-like)

PATTERN 17: Math & Geometry
    |
    +---> PATTERN 18: Bit Manipulation
          |
          +---> PATTERN 10: Tries (XOR trie is advanced)
```

---

## Learning Paths

### Path A: The Classic Route (Recommended for Beginners)
**Duration:** 8-12 weeks

| Week | Patterns | Focus |
|---|---|---|
| 1 | 01 Arrays & Hashing | Master O(1) lookup, frequency, complement |
| 2 | 02 Two Pointers | Converging, same-direction, partitioning |
| 3 | 03 Stack + 04 Binary Search | LIFO, monotonic stack, divide search space |
| 4 | 05 Sliding Window | Fixed, variable, min window |
| 5 | 06 Linked List + 07 Trees | Pointer manipulation, traversals |
| 6 | 08 Heap + 09 Backtracking | Priority queue, DFS decision trees |
| 7 | 10 Tries + 11 Graphs | Prefix trees, BFS/DFS |
| 8 | 12 Advanced Graphs | Dijkstra, Union-Find, MST |
| 9 | 13 1-D DP | Linear choice, climbing, stock, LIS |
| 10 | 14 2-D DP | Grid, edit distance, knapsack |
| 11 | 15 Greedy + 16 Intervals | Local optimal, scheduling |
| 12 | 17 Math + 18 Bit | Number theory, bit tricks |

### Path B: The Interview-Focused Route (2-4 weeks)
**For people with upcoming interviews.**

**Week 1-2: The Big 6 (80% of interviews)**
- 01 Arrays & Hashing
- 02 Two Pointers
- 03 Stack
- 04 Binary Search
- 05 Sliding Window
- 07 Trees

**Week 3: The Next 4 (15% of interviews)**
- 06 Linked List
- 08 Heap
- 09 Backtracking
- 11 Graphs

**Week 4: The Specialist 4 (5% of interviews, but distinguishes you)**
- 10 Tries
- 13 1-D DP
- 14 2-D DP
- 15 Greedy

### Path C: The Topic-Deep Route
Pick one pattern per week and master ALL its problems.

---

## Pattern Blending: What Connects to What

### Pattern 01 blends with EVERYTHING
- 01 + 02: Two-sum in sorted array (set vs pointers)
- 01 + 05: Longest substring with K distinct (hash map + window)
- 01 + 07: Path sum III (hash map + tree DFS)
- 01 + 11: Clone graph (hash map + BFS)

### Pattern 02 blends with 05
- Sliding window IS two pointers with a condition
- If you master 02, 05 is a natural extension

### Pattern 03 blends with 07
- Iterative tree traversals use stack
- DFS is just stack-based graph traversal

### Pattern 04 blends with 08
- Kth smallest/largest often uses heap or binary search
- Answer-space search is binary search on value domain

### Pattern 07 blends with 09
- Tree path problems → backtracking
- N-ary tree permutations → backtracking

### Pattern 09 blends with 13
- Backtracking with memoization = top-down DP
- If you can write backtracking, you can write DP

### Pattern 11 blends with 12
- Graphs → shortest path → Dijkstra
- Connected components → Union-Find

### Pattern 13 blends with 14
- 1D: linear recurrence
- 2D: grid recurrence
- Same logic, one more dimension

### Pattern 15 blends with 16
- Greedy interval scheduling
- Intervals + heap = meeting rooms II

### Pattern 17 blends with 18
- Number theory + bit manipulation
- Prime checking with bit masks

---

## The Gate System

Before advancing to the next pattern, pass ALL gates for the current pattern:

### Gate 1: Recognition (10 minutes)
Given 5 problem statements, identify the correct archetype without solving.
Example: "Find two numbers that add up to target" → "Archetype 1.3: Complement Lookup"

### Gate 2: Template Recall (20 minutes)
Write the core template from memory.
Example: Write the hash set existence template in under 2 minutes.

### Gate 3: Variation Adaptation (30 minutes)
Given a variation problem, adapt the template.
Example: "Two Sum with duplicates allowed" → adjust check-before-insert order.

### Gate 4: Mixed Identification (15 minutes)
Given 5 problems from DIFFERENT patterns, identify each correctly.
This tests whether you confuse similar-looking patterns.

### Gate 5: Pattern Blend (45 minutes)
Solve a problem that uses TWO patterns.
Example: Top K Frequent Elements (heap + hash map)

**Only after passing all 5 gates should you move to the next pattern.**

---

## Critical Path: Minimum for Interviews

If you only have time for 60% of the content, do this order:

1. **01 Arrays & Hashing** (non-negotiable foundation)
2. **02 Two Pointers** (very common)
3. **04 Binary Search** (common, easy to mess up)
4. **05 Sliding Window** (very common)
5. **07 Trees** (extremely common)
6. **03 Stack** (common, distinct pattern)
7. **06 Linked List** (common but smaller problem set)
8. **11 Graphs** (common, BFS/DFS essential)
9. **13 1-D DP** (distinguishes mid-level from junior)
10. **08 Heap** (medium frequency, easy to learn)

**Skip initially (learn only if time permits):**
- 09 Backtracking (lower frequency, harder)
- 10 Tries (specialized)
- 12 Advanced Graphs (rare in standard interviews)
- 14 2-D DP (harder, less frequent)
- 15 Greedy (often simple once you see it)
- 16 Intervals (subset of greedy)
- 17 Math (can be tricky, often avoidable)
- 18 Bit Manipulation (specialized, some companies love it)

---

## Pattern Confusion Matrix

Problems that LOOK like one pattern but are actually another:

| Problem Looks Like | Actually Is | Why |
|---|---|---|
| Two Sum (unsorted) | Arrays & Hashing | Need hash map, not two pointers |
| Subarray Sum Equals K | Sliding Window | Needs prefix sums + hash map (not window) |
| Maximum Subarray | Sliding Window | Needs Kadane's DP, not window |
| Word Search | Backtracking | Single word = DFS. Multiple words = Trie + DFS |
| Valid Parentheses | Stack | Yes, but "generate parentheses" is backtracking |
| Kth Largest | Heap | Can also be solved with quickselect |
| Word Break | Backtracking | Actually 1D DP (boolean) |
| Jump Game | DP | Actually greedy (track max reach) |
| Longest Increasing Subsequence | DP | Can be O(n log n) with binary search |
| Merge Intervals | Intervals | Actually just sort + iterate (barely a pattern) |

**Study this matrix.** These are the most common misidentifications in interviews.

---

## Next Steps

1. Read `docs_dsa/README.md` for study phases
2. Read `docs_dsa/BLENDED_DRILLS.md` for mixed pattern practice
3. Read `docs_dsa/NEETCODE_150.md` for the curated problem list
4. Read `docs_dsa/PROGRESS_TRACKER.md` to track your progress

---

*Start with Pattern 01. Do not skip ahead.*
