# DSA Mastery System: The Complete Plan

> **Scope:** 250+ NeetCode problems, but organized by ~108 problem archetypes.
> **Method:** For each archetype, we drill 5-7 variations until recognition is automatic.
> **Goal:** See any problem → 10 seconds → know the exact archetype → write the template.

---

## The Philosophy: Archetypes, Not Problems

Memorizing 250 solutions is impossible. But there are only ~108 core **problem archetypes** across all of DSA. 

An archetype is a problem structure that stays the same even when the story changes.

**Example Archetype: "Hash Map Complement Lookup"**
- Canonical: Two Sum (find pair that adds to target)
- Variation 1: Two Sum II (sorted array → two pointers instead)
- Variation 2: 3Sum (find triplets → fix one, two-sum the rest)
- Variation 3: 4Sum (same pattern, more loops)
- Variation 4: Two Sum with duplicates allowed
- Variation 5: Count pairs with sum < target
- Near Miss: Subarray Sum Equals K (looks like pair sum, but uses prefix sums)

Once you see 6 variations of the same archetype, the 7th problem feels obvious.

---

## The Math

| Level | Count | Examples |
|---|---|---|
| **Patterns** | 18 | Arrays & Hashing, Two Pointers, etc. |
| **Archetypes per Pattern** | 4-8 | ~6 average |
| **Total Archetypes** | ~108 | The complete vocabulary of DSA problems |
| **Variations per Archetype** | 5-7 | Canonical + twists |
| **Total Problem Exposures** | ~540 | More than enough for mastery |
| **NeetCode Problems Mapped** | 250+ | Every problem maps to an archetype |

**Key insight:** You don't need to solve 250 unique problems. You need to solve ~108 archetypes deeply, with multiple variations each. The 250 NeetCode problems are just variations of these archetypes.

---

## The Structure Per Archetype

For every archetype, we build a "Recognition Module":

```
ARCHETYPE: [Name]
├── RECOGNITION SIGNAL (10-second identification)
│   └── "When you see these words, think this archetype"
├── CORE STRUCTURE (the invariant)
│   └── What stays the same across all variations
├── CANONICAL PROBLEM (the purest form)
│   └── Full solution with intuition
├── VARIATION FAMILY (5-7 twists)
│   ├── V1: Constraint change
│   ├── V2: Data structure change
│   ├── V3: Multi-pattern blend
│   ├── V4: Reverse the question
│   ├── V5: Optimization pressure
│   └── V6: Near miss (different archetype, similar look)
├── TEMPLATE (skeleton code)
├── TRAPS (how interviewers trick you)
└── PREDICTION DRILL (new problem → which archetype?)
```

---

## The 18 Patterns → Archetypes Map

### Pattern 01: Arrays & Hashing (8 archetypes)
1. **Existence Checking** — Set membership, duplicates
2. **Frequency Counting** — Character/word counts, anagrams
3. **Complement Lookup** — Two-sum family, pair problems
4. **Grouping by Signature** — Anagram groups, categorize by property
5. **Prefix Aggregate** — Running sums, products, XOR
6. **Hash Map Design** — Custom data structures with O(1) ops
7. **Constraint Satisfaction** — Valid Sudoku, checking rules
8. **Sequence Building** — Longest consecutive, union-find lite

### Pattern 02: Two Pointers (7 archetypes)
1. **Converging Pointers** — Pair sum in sorted array
2. **Same-Direction Pointers** — Remove duplicates, move zeros
3. **Partitioning** — Dutch national flag, quicksort partition
4. **Palindrome Check** — Valid palindrome, palindrome substrings
5. **Container/Area** — Container with most water, trapping rain
6. **Merge Sorted** — Merge two arrays, merge K lists
7. **Sliding Window Variant** — Fixed-size window with two pointers

### Pattern 03: Stack (6 archetypes)
1. **Matching/Validation** — Valid parentheses
2. **Monotonic Stack (Next Greater)** — Daily temperatures, stock span
3. **Expression Evaluation** — Reverse Polish notation, calculator
4. **History/Undo** — Browser history, text editor
5. **DFS Simulation** — Tree iteration without recursion
6. **String Processing** — Decode string, simplify path

