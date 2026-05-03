# DSA Quick Reference — 1-Page Cheat Sheet

> **Use this during practice:** Glance at the trigger words. If they match, write the template.

---

## The 18 Patterns at a Glance

| # | Pattern | Trigger Words | Core Operation | Template Size |
|---|---|---|---|---|
| 01 | Arrays & Hashing | "find", "count", "duplicate", "frequency", "group", "pair" | Hash map/set lookup | 5 lines |
| 02 | Two Pointers | "sorted", "pair sum", "palindrome", "merge", "in-place" | Converge from ends or same direction | 6 lines |
| 03 | Stack | "valid parentheses", "next greater", "history", "undo" | Push/pop LIFO | 4 lines |
| 04 | Binary Search | "sorted", "O(log n)", "find min/max where condition changes" | Halve search space | 6 lines |
| 05 | Sliding Window | "subarray", "substring", "consecutive", "at most K" | Expand/shrink window | 8 lines |
| 06 | Linked List | "reverse", "cycle", "merge", "remove nth", "reorder" | Pointer manipulation | 6 lines |
| 07 | Trees | "root-to-leaf", "LCA", "level order", "path sum" | Recursion/stack/queue | 4 lines |
| 08 | Heap | "K largest/smallest", "merge K", "median", "schedule" | Min/max access | 5 lines |
| 09 | Backtracking | "all combinations", "permutations", "subsets", "N-queens" | DFS with undo | 8 lines |
| 10 | Tries | "prefix", "auto-complete", "word search", "XOR" | Tree of characters | 10 lines |
| 11 | Graphs | "connected", "path", "shortest", "dependencies", "islands" | BFS/DFS | 6 lines |
| 12 | Advanced Graphs | "shortest path weighted", "MST", "negative weights" | Dijkstra/Prim/UF | 10 lines |
| 13 | 1-D DP | "maximize", "ways to reach", "decision at each step" | Cache subproblems | 5 lines |
| 14 | 2-D DP | "grid", "edit distance", "LCS", "knapsack" | 2D table | 6 lines |
| 15 | Greedy | "minimum intervals", "pick cheapest", "non-overlapping" | Local optimal | 4 lines |
| 16 | Intervals | "merge", "overlap", "meeting rooms", "schedule" | Sort + scan | 5 lines |
| 17 | Math & Geometry | "GCD", "prime", "matrix rotate", "power", "game" | Math properties | varies |
| 18 | Bit Manipulation | "single number", "power of two", "XOR", "subset mask" | Bit operators | 3 lines |

---

## Ultra-Condensed Templates

### 01 — Hash Map Existence
```python
seen = set()
for x in arr:
    if x in seen: return True
    seen.add(x)
return False
```

### 01 — Two Sum (Complement)
```python
seen = {}
for i, x in enumerate(nums):
    if target - x in seen: return [seen[target-x], i]
    seen[x] = i
```

### 02 — Converging Two Pointers
```python
l, r = 0, len(arr)-1
while l < r:
    if condition(arr[l], arr[r]): return result
    elif too_small: l += 1
    else: r -= 1
```

### 03 — Monotonic Stack (Next Greater)
```python
stack = []
for i, x in enumerate(arr):
    while stack and x > arr[stack[-1]]:
        result[stack.pop()] = x
    stack.append(i)
```

### 04 — Binary Search
```python
l, r = 0, len(arr)-1
while l <= r:
    m = l + (r-l)//2
    if arr[m] == target: return m
    elif arr[m] < target: l = m+1
    else: r = m-1
return -1
```

### 05 — Sliding Window (Variable)
```python
l = 0
for r in range(len(s)):
    window.add(s[r])
    while invalid(window):
        window.remove(s[l])
        l += 1
    ans = max(ans, r-l+1)
```

### 06 — Reverse Linked List
```python
prev, curr = None, head
while curr:
    nxt = curr.next
    curr.next = prev
    prev, curr = curr, nxt
return prev
```

### 07 — Tree DFS
```python
def dfs(node):
    if not node: return base_case
    left = dfs(node.left)
    right = dfs(node.right)
    return combine(node, left, right)
```

### 08 — Top K (Min Heap)
```python
heap = nums[:k]; heapify(heap)
for x in nums[k:]:
    if x > heap[0]: heapreplace(heap, x)
return heap[0]
```

### 09 — Backtracking
```python
def backtrack(path, choices):
    if valid(path): result.append(path[:]); return
    for choice in choices:
        if not valid(choice): continue
        path.append(choice)
        backtrack(path, next_choices)
        path.pop()  # UNDO
```

