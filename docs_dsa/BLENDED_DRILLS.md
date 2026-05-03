# Blended Pattern Drills

> **These problems require 2-3 patterns.** Solve them to build pattern identification muscle.
>
> **Instructions:** Cover the "Pattern Blend" column. Read the problem. Identify patterns. Then check.

---

## Blend 01: Arrays & Hashing + Two Pointers

### Problem: 3Sum Closest (LeetCode 16)
**Statement:** Find triplet sum closest to target.
**Pattern Blend:** 01 (sorting enables two pointers) + 02 (converging pointers)
**Why:** Sort the array (01 preprocessing), then use two pointers on the remaining array (02).

### Problem: Container With Most Water (LeetCode 11)
**Statement:** Max area container.
**Pattern Blend:** 01 (understand why move shorter) + 02 (converging pointers)
**Why:** Two pointers from ends. The insight is about why moving the shorter line is optimal.

---

## Blend 02: Arrays & Hashing + Heap

### Problem: Top K Frequent Elements (LeetCode 347)
**Statement:** K most frequent elements.
**Pattern Blend:** 01 (frequency counting) + 08 (top K extraction)
**Why:** Count with hash map. Extract top K with heap. Alternative: bucket sort.

### Problem: Find K Pairs with Smallest Sums (LeetCode 373)
**Statement:** K pairs from two sorted arrays.
**Pattern Blend:** 02 (sorted arrays) + 08 (merge K with heap)
**Why:** Think of it as merging K sorted lists where each list starts from a different index.

---

## Blend 03: Arrays & Hashing + Sliding Window

### Problem: Longest Substring Without Repeating Characters (LeetCode 3)
**Statement:** Longest unique substring.
**Pattern Blend:** 05 (window) + 01 (hash set for duplicates)
**Why:** Expand window. Use set to check if duplicate exists. Shrink from left if needed.

### Problem: Subarrays with K Different Integers (LeetCode 992)
**Statement:** Count subarrays with exactly K distinct.
**Pattern Blend:** 05 (window) + 01 (hash map for counts) + 13 (exactly K = at_most(K) - at_most(K-1))
**Why:** Three patterns in one. This is a true test of mastery.

---

## Blend 04: Stack + Trees

### Problem: Binary Tree Inorder Traversal (LeetCode 94) — Iterative
**Statement:** Inorder without recursion.
**Pattern Blend:** 07 (tree traversal) + 03 (stack simulates recursion)
**Why:** Recursive DFS uses implicit stack. Iterative version uses explicit stack.

### Problem: Flatten Binary Tree to Linked List (LeetCode 114)
**Statement:** Flatten tree to right-linked list in-place.
**Pattern Blend:** 07 (tree) + 03 (stack for Morris traversal) + 06 (linked list result)
**Why:** Can be done with stack, recursion, or Morris traversal (O(1) space).

---

## Blend 05: Heap + Trees

### Problem: Kth Smallest Element in a BST (LeetCode 230)
**Statement:** Kth smallest in BST.
**Pattern Blend:** 07 (tree) + 08 (heap / order statistic)
**Why:** Inorder traversal gives sorted order. Can also use quickselect on implicit array.

---

## Blend 06: Backtracking + Tries

### Problem: Word Search II (LeetCode 212)
**Statement:** Find all words in grid.
**Pattern Blend:** 10 (trie stores words) + 09 (DFS searches grid) + 11 (graph traversal)
**Why:** Build trie from word list. DFS from each cell. Prune matched words.

---

## Blend 07: Graphs + Heap

### Problem: Network Delay Time (LeetCode 743)
**Statement:** Time for all nodes to receive signal.
**Pattern Blend:** 11 (graph) + 12 (Dijkstra) + 08 (heap for shortest path)
**Why:** Dijkstra is BFS + priority queue. The heap gives the next closest node.

### Problem: Merge k Sorted Lists (LeetCode 23)
**Statement:** Merge k sorted linked lists.
**Pattern Blend:** 06 (linked list) + 08 (heap for merging) + 02 (merge 2 sorted)
**Why:** Extends merge-two-sorted to k lists using heap.

---

## Blend 08: DP + Binary Search

### Problem: Longest Increasing Subsequence (LeetCode 300)
**Statement:** Length of LIS.
**Pattern Blend:** 13 (1D DP recurrence) + 04 (binary search optimization)
**Why:** dp[i] = LIS ending at i. O(n^2). Or patience sorting with binary search: O(n log n).

### Problem: Split Array Largest Sum (LeetCode 410)
**Statement:** Split array into m subarrays, minimize largest sum.
**Pattern Blend:** 04 (binary search on answer) + 13 (DP verification)
**Why:** Binary search on possible max sum. Check if feasible with greedy/DP.

---

## Blend 09: Greedy + Intervals + Heap

### Problem: Meeting Rooms II (LeetCode 253)
**Statement:** Min conference rooms needed.
**Pattern Blend:** 16 (intervals) + 15 (greedy scheduling) + 08 (heap tracks end times)
**Why:** Sort by start. Min heap of end times. If next starts after earliest end, reuse room.

### Problem: Employee Free Time (LeetCode 759)
**Statement:** Find common free time.
**Pattern Blend:** 16 (merge intervals) + 08 (heap for k employees)
**Why:** Merge all intervals using heap. Find gaps in merged result.

---

## Blend 10: Math + Bit Manipulation