### Pattern 04: Binary Search (8 archetypes)
1. **Classic Search** — Find element in sorted array
2. **Search Space Reduction** — Find minimum in rotated array
3. **Boundary Detection** — First/last occurrence, insert position
4. **Condition-Based Search** — Peak element, find in mountain
5. **2D Matrix Search** — Search 2D matrix I & II
6. **Answer Space Search** — Koko eating bananas, ship packages
7. **Advanced: Exponential Search** — Search in infinite array
8. **Multi-Array Search** — Find median of two sorted arrays

### Pattern 05: Sliding Window (7 archetypes)
1. **Fixed-Size Window** — Max sum subarray of size K
2. **Variable-Size Window (At Most K)** — Longest substring with K distinct
3. **Variable-Size Window (At Least K)** — Minimum window substring
4. **Window with Hash Map** — Anagram in string, permutation
5. **Two-Window Comparison** — Longest repeating character replacement
6. **Count-Based Window** — Fruit into baskets, max consecutive ones III
7. **Multi-Condition Window** — Subarrays with K different integers

### Pattern 06: Linked List (8 archetypes)
1. **Traversal & Modification** — Reverse linked list
2. **Fast & Slow Pointers** — Detect cycle, find middle
3. **Merge Operations** — Merge two sorted lists
4. **Reordering** — Reorder list, odd-even list
5. **Multi-List Operations** — Add two numbers, merge K lists
6. **Cycle & Intersection** — Cycle start, intersection node
7. **Copy/Deep Copy** — Copy list with random pointer
8. **Partition & Sort** — Partition list, insertion sort list

### Pattern 07: Trees (10 archetypes)
1. **Basic Traversals** — DFS (in/pre/post), BFS level-order
2. **Path Problems** — Root-to-leaf sum, binary tree paths
3. **Validation** — Validate BST, balanced tree, symmetric
4. **LCA Problems** — Lowest common ancestor family
5. **View/Boundary** — Right/left view, boundary traversal
6. **Serialization** — Serialize/deserialize, construct from traversal
7. **Modification** — Invert tree, flatten to linked list
8. **Counting/Metrics** — Diameter, max path sum, count nodes
9. **Advanced: Morris Traversal** — O(1) space traversal
10. **N-ary Trees** — N-ary traversal, max depth

### Pattern 08: Heap (6 archetypes)
1. **Top K Elements** — K largest, K closest to origin
2. **Merge K Sorted** — Merge K lists/arrays
3. **Scheduling/Intervals** — Meeting rooms II, task scheduler
4. **Median Finder** — Running median, sliding window median
5. **Frequency-Based** — Top K frequent, reorganize string
6. **Two-Heap Technique** — Find median from data stream

### Pattern 09: Backtracking (8 archetypes)
1. **Subsets** — All subsets, subsets with duplicates
2. **Permutations** — All permutations, permutations II
3. **Combinations** — Combination sum I/II/III, combinations
4. **N-Queens** — N-queens, N-queens II
5. **Grid/Path Exploration** — Word search, unique paths III
6. **Expression Building** — Expression add operators, different ways to add parentheses
7. **Graph Coloring** — Sudoku solver, graph coloring
8. **Pruning Optimization** — Palindrome partitioning, word break II

### Pattern 10: Tries (4 archetypes)
1. **Prefix Search** — Implement Trie, prefix tree
2. **Word Search** — Word search II, add and search word
3. **Autocomplete** — Design search autocomplete system
4. **XOR Optimization** — Maximum XOR of two numbers

### Pattern 11: Graphs (10 archetypes)
1. **BFS Traversal** — Level order, shortest path unweighted
2. **DFS Traversal** — Connected components, find path
3. **Cycle Detection** — Course schedule, detect cycle
4. **Topological Sort** — Course schedule II, alien dictionary
5. **Bipartite Check** — Is graph bipartite, possible bipartition
6. **Connected Components** — Number of islands, friend circles
7. **Clone/Copy** — Clone graph
8. **Word Ladder** — Word ladder I/II (BFS + DFS)
9. **Pacific Atlantic** — Multi-source BFS/DFS
10. **Reconstruction** — Reconstruct itinerary

### Pattern 12: Advanced Graphs (7 archetypes)
1. **Dijkstra (Shortest Path)** — Network delay time, cheapest flights
2. **Bellman-Ford** — Cheapest flights within K stops
3. **Floyd-Warshall** — Find city with smallest number of neighbors
4. **Prim/Kruskal (MST)** — Min cost to connect all points
5. **Union-Find** — Number of provinces, redundant connection
6. **Tarjan (SCC/Bridges)** — Critical connections
7. **Advanced: A* Search** — concepts (not in NeetCode but useful)