### 10 — Trie Insert
```python
node = root
for ch in word:
    if ch not in node.children: node.children[ch] = TrieNode()
    node = node.children[ch]
node.is_end = True
```

### 11 — BFS
```python
queue = [start]; visited = {start}
while queue:
    node = queue.pop(0)
    for nei in graph[node]:
        if nei not in visited:
            visited.add(nei); queue.append(nei)
```

### 12 — Dijkstra
```python
heap = [(0, start)]; dist = {start: 0}
while heap:
    d, u = heappop(heap)
    if d > dist[u]: continue
    for v, w in graph[u]:
        if d+w < dist.get(v, inf):
            dist[v] = d+w; heappush(heap, (d+w, v))
```

### 13 — 1D DP
```python
dp = [0] * n; dp[0] = base
for i in range(1, n):
    dp[i] = recurrence(dp[i-1], dp[i-2], arr[i])
return dp[-1]
```

### 14 — Edit Distance
```python
dp = [[0]*(m+1) for _ in range(n+1)]
for i in range(1, n+1):
    for j in range(1, m+1):
        if s1[i-1]==s2[j-1]: dp[i][j]=dp[i-1][j-1]
        else: dp[i][j]=1+min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
```

### 15 — Interval Greedy
```python
intervals.sort(key=lambda x: x[1])
count, end = 0, -inf
for s, e in intervals:
    if s >= end: count += 1; end = e
```

### 16 — Merge Intervals
```python
intervals.sort(); result = [intervals[0]]
for curr in intervals[1:]:
    last = result[-1]
    if curr[0] <= last[1]: last[1] = max(last[1], curr[1])
    else: result.append(curr)
```

### 18 — XOR Single Number
```python
result = 0
for num in nums: result ^= num
return result
```

---

## The 10-Second Decision Tree

```
Does problem ask for O(1) lookup by value?
  YES → 01 Arrays & Hashing

Is array sorted or can be sorted?
  YES + need pair/area/container → 02 Two Pointers
  YES + need O(log n) search → 04 Binary Search

Need contiguous subarray/substring?
  YES → 05 Sliding Window

Need last-in-first-out processing?
  YES → 03 Stack

Working with nodes and pointers?
  YES → 06 Linked List

Hierarchical structure?
  YES → 07 Trees

Need extreme element (min/max) fast?
  YES → 08 Heap

Explore all possibilities?
  YES → 09 Backtracking

Prefix-based string matching?
  YES → 10 Tries

Nodes connected by edges?
  YES + unweighted → 11 Graphs BFS/DFS
  YES + weighted → 12 Advanced Graphs

Optimize over sequence of decisions?
  YES → 13 1-D DP or 14 2-D DP

Always pick best local option?
  YES → 15 Greedy or 16 Intervals

Number theory or spatial?
  YES → 17 Math & Geometry

Operating on individual bits?
  YES → 18 Bit Manipulation
```

---

## Blended Pattern Quick ID

| Problem | Patterns | Trigger |
|---|---|---|
| Top K Frequent | 01 + 08 | Count + extract top |
| Word Search II | 10 + 11 | Dictionary + grid |
| LRU Cache | 01 + 06 | Lookup + eviction order |
| Kth Smallest Matrix | 04 + 08 | Value search + priority |
| Subarrays K Distinct | 05 + 01 | Window + frequency |
| Longest Consecutive | 01 + sequence | Set + build chains |
| Meeting Rooms II | 16 + 08 | Intervals + scheduling |
| Reorganize String | 15 + 08 | Greedy + max freq |
| Course Schedule | 11 + 13 | Graph + topological |
| Paint House | 13 + state | Linear + color states |

---

## Complexity Quick Reference

| Operation | Array | Hash Map | Heap | BST |
|---|---|---|---|---|
| Access | O(1) | O(1) | O(1) min/max | O(log n) |
| Search | O(n) | O(1) | O(n) | O(log n) |
| Insert | O(1)* | O(1) | O(log n) | O(log n) |
| Delete | O(n) | O(1) | O(log n) | O(log n) |

*Amortized

---

## Must-Memorize Formulas

- **2-sum sorted:** Two pointers, O(n)
- **LIS:** Patience sorting, O(n log n)
- **Edit distance:** dp[i][j], O(mn)
- **0/1 Knapsack:** Backwards iteration, O(nW)
- **Coin change:** Forwards iteration, O(nW)
- **Dijkstra:** Heap, O((V+E) log V)
- **Floyd-Warshall:** Triple loop, O(V^3)
- **Union-Find:** Path compression, O(α(V))
- **Power of 2:** `n & (n-1) == 0`
- **XOR swap:** `a ^= b; b ^= a; a ^= b`

---

*Print this page. Keep it next to you while practicing.*