### Problem: Power of Four (LeetCode 342)
**Statement:** Is n a power of 4?
**Pattern Blend:** 17 (number theory) + 18 (bit check)
**Why:** Power of 2 check + bit in odd position check.

### Problem: Single Number II (LeetCode 137)
**Statement:** Every element appears 3 times except one.
**Pattern Blend:** 18 (bitwise) + 17 (counting/modular arithmetic)
**Why:** Count bits modulo 3. Or use two-bit state machine.

---

## Blend 11: Sliding Window + Heap

### Problem: Sliding Window Maximum (LeetCode 239)
**Statement:** Max in every window of size k.
**Pattern Blend:** 05 (window) + 03 (monotonic deque, which is stack-like) + 08 (heap alternative)
**Why:** Monotonic deque is O(n). Heap is O(n log k). Know both.

### Problem: Sliding Window Median (LeetCode 480)
**Statement:** Median in every window.
**Pattern Blend:** 05 (window) + 08 (two heaps for median)
**Why:** Two heaps + lazy deletion. Much harder than it looks.

---

## Blend 12: Linked List + Trees + Heap

### Problem: Merge k Sorted Lists (LeetCode 23)
**Statement:** Already listed, but worth repeating.
**Pattern Blend:** 06 + 08 + 02
**Why:** This is THE blended problem. Tests pointer manipulation, heap usage, and merging.

---

## Blend 13: Graphs + Union-Find + Heap

### Problem: Min Cost to Connect All Points (LeetCode 1584)
**Statement:** Connect all points with minimum cost.
**Pattern Blend:** 11 (graph) + 12 (MST) + 08 (Prim's with heap) + 12 (Kruskal with Union-Find)
**Why:** Can solve with Prim's (heap) or Kruskal's (Union-Find). Know both approaches.

---

## Blend 14: 1D DP + State Machine

### Problem: Best Time to Buy/Sell Stock with Cooldown (LeetCode 309)
**Statement:** Max profit with 1-day cooldown after selling.
**Pattern Blend:** 13 (1D DP) + 13.7 (state machine)
**Why:** Three states: hold, sold, rest. Recurrence between states.

### Problem: House Robber II (LeetCode 213)
**Statement:** Houses in circle.
**Pattern Blend:** 13 (linear DP) + 01 (two cases: rob first or not)
**Why:** Two scenarios: rob house 0 (can't rob last) or don't rob house 0.

---

## Blend 15: 2D DP + String Matching

### Problem: Regular Expression Matching (LeetCode 10)
**Statement:** Match string with pattern (.*).
**Pattern Blend:** 14 (2D DP) + 14.7 (string matching)
**Why:** dp[i][j] = first i chars of s match first j of p. Complex transitions.

### Problem: Edit Distance (LeetCode 72)
**Statement:** Min operations to convert word1 to word2.
**Pattern Blend:** 14 (2D DP) + 14.2 (edit distance template)
**Why:** Classic 2D DP. Three operations: insert, delete, replace.

---

## The Ultimate Blends (3+ Patterns)

### Problem: LRU Cache (LeetCode 146)
**Patterns:** 01 (hash map for O(1) lookup) + 06 (doubly linked list for O(1) eviction) + 03 (stack-like access pattern)
**Why:** One of the most famous design problems. Tests data structure combination.

### Problem: LFU Cache (LeetCode 460)
**Patterns:** 01 (hash map) + 06 (linked lists) + 08 (frequency buckets) + 13 (state tracking)
**Why:** Even harder than LRU. Multiple data structures working together.

### Problem: Design Search Autocomplete System (LeetCode 642)
**Patterns:** 10 (trie for prefix storage) + 08 (heap for ranking) + 01 (hash map for frequency)
**Why:** Real-world system design. Trie + heap + hash map.

### Problem: Design Underground System (LeetCode 1396)
**Patterns:** 01 (two hash maps: check-ins and stats) + 17 (average calculation)
**Why:** Simple but tests design thinking and multiple hash maps.

---

## Blended Drill Sets

### Set A: Easy Blends (2 patterns)
1. Two Sum II (01 + 02)
2. 3Sum Closest (01 + 02)
3. Top K Frequent (01 + 08)
4. Longest Substring Without Repeating (01 + 05)
5. Binary Tree Inorder Iterative (03 + 07)
6. Kth Smallest in BST (07 + 08)

### Set B: Medium Blends (2-3 patterns)
1. Subarrays with K Different (01 + 05 + 13)
2. Word Search II (09 + 10 + 11)
3. Network Delay Time (11 + 12 + 08)
4. Meeting Rooms II (15 + 16 + 08)
5. LIS (13 + 04)
6. Sliding Window Maximum (05 + 03)

### Set C: Hard Blends (3+ patterns)
1. Merge k Sorted Lists (06 + 08 + 02)
2. LRU Cache (01 + 06 + 03)
3. Word Search II (09 + 10 + 11)
4. Min Cost to Connect Points (11 + 12 + 08)
5. Regular Expression Matching (14 + 14.7)
6. LFU Cache (01 + 06 + 08 + 13)

---

## How to Practice Blends

1. **Read the problem** without looking at the blend hint
2. **Identify patterns** in 30 seconds
3. **Write the template** for each pattern
4. **Connect them** — how do they work together?
5. **Solve the problem**
6. **Check the blend hint** — did you identify correctly?

If you misidentified, study the confusion matrix in ROADMAP.md.

---

*Master these and you will dominate interviews. Most candidates know individual patterns. Very few can blend them seamlessly.*
