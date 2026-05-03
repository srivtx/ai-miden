# DSA Progress Tracker

> **Print this or copy into your notes. Check off problems as you solve them without hints.**
>
> **Legend:** ✅ = Solved cold | 🔄 = Solved with hints | ❌ = Need to revisit

---

## Pattern 01: Arrays & Hashing

### Warm-Up
- [ ] 217. Contains Duplicate
- [ ] 242. Valid Anagram
- [ ] 1. Two Sum

### Core
- [ ] 49. Group Anagrams
- [ ] 347. Top K Frequent Elements
- [ ] 238. Product of Array Except Self
- [ ] 128. Longest Consecutive Sequence
- [ ] 271. Encode and Decode Strings
- [ ] 380. Insert Delete GetRandom O(1)

### Advanced
- [ ] 560. Subarray Sum Equals K
- [ ] 525. Contiguous Array
- [ ] 523. Continuous Subarray Sum
- [ ] 325. Maximum Size Subarray Sum Equals K

**Gate Check:**
- [ ] Can write two-sum hash map in < 2 minutes
- [ ] Can explain why we check before insert
- [ ] Can derive prefix sum formula

---

## Pattern 02: Two Pointers

### Warm-Up
- [ ] 125. Valid Palindrome
- [ ] 167. Two Sum II

### Core
- [ ] 15. 3Sum
- [ ] 11. Container With Most Water
- [ ] 42. Trapping Rain Water
- [ ] 16. 3Sum Closest

### Same-Direction
- [ ] 26. Remove Duplicates from Sorted Array
- [ ] 27. Remove Element
- [ ] 283. Move Zeroes
- [ ] 80. Remove Duplicates II

### Advanced
- [ ] 881. Boats to Save People
- [ ] 977. Squares of Sorted Array

**Gate Check:**
- [ ] Know when to use pointers vs hash map
- [ ] Can explain why move shorter line in container

---

## Pattern 03: Stack

### Warm-Up
- [ ] 20. Valid Parentheses
- [ ] 155. Min Stack

### Core
- [ ] 150. Evaluate RPN
- [ ] 739. Daily Temperatures
- [ ] 853. Car Fleet

### Advanced
- [ ] 84. Largest Rectangle in Histogram
- [ ] 85. Maximal Rectangle
- [ ] 224. Basic Calculator
- [ ] 394. Decode String

**Gate Check:**
- [ ] Can write monotonic stack template
- [ ] Know when stack simulates recursion

---

## Pattern 04: Binary Search

### Warm-Up
- [ ] 704. Binary Search
- [ ] 35. Search Insert Position

### Core
- [ ] 74. Search a 2D Matrix
- [ ] 33. Search in Rotated Sorted Array
- [ ] 153. Find Minimum in Rotated Array
- [ ] 34. Find First and Last Position

### Advanced
- [ ] 4. Median of Two Sorted Arrays
- [ ] 875. Koko Eating Bananas
- [ ] 1011. Capacity To Ship Packages

**Gate Check:**
- [ ] Know `left <= right` vs `left < right`
- [ ] Can find boundary (first/last occurrence)
- [ ] Can set up answer-space search

---

## Pattern 05: Sliding Window

### Fixed Size
- [ ] 643. Maximum Average Subarray I
- [ ] 219. Contains Duplicate II
- [ ] 1343. Number of Subarrays Size K

### Variable Size
- [ ] 3. Longest Substring Without Repeating
- [ ] 424. Longest Repeating Character Replacement
- [ ] 904. Fruit Into Baskets
- [ ] 1004. Max Consecutive Ones III

### Minimum Window
- [ ] 76. Minimum Window Substring
- [ ] 209. Minimum Size Subarray Sum
- [ ] 567. Permutation in String

### Advanced
- [ ] 239. Sliding Window Maximum
- [ ] 862. Shortest Subarray with Sum at Least K
- [ ] 992. Subarrays with K Different Integers

**Gate Check:**
- [ ] Know fixed vs variable templates
- [ ] Know `at_most(K) - at_most(K-1)` trick
- [ ] Know when NOT to use sliding window

---

## Pattern 06: Linked List