### Pattern 13: 1-D DP (9 archetypes)
1. **Linear Choice** — House robber, max subarray
2. **Climbing/Jump** — Climbing stairs, jump game
3. **Partition/Cut** — Palindrome partitioning II, word break
4. **Decoding/Translation** — Decode ways
5. **Stock Problems** — Best time to buy/sell stock family
6. **Counting Ways** — Domino tromino tiling
7. **Delete/Insert** — Longest increasing subsequence
8. **State Machine** — Best time to buy/sell with cooldown
9. **Digit DP** — Numbers with repeated digits (advanced)

### Pattern 14: 2-D DP (8 archetypes)
1. **Grid Path** — Unique paths, min path sum
2. **Edit Distance** — Edit distance, delete operation
3. **LCS Variations** — Longest common subsequence, uncrossed lines
4. **Knapsack (0/1)** — Partition equal subset, target sum
5. **Knapsack (Unbounded)** — Coin change, combination sum IV
6. **Interval DP** — Burst balloons, strange printer
7. **String Matching** — Regular expression matching, wildcard
8. **Matrix Chain** — Minimum cost tree from leaf values

### Pattern 15: Greedy (7 archetypes)
1. **Interval Scheduling** — Non-overlapping intervals, meeting rooms
2. **Jump Game** — Jump game II, can reach end
3. **Partition/Rearrange** — Partition labels, reorganize string
4. **Queue/Line Problems** — Queue reconstruction, candy distribution
5. **String Greedy** — Remove K digits, monotone increasing digits
6. **Two-Choice Greedy** — Best time to buy/sell stock II
7. **Advanced: Huffman** — Optimal merge pattern concepts

### Pattern 16: Intervals (5 archetypes)
1. **Merge Overlapping** — Merge intervals
2. **Insert & Merge** — Insert interval
3. **Meeting Room Problems** — Meeting rooms I & II
4. **Interval Intersection** — Interval list intersections
5. **Minimum Interval Queries** — Find right interval

### Pattern 17: Math & Geometry (8 archetypes)
1. **Prime & Factors** — Count primes, ugly number
2. **GCD/LCM** — Fraction to recurring decimal
3. **Power/Modulo** — Pow(x,n), super pow
4. **Coordinate Geometry** — Max points on a line, rectangle area
5. **Matrix Operations** — Spiral order, rotate image, set zeroes
6. **Randomized** — Shuffle array, random pick with weight
7. **Simulation** — Fraction addition, multiply strings
8. **Game Theory** — Nim game, can I win

### Pattern 18: Bit Manipulation (7 archetypes)
1. **Single Number** — Single number I/II/III
2. **Power of Two** — Power of two, count bits
3. **XOR Properties** — Missing number, find duplicate
4. **Bit Masking** — Subsets, max product of word lengths
5. **Bitwise Operations** — Reverse bits, number of 1 bits
6. **Bit DP** — Counting bits, concatenated binary
7. **Advanced: Bitwise Optimization** — Minimum XOR sum of two arrays

---

## How We Build This

**Phase 1: Pattern Docs (Weeks 1-6)**
- Build all 18 pattern docs with full archetype breakdown
- Each doc: ~30-50 pages of dense intuition
- Focus: Recognition signals, templates, variation families

**Phase 2: Problem Library (Weeks 7-12)**
- Create individual problem files for all 250+ NeetCode problems
- Each problem links to its archetype
- Include: problem statement, archetype identification, solution, similar problems

**Phase 3: Drill Sets (Weeks 13-16)**
- Mixed problem sets organized by archetype similarity
- "Solve these 5 problems — they are all the same archetype with different stories"
- Prediction exercises: given a new problem, identify the archetype

**Phase 4: Speed & Interview (Weeks 17+)**
- Timed archetype identification (10 seconds per problem)
- Mock interviews using the pattern language
- Blind 75 mixed sets

---

## The Recognition Test

After completing this system, you should be able to:

1. Read ANY LeetCode medium in 10 seconds and name the archetype
2. Write the template for that archetype in 30 seconds
3. Adapt the template to the specific problem in 2 minutes
4. Explain WHY this archetype fits and not another
5. Predict what variations the interviewer might ask next

---

## Next Step

Shall I start building Pattern 01 with all 8 archetypes and their variation families? Or do you want me to adjust this plan first?
