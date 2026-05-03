# Interview Simulation — Cold Start Problems

> **Instructions:** These problems are NOT labeled by pattern. Time yourself. Identify the pattern in 30 seconds. Then solve.
>
> **Do not look at the answer key until you've attempted the problem.**

---

## Set A: Easy Identification (30 sec per problem)

### Problem 1
**Statement:** Given an array of integers, find if the array contains any duplicates.

<details>
<summary>Answer Key (click after solving)</summary>

**Pattern:** 01 Arrays & Hashing — Existence Checking
**Archetype:** 1.1
**Template:** Hash set
**Code:**
```python
def contains_duplicate(nums):
    return len(nums) != len(set(nums))
```
</details>

---

### Problem 2
**Statement:** Given two strings s and t, return true if t is an anagram of s.

<details>
<summary>Answer Key</summary>

**Pattern:** 01 Arrays & Hashing — Frequency Counting
**Archetype:** 1.2
**Template:** Counter comparison
**Code:**
```python
from collections import Counter
def is_anagram(s, t):
    return Counter(s) == Counter(t)
```
</details>

---

### Problem 3
**Statement:** Given a sorted array of integers, find two numbers that add up to a specific target.

<details>
<summary>Answer Key</summary>

**Pattern:** 02 Two Pointers — Converging
**Archetype:** 2.1
**Why not hash map?** Because array is SORTED.
**Code:**
```python
def two_sum(numbers, target):
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target: return [l+1, r+1]
        elif s < target: l += 1
        else: r -= 1
```
</details>

---

### Problem 4
**Statement:** Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

<details>
<summary>Answer Key</summary>

**Pattern:** 03 Stack — Matching
**Archetype:** 3.1
**Code:**
```python
def is_valid(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in pairs.values(): stack.append(c)
        elif not stack or stack.pop() != pairs[c]: return False
    return not stack
```
</details>

---

### Problem 5
**Statement:** You are given an array of k linked-lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list.

<details>
<summary>Answer Key</summary>

**Pattern:** 08 Heap — Merge K Sorted
**Archetype:** 8.2
**Why heap?** Need to always get minimum of k lists efficiently.
**Code:** See pattern doc.
</details>

---

## Set B: Medium Identification (45 sec per problem)

### Problem 6
**Statement:** Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals.

<details>
<summary>Answer Key</summary>

**Pattern:** 16 Intervals — Merge
**Archetype:** 16.1
**Why:** Sort + scan is the standard approach.
**Code:** See pattern doc.
</details>

---

### Problem 7
**Statement:** A robot is located at the top-left corner of a m x n grid. The robot can only move either down or right at any point in time. How many possible unique paths are there?

<details>
<summary>Answer Key</summary>

**Pattern:** 14 2-D DP — Grid Path
**Archetype:** 14.1
**Why:** Each cell depends on cell above and cell to left.
**Code:**
```python
def unique_paths(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j-1]
    return dp[-1]
```
</details>

---

### Problem 8
**Statement:** Given an m x n 2D binary grid which represents a map of '1's (land) and '0's (water), return the number of islands.

<details>
<summary>Answer Key</summary>

**Pattern:** 11 Graphs — Connected Components
**Archetype:** 11.6
**Why:** Each island is a connected component of 1s.
**Code:** BFS or DFS from each unvisited land cell.
</details>

---

### Problem 9
**Statement:** Given an integer array nums, find the contiguous subarray with the largest sum, and return its sum.

<details>
<summary>Answer Key</summary>