### Core
- [ ] 206. Reverse Linked List
- [ ] 21. Merge Two Sorted Lists
- [ ] 141. Linked List Cycle
- [ ] 142. Linked List Cycle II

### Advanced
- [ ] 143. Reorder List
- [ ] 19. Remove Nth From End
- [ ] 23. Merge k Sorted Lists
- [ ] 138. Copy List with Random Pointer
- [ ] 25. Reverse Nodes in k-Group

**Gate Check:**
- [ ] Can reverse iteratively and recursively
- [ ] Can find middle with fast/slow
- [ ] Always use dummy node when head might change

---

## Pattern 07: Trees

### Traversals
- [ ] 144. Preorder Traversal
- [ ] 94. Inorder Traversal
- [ ] 145. Postorder Traversal
- [ ] 102. Level Order Traversal

### Core
- [ ] 104. Maximum Depth
- [ ] 100. Same Tree
- [ ] 226. Invert Binary Tree
- [ ] 98. Validate BST
- [ ] 110. Balanced Binary Tree
- [ ] 572. Subtree of Another Tree

### Path & LCA
- [ ] 112. Path Sum
- [ ] 113. Path Sum II
- [ ] 437. Path Sum III
- [ ] 235. LCA of BST
- [ ] 236. LCA of Binary Tree

### Advanced
- [ ] 124. Binary Tree Maximum Path Sum
- [ ] 297. Serialize and Deserialize
- [ ] 105. Construct from Traversals
- [ ] 543. Diameter of Binary Tree

**Gate Check:**
- [ ] All traversals recursive and iterative
- [ ] LCA in BST (O(h)) and binary tree (O(n))
- [ ] Diameter / max path sum with postorder

---

## Pattern 08: Heap

### Core
- [ ] 215. Kth Largest Element
- [ ] 973. K Closest Points to Origin
- [ ] 378. Kth Smallest in Sorted Matrix

### Scheduling
- [ ] 253. Meeting Rooms II
- [ ] 621. Task Scheduler
- [ ] 767. Reorganize String

### Median
- [ ] 295. Find Median from Data Stream
- [ ] 480. Sliding Window Median

**Gate Check:**
- [ ] Can implement min heap for top K
- [ ] Know two-heap median structure
- [ ] Know when heap beats sorting

---

## Pattern 09: Backtracking

### Core
- [ ] 78. Subsets
- [ ] 90. Subsets II
- [ ] 46. Permutations
- [ ] 47. Permutations II
- [ ] 77. Combinations

### Sum Problems
- [ ] 39. Combination Sum
- [ ] 40. Combination Sum II
- [ ] 216. Combination Sum III

### Advanced
- [ ] 51. N-Queens
- [ ] 37. Sudoku Solver
- [ ] 131. Palindrome Partitioning
- [ ] 79. Word Search
- [ ] 212. Word Search II

**Gate Check:**
- [ ] Know the template by heart
- [ ] Know when to use used[] array
- [ ] Know when to sort to skip duplicates

---

## Pattern 10: Tries

### Core
- [ ] 208. Implement Trie
- [ ] 211. Add and Search Word

### Word Search
- [ ] 79. Word Search
- [ ] 212. Word Search II

### Advanced
- [ ] 648. Replace Words
- [ ] 421. Maximum XOR of Two Numbers

**Gate Check:**
- [ ] Can implement insert, search, startsWith
- [ ] Know when trie beats hash set

---

## Pattern 11: Graphs

### Core
- [ ] 200. Number of Islands
- [ ] 133. Clone Graph
- [ ] 695. Max Area of Island
- [ ] 417. Pacific Atlantic Water Flow

### Cycle & Topo
- [ ] 207. Course Schedule
- [ ] 210. Course Schedule II
- [ ] 261. Graph Valid Tree

### Advanced
- [ ] 994. Rotting Oranges
- [ ] 286. Walls and Gates
- [ ] 127. Word Ladder
- [ ] 721. Accounts Merge

