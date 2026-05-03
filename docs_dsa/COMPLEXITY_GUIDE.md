# Complexity Guide

> **"What's the best possible time/space for this problem type?"**
> Use this to sanity-check your solutions.

---

## Arrays & Hashing

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Existence checking | O(n) | O(n) | Hash set |
| Frequency counting | O(n) | O(k) where k = unique | Hash map |
| Two sum (unsorted) | O(n) | O(n) | Hash map |
| Two sum (sorted) | O(n) | O(1) | Two pointers |
| Grouping | O(n * k log k) | O(n) | Sort signature |
| Subarray sum = K | O(n) | O(n) | Prefix sum + hash |
| Longest consecutive | O(n) | O(n) | Hash set |

---

## Two Pointers

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Pair in sorted array | O(n) | O(1) | Converging |
| Remove duplicates in-place | O(n) | O(1) | Same-direction |
| Merge sorted arrays | O(n+m) | O(1) if in-place | Two pointers |
| Container with most water | O(n) | O(1) | Converging |
| Trapping rain water | O(n) | O(1) | Two pointers |
| Palindrome check | O(n) | O(1) | Converging |

---

## Stack

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Valid parentheses | O(n) | O(n) | Stack |
| Next greater element | O(n) | O(n) | Monotonic stack |
| RPN evaluation | O(n) | O(n) | Stack |
| Min stack | O(1) all ops | O(n) | Auxiliary stack |
| Decode string | O(n) | O(n) | Two stacks |

---

## Binary Search

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Find target | O(log n) | O(1) | Binary search |
| First/last occurrence | O(log n) | O(1) | Boundary search |
| Rotated array search | O(log n) | O(1) | Modified BS |
| Peak element | O(log n) | O(1) | Compare neighbors |
| Answer-space search | O(log C * check) | O(1) | Binary search |
| Kth in two sorted | O(log(min(m,n))) | O(1) | Partition |

---

## Sliding Window

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Fixed-size window sum | O(n) | O(1) | Window sum |
| Longest unique substring | O(n) | O(k) | Variable window |
| Minimum window substring | O(n) | O(k) | Variable window |
| Count subarrays exactly K | O(n) | O(k) | at_most(K) - at_most(K-1) |
| Window maximum | O(n) | O(k) | Monotonic deque |
| Window median | O(n log k) | O(k) | Two heaps |

---

## Linked List

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Reverse | O(n) | O(1) | Iterative |
| Detect cycle | O(n) | O(1) | Floyd's |
| Find middle | O(n) | O(1) | Fast/slow |
| Merge two sorted | O(n+m) | O(1) | Iterative |
| Remove nth from end | O(n) | O(1) | Fast/slow |
| Add two numbers | O(max(n,m)) | O(1) | Traverse both |

---

## Trees

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Traversal (any) | O(n) | O(h) recursive | DFS |
| Level order | O(n) | O(w) where w = max width | BFS |
| LCA in BST | O(h) | O(1) | BST property |
| LCA in binary tree | O(n) | O(h) | DFS |
| Diameter | O(n) | O(h) | Postorder |
| Serialize/deserialize | O(n) | O(n) | BFS/DFS |
| Validate BST | O(n) | O(h) | Inorder or bounds |

---

## Heap

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Top K | O(n log k) | O(k) | Min heap |
| Kth largest | O(n log k) | O(k) | Min heap |
| Merge K sorted | O(n log k) | O(k) | Min heap |
| Running median | O(log n) per op | O(n) | Two heaps |
| Meeting rooms II | O(n log n) | O(n) | Sort + heap |

---

## Backtracking

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Subsets | O(2^n) | O(n) | Backtracking |
| Permutations | O(n!) | O(n) | Backtracking |
| N-Queens | O(n!) | O(n) | Backtracking |
| Combination sum | O(2^n) worst | O(n) | Backtracking |
| Word break II | O(2^n) worst | O(n) | Backtracking + memo |

---

## Tries

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Insert | O(m) | O(m) | Trie |
| Search | O(m) | O(1) | Trie |
| Prefix search | O(m) | O(1) | Trie |
| Word search II | O(M * 4^L) | O(N) | Trie + DFS |

where m = word length, M = board cells, L = max word length, N = total letters