**Pattern:** 13 1-D DP — Linear Choice (Kadane's)
**Archetype:** 13.1
**Why:** Max ending here = max(num, max_ending_here + num)
**Code:**
```python
def max_sub_array(nums):
    max_so_far = max_ending = nums[0]
    for num in nums[1:]:
        max_ending = max(num, max_ending + num)
        max_so_far = max(max_so_far, max_ending)
    return max_so_far
```
</details>

---

### Problem 10
**Statement:** Given a string s, find the length of the longest substring without repeating characters.

<details>
<summary>Answer Key</summary>

**Pattern:** 05 Sliding Window + 01 Hashing
**Archetype:** 5.2 + 1.1
**Why:** Window expands. Set tracks duplicates. Shrink when duplicate found.
**Code:** See pattern doc.
</details>

---

## Set C: Hard Identification (60 sec per problem)

### Problem 11
**Statement:** Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

<details>
<summary>Answer Key</summary>

**Pattern:** 01 Hash Map + 06 Doubly Linked List
**Why:** Hash map for O(1) lookup. Linked list for O(1) eviction order.
**Code:** See BLENDED_DRILLS.md
</details>

---

### Problem 12
**Statement:** You are given an array of strings words and a rectangular grid of characters. Return all words found in the grid.

<details>
<summary>Answer Key</summary>

**Pattern:** 10 Trie + 09 Backtracking + 11 Graph DFS
**Archetype:** 10.2 + 9.5 + 11.2
**Why:** Trie stores words efficiently. DFS searches grid. Prune using trie.
**Code:** See pattern doc.
</details>

---

### Problem 13
**Statement:** There is a new alien language which uses the english alphabet. However, the order among letters is unknown to you. You are given a list of strings from the alien language, sorted lexicographically. Derive the order of letters.

<details>
<summary>Answer Key</summary>

**Pattern:** 11 Graphs — Topological Sort
**Archetype:** 11.4
**Why:** Compare adjacent words to build graph of character order. Topo sort.
**Code:** See pattern doc.
</details>

---

### Problem 14
**Statement:** You have a graph of n nodes labeled from 0 to n - 1. You are given an integer n and a list of edges where edges[i] = [ai, bi] indicates that there is an undirected edge between ai and bi. Return the number of connected components.

<details>
<summary>Answer Key</summary>

**Pattern:** 11 Graphs (DFS/BFS) OR 12 Union-Find
**Why:** Both work. Union-Find is more elegant for this specific problem.
**Code:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.count = n
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py:
            self.parent[py] = px
            self.count -= 1

def count_components(n, edges):
    uf = UnionFind(n)
    for a, b in edges:
        uf.union(a, b)
    return uf.count
```
</details>

---

### Problem 15
**Statement:** Given an integer array nums, return the number of subarrays filled with 0.

<details>
<summary>Answer Key</summary>

**Pattern:** 13 1-D DP — Counting
**Why:** Consecutive k zeros contribute k*(k+1)/2 subarrays.
**Code:**
```python
def zero_filled_subarray(nums):
    total = current = 0
    for num in nums:
        if num == 0:
            current += 1
            total += current
        else:
            current = 0
    return total
```
</details>

---

## Set D: Expert Level (90 sec per problem)

### Problem 16
**Statement:** You are given k identical eggs and you have access to a building with n floors labeled from 1 to n. Return the minimum number of moves to determine with certainty what the value of f is.

<details>
<summary>Answer Key</summary>

**Pattern:** 14 2-D DP — Optimization
**Why:** dp[e][f] = min moves with e eggs and f floors. Try every floor.
**Optimization:** Binary search on floor to drop from.
**Code:** See advanced DP resources.
</details>

---

### Problem 17
**Statement:** Design a simplified version of Twitter where users can post tweets, follow/unfollow another user, and see the 10 most recent tweets in the user's news feed.

<details>
<summary>Answer Key</summary>

**Pattern:** 08 Heap + 01 Hash Map + 06 Linked List
**Why:** Heap merges k users' tweets. Hash maps track followers and tweets.
**Code:** Design problem. Use heap of (timestamp, tweet_id).
</details>

---

### Problem 18
**Statement:** Given an integer n, count the total number of digit 1 appearing in all non-negative integers less than or equal to n.

<details>
<summary>Answer Key</summary>

**Pattern:** 17 Math — Digit DP
**Why:** Count 1s at each digit position separately.
**Code:** See math resources.
</details>

---

## Scoring

| Set | Problems | Target Time | Mastery Level |
|---|---|---|---|
| A | 5 | 30 sec each | Pattern recognition |
| B | 5 | 45 sec each | Medium blending |
| C | 5 | 60 sec each | Hard blending |
| D | 3 | 90 sec each | Expert identification |

**Scoring:**
- 18/18 correct: You are interview-ready for pattern identification
- 15-17 correct: Strong, but review missed patterns
- 10-14 correct: Need more practice with blended problems
- <10 correct: Go back to individual pattern practice

---

*Do this weekly. Time yourself. Track your scores.*