**Gate Check:**
- [ ] BFS vs DFS decision tree
- [ ] Cycle detection with 3 states
- [ ] Topological sort (Kahn's and DFS)

---

## Pattern 12: Advanced Graphs

### Core
- [ ] 743. Network Delay Time
- [ ] 787. Cheapest Flights K Stops
- [ ] 1584. Min Cost to Connect Points

### Union-Find
- [ ] 547. Number of Provinces
- [ ] 684. Redundant Connection
- [ ] 1319. Number of Operations to Connect

### Advanced
- [ ] 1192. Critical Connections

**Gate Check:**
- [ ] Can implement Dijkstra
- [ ] Can implement Union-Find with path compression
- [ ] Know when to use which algorithm

---

## Pattern 13: 1-D DP

### Core
- [ ] 70. Climbing Stairs
- [ ] 198. House Robber
- [ ] 213. House Robber II
- [ ] 91. Decode Ways
- [ ] 322. Coin Change

### Advanced
- [ ] 300. Longest Increasing Subsequence
- [ ] 139. Word Break
- [ ] 53. Maximum Subarray
- [ ] 152. Maximum Product Subarray
- [ ] 309. Stock with Cooldown

**Gate Check:**
- [ ] Can define dp[i] meaning
- [ ] Can derive recurrence
- [ ] Can optimize space to O(1) or O(k)

---

## Pattern 14: 2-D DP

### Core
- [ ] 62. Unique Paths
- [ ] 64. Minimum Path Sum
- [ ] 72. Edit Distance
- [ ] 1143. Longest Common Subsequence

### Advanced
- [ ] 416. Partition Equal Subset Sum
- [ ] 494. Target Sum
- [ ] 312. Burst Balloons
- [ ] 10. Regular Expression Matching

**Gate Check:**
- [ ] Can reduce 2D to 1D when possible
- [ ] Know 0/1 vs unbounded knapsack iteration direction

---

## Pattern 15: Greedy

### Core
- [ ] 55. Jump Game
- [ ] 45. Jump Game II
- [ ] 134. Gas Station
- [ ] 763. Partition Labels

### Advanced
- [ ] 406. Queue Reconstruction by Height
- [ ] 135. Candy

**Gate Check:**
- [ ] Know when greedy works
- [ ] Can prove greedy choice property

---

## Pattern 16: Intervals

### Core
- [ ] 56. Merge Intervals
- [ ] 57. Insert Interval
- [ ] 435. Non-overlapping Intervals
- [ ] 252. Meeting Rooms
- [ ] 253. Meeting Rooms II

### Advanced
- [ ] 986. Interval List Intersections
- [ ] 759. Employee Free Time

**Gate Check:**
- [ ] Sort by start or end depending on problem
- [ ] Know overlap condition

---

## Pattern 17: Math & Geometry

### Core
- [ ] 48. Rotate Image
- [ ] 54. Spiral Matrix
- [ ] 202. Happy Number
- [ ] 50. Pow(x, n)
- [ ] 43. Multiply Strings

### Advanced
- [ ] 149. Max Points on a Line
- [ ] 166. Fraction to Recurring Decimal

**Gate Check:**
- [ ] Fast modular exponentiation
- [ ] Matrix operations in-place

---

## Pattern 18: Bit Manipulation

### Core
- [ ] 136. Single Number
- [ ] 191. Number of 1 Bits
- [ ] 338. Counting Bits
- [ ] 190. Reverse Bits
- [ ] 268. Missing Number

### Advanced
- [ ] 137. Single Number II
- [ ] 260. Single Number III
- [ ] 421. Maximum XOR of Two Numbers

**Gate Check:**
- [ ] XOR properties
- [ ] Power of 2 check
- [ ] Brian Kernighan bit count

---

## Overall Progress

| Phase | Problems | Completed | % |
|---|---|---|---|
| Phase 1: Foundation (01-06) | 35 | ___ | ___% |
| Phase 2: Trees & Graphs (07-12) | 45 | ___ | ___% |
| Phase 3: DP & Advanced (13-18) | 45 | ___ | ___% |
| **Total** | **125** | **___** | **___%** |

---

## Weekly Log

| Week | Patterns Studied | Problems Solved | Time Spent | Notes |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |

---

## Weak Areas Tracker

Patterns I consistently struggle with:
1. _________________________
2. _________________________
3. _________________________

Problems I need to revisit:
1. _________________________
2. _________________________
3. _________________________

---

*Update this tracker daily. Be honest about what you solved cold vs with hints.*