---

## Graphs

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| BFS traversal | O(V+E) | O(V) | Queue |
| DFS traversal | O(V+E) | O(V) | Stack/recursion |
| Shortest path (unweighted) | O(V+E) | O(V) | BFS |
| Cycle detection | O(V+E) | O(V) | DFS states |
| Topological sort | O(V+E) | O(V) | Kahn's or DFS |
| Connected components | O(V+E) | O(V) | DFS/BFS/UF |
| Clone graph | O(V+E) | O(V) | BFS/DFS + map |

---

## Advanced Graphs

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Shortest path (weighted, non-neg) | O((V+E) log V) | O(V) | Dijkstra + heap |
| Shortest path (negative weights) | O(VE) | O(V) | Bellman-Ford |
| All pairs shortest path | O(V^3) | O(V^2) | Floyd-Warshall |
| Minimum spanning tree | O(E log V) | O(V) | Prim's / Kruskal's |
| Detect negative cycle | O(VE) | O(V) | Bellman-Ford |
| Bridges/articulation points | O(V+E) | O(V) | Tarjan's |

---

## 1-D DP

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Climbing stairs | O(n) | O(1) | Fibonacci |
| House robber | O(n) | O(1) | Linear DP |
| Max subarray | O(n) | O(1) | Kadane's |
| Word break | O(n * m) | O(n) | Boolean DP |
| LIS | O(n log n) | O(n) | Patience sort |
| Coin change (min coins) | O(n * amount) | O(amount) | Unbounded knapsack |
| Stock with cooldown | O(n) | O(1) | State machine |

---

## 2-D DP

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Unique paths | O(mn) | O(min(m,n)) | Grid DP |
| Min path sum | O(mn) | O(min(m,n)) | Grid DP |
| Edit distance | O(mn) | O(min(m,n)) | 2D DP |
| LCS | O(mn) | O(min(m,n)) | 2D DP |
| 0/1 Knapsack | O(nW) | O(W) | 1D DP |
| Unbounded knapsack | O(nW) | O(W) | 1D DP forwards |
| Burst balloons | O(n^3) | O(n^2) | Interval DP |
| Regex matching | O(mn) | O(m) | 2D DP |

---

## Greedy

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Interval scheduling | O(n log n) | O(1) | Sort by end |
| Jump game | O(n) | O(1) | Track max reach |
| Jump game II | O(n) | O(1) | Greedy BFS |
| Gas station | O(n) | O(1) | Circuit check |
| Queue reconstruction | O(n^2) | O(n) | Sort + insert |

---

## Intervals

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Merge intervals | O(n log n) | O(n) | Sort + scan |
| Insert interval | O(n) | O(n) | Linear scan |
| Meeting rooms | O(n log n) | O(n) | Sort + heap |
| Non-overlapping | O(n log n) | O(1) | Greedy |

---

## Math & Geometry

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Count primes | O(n log log n) | O(n) | Sieve |
| GCD | O(log min(a,b)) | O(1) | Euclidean |
| Fast power | O(log n) | O(1) | Binary exponentiation |
| Matrix rotate | O(n^2) | O(1) | Transpose + reverse |
| Spiral matrix | O(n^2) | O(1) | Boundary tracking |

---

## Bit Manipulation

| Problem Type | Best Time | Best Space | Algorithm |
|---|---|---|---|
| Single number | O(n) | O(1) | XOR |
| Single number II | O(n) | O(1) | Bit counting |
| Missing number | O(n) | O(1) | XOR |
| Power of two | O(1) | O(1) | Bit check |
| Count bits | O(n) | O(1) | DP |
| Reverse bits | O(1) | O(1) | 32 iterations |

---

## Sanity Check Questions

When you finish coding, ask:

1. **Did I achieve the best possible time?**
   - If your solution is O(n^2) and the table says O(n), you missed something.

2. **Did I achieve the best possible space?**
   - If your solution is O(n) and the table says O(1), optimize.

3. **Is there a better algorithm?**
   - Check the table. If Dijkstra exists and you used BFS, you're wrong for weighted graphs.

4. **Did I handle all edge cases?**
   - Empty input, single element, all same, all different, maximum values.

---

*Use this guide to verify your solutions are optimal.*
