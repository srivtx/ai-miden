# Pattern 14: 2-D DP — Drills Part 2

> **5 Warm-ups + 10 Core Drills**
> Focus: Build 2-D table intuition before tackling complex transitions and space optimization.

---

## Warm-ups

### 1. LeetCode 62. Unique Paths
**Archetype:** 14.1 Grid Path
**Type:** Warm-Up
**Statement:** A robot starts at top-left and wants to reach bottom-right, moving only right or down. Count unique paths.
**Why it fits:** The canonical 2-D DP. `dp[i][j]` = number of ways to reach cell `(i, j)`. The recurrence `dp[i][j] = dp[i-1][j] + dp[i][j-1]` captures the two possible previous cells.
**The Twist:** None — this is the archetype. Practice the 1-D space optimization because only the previous row is needed.
**Code Skeleton:**
```python
def uniquePaths(m: int, n: int) -> int:
    # 1D optimization: dp[j] represents current row's ways to column j
    dp = [1] * n
    for i in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[n - 1]
```

---

### 2. LeetCode 1143. Longest Common Subsequence
**Archetype:** 14.3 LCS Variations
**Type:** Warm-Up
**Statement:** Given two strings, find the length of their longest common subsequence.
**Why it fits:** The foundational string 2-D DP. `dp[i][j]` = LCS of `text1[0:i]` and `text2[0:j]`. If characters match, add 1 to the diagonal; otherwise take the max of top and left.
**The Twist:** The subsequence is not contiguous, so you never move diagonally on mismatch. The table dimensions are `(m+1) x (n+1)` to handle empty prefixes gracefully.
**Code Skeleton:**
```python
def longestCommonSubsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

---

### 3. LeetCode 72. Edit Distance
**Archetype:** 14.2 Edit Distance
**Type:** Warm-Up
**Statement:** Given two strings, return the minimum number of operations (insert, delete, replace) to convert one to the other.
**Why it fits:** `dp[i][j]` = edit distance between first `i` chars of word1 and first `j` chars of word2. The three operations map directly to three neighboring cells (left, top, diagonal).
**The Twist:** When characters match, the cost is zero (diagonal). When they differ, you take the minimum of the three neighbors plus one. Base cases are the full first row and column.
**Code Skeleton:**
```python
def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],    # delete
                                   dp[i][j - 1],    # insert
                                   dp[i - 1][j - 1]) # replace
    return dp[m][n]
```

---

### 4. LeetCode 322. Coin Change
**Archetype:** 14.5 Knapsack Unbounded
**Type:** Warm-Up
**Statement:** Given coins of different denominations and an amount, find the fewest coins to make up that amount.
**Why it fits:** This is unbounded knapsack in 1-D form. `dp[a]` = min coins for amount `a`. Iterate coins outer, amounts inner, forwards — because each coin can be reused.
**The Twist:** The forward iteration distinguishes unbounded from 0/1 knapsack. Initialize with infinity and check for unreachable amounts at the end.
**Code Skeleton:**
```python
def coinChange(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] = min(dp[a], dp[a - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

---

### 5. LeetCode 63. Unique Paths II
**Archetype:** 14.1 Grid Path
**Type:** Warm-Up
**Statement:** Same as Unique Paths, but some cells are obstacles (marked 1).
**Why it fits:** Adds a boolean condition to the grid path archetype. If a cell is an obstacle, its path count is zero; otherwise use the standard recurrence. Teaches handling blocked states in grid DP.
**The Twist:** The start or end cell might be an obstacle. You must also handle the first row/column initialization carefully when obstacles appear early.
**Code Skeleton:**
```python
def uniquePathsWithObstacles(obstacleGrid: list[list[int]]) -> int:
    m, n = len(obstacleGrid), len(obstacleGrid[0])
    dp = [0] * n
    dp[0] = 1 if obstacleGrid[0][0] == 0 else 0
    for i in range(m):
        for j in range(n):
            if obstacleGrid[i][j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]
            # if j == 0, dp[j] carries down from previous row
    return dp[n - 1]
```

---

## Core Drills

### 6. LeetCode 416. Partition Equal Subset Sum
**Archetype:** 14.4 Knapsack 0/1
**Type:** Core Drill
**Statement:** Given an array of positive integers, determine if it can be partitioned into two subsets with equal sums.
**Why it fits:** This is the classic 0/1 knapsack decision problem. If total sum is even, find a subset that sums to `total // 2`. Each number can be used at most once.
**The Twist:** The target is derived from the total sum, not given. The backward iteration over the target is essential to prevent reusing the same element multiple times.
**Code Skeleton:**
```python
def canPartition(nums: list[int]) -> bool:
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True
    for num in nums:
        for t in range(target, num - 1, -1):
            dp[t] = dp[t] or dp[t - num]
    return dp[target]
```

---

### 7. LeetCode 64. Minimum Path Sum
**Archetype:** 14.1 Grid Path
**Type:** Core Drill
**Statement:** Given a grid of non-negative numbers, find a path from top-left to bottom-right that minimizes the sum of all numbers along its path.
**Why it fits:** `dp[i][j]` = min path sum to reach `(i, j)`. Same grid structure as Unique Paths, but with min instead of sum and weighted cells.
**The Twist:** The first row and column have no choice — they are accumulated sums. This teaches that grid DP initialization is not always all 1s.
**Code Skeleton:**
```python
def minPathSum(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    dp = [0] * n
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                dp[j] = grid[i][j]
            elif i == 0:
                dp[j] = dp[j - 1] + grid[i][j]
            elif j == 0:
                dp[j] = dp[j] + grid[i][j]
            else:
                dp[j] = min(dp[j], dp[j - 1]) + grid[i][j]
    return dp[n - 1]
```

---

### 8. LeetCode 583. Delete Operation for Two Strings
**Archetype:** 14.3 LCS Variations
**Type:** Core Drill
**Statement:** Given two words, find the minimum number of steps to make them the same by deleting characters from either word.
**Why it fits:** The answer is `len(word1) + len(word2) - 2 * LCS`. It tests whether you can recognize an LCS problem when it is disguised as a deletion problem.
**The Twist:** The problem does not mention "common subsequence" at all. You must realize that the undeleted characters form an LCS, making this a direct application of the LCS template.
**Code Skeleton:**
```python
def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[m][n]
    return (m - lcs) + (n - lcs)
```

---

### 9. LeetCode 518. Coin Change 2
**Archetype:** 14.5 Knapsack Unbounded
**Type:** Core Drill
**Statement:** Given coins and an amount, return the number of combinations that make up that amount.
**Why it fits:** Unbounded knapsack counting variant. `dp[a]` = number of ways to form amount `a`. The order of coins in the outer loop ensures combinations, not permutations.
**The Twist:** If you iterate amounts outer and coins inner, you count permutations (Combination Sum IV). The order matters for counting vs combinations.
**Code Skeleton:**
```python
def change(amount: int, coins: list[int]) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1
    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] += dp[a - coin]
    return dp[amount]
```

---

### 10. LeetCode 10. Regular Expression Matching
**Archetype:** 14.7 String Matching
**Type:** Core Drill
**Statement:** Implement regular expression matching with support for `.` (matches any single char) and `*` (matches zero or more of the preceding element).
**Why it fits:** `dp[i][j]` = does `s[0:i]` match `p[0:j]`? The `*` handling requires looking two cells back (zero occurrences) or diagonally up (one or more occurrences). This is the most complex 2-D boolean DP.
**The Twist:** `*` can represent zero occurrences (skip `x*` in pattern) or multiple occurrences (match current char and stay). The state transition for `*` is the hardest part.
**Code Skeleton:**
```python
def isMatch(s: str, p: str) -> bool:
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    # Pattern like a* or a*b* can match empty string
    for j in range(2, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '.' or p[j - 1] == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            elif p[j - 1] == '*':
                # Zero occurrences of preceding char
                dp[i][j] = dp[i][j - 2]
                # One or more occurrences (if preceding matches current)
                if p[j - 2] == '.' or p[j - 2] == s[i - 1]:
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
    return dp[m][n]
```

---

### 11. LeetCode 44. Wildcard Matching
**Archetype:** 14.7 String Matching
**Type:** Core Drill
**Statement:** Given an input string and a pattern with `?` (single char) and `*` (any sequence including empty), implement wildcard matching.
**Why it fits:** Similar to regex matching but `*` is more powerful (any sequence, not just repeats of one char). `dp[i][j]` = does `s[0:i]` match `p[0:j]`? The `*` transition looks at `dp[i][j-1]` (empty) or `dp[i-1][j]` (consume one char).
**The Twist:** `*` can match any sequence, so the transition is simpler than regex `*` in some ways but the pattern logic is different. The O(1) space two-pointer greedy solution is also possible.
**Code Skeleton:**
```python
def isMatch(s: str, p: str) -> bool:
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 1]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '?' or p[j - 1] == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            elif p[j - 1] == '*':
                dp[i][j] = dp[i][j - 1] or dp[i - 1][j]
    return dp[m][n]
```

---

### 12. LeetCode 494. Target Sum
**Archetype:** 14.4 Knapsack 0/1
**Type:** Core Drill
**Statement:** Assign `+` or `-` to each integer in nums so the expression equals target. Count the number of ways.
**Why it fits:** Let `P` = positive subset, `N` = negative subset. `sum(P) - sum(N) = target` and `sum(P) + sum(N) = total`. Solving gives `sum(P) = (target + total) / 2`. This reduces to counting subsets with a given sum.
**The Twist:** The target can be negative or larger than the total sum, so early checks are needed. The transformation from signs to subset sum is the key insight.
**Code Skeleton:**
```python
def findTargetSumWays(nums: list[int], target: int) -> int:
    total = sum(nums)
    # sum(P) - sum(N) = target, sum(P) + sum(N) = total
    # => sum(P) = (target + total) // 2
    if total < abs(target) or (target + total) % 2 != 0:
        return 0
    subset_sum = (target + total) // 2
    dp = [0] * (subset_sum + 1)
    dp[0] = 1
    for num in nums:
        for s in range(subset_sum, num - 1, -1):
            dp[s] += dp[s - num]
    return dp[subset_sum]
```

---

### 13. LeetCode 312. Burst Balloons
**Archetype:** 14.6 Interval DP
**Type:** Core Drill
**Statement:** Given n balloons with values, burst balloon `i` to get `nums[left] * nums[i] * nums[right]` coins. Find the max coins you can collect.
**Why it fits:** `dp[i][j]` = max coins from bursting all balloons between `i` and `j` (exclusive). For each possible last balloon to burst in the interval, combine left and right subproblems.
**The Twist:** The interval DP requires thinking about the *last* action rather than the first. Adding virtual boundary balloons `1` at both ends simplifies indexing.
**Code Skeleton:**
```python
def maxCoins(nums: list[int]) -> int:
    balloons = [1] + nums + [1]
    n = len(balloons)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):
        for left in range(0, n - length):
            right = left + length
            for i in range(left + 1, right):
                coins = balloons[left] * balloons[i] * balloons[right]
                coins += dp[left][i] + dp[i][right]
                dp[left][right] = max(dp[left][right], coins)
    return dp[0][n - 1]
```

---

### 14. LeetCode 174. Dungeon Game
**Archetype:** 14.1 Grid Path
**Type:** Core Drill
**Statement:** Given a dungeon grid where cells contain health changes, find the minimum initial health needed to rescue the princess at bottom-right.
**Why it fits:** Unlike standard grid DP where you start at top-left, here you work backwards from the princess. `dp[i][j]` = minimum health needed *before* entering cell `(i, j)` to survive to the end.
**The Twist:** The recurrence uses max with 1 to ensure health never drops to zero or below. Working backwards eliminates the exponential branching of forward DP.
**Code Skeleton:**
```python
def calculateMinimumHP(dungeon: list[list[int]]) -> int:
    m, n = len(dungeon), len(dungeon[0])
    dp = [[float('inf')] * (n + 1) for _ in range(m + 1)]
    dp[m][n - 1] = dp[m - 1][n] = 1  # Boundary condition
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            need = min(dp[i + 1][j], dp[i][j + 1]) - dungeon[i][j]
            dp[i][j] = max(1, need)
    return dp[0][0]
```

---

### 15. LeetCode 712. Minimum ASCII Delete Sum for Two Strings
**Archetype:** 14.3 LCS Variations
**Type:** Core Drill
**Statement:** Given two strings, find the lowest ASCII sum of deleted characters to make them equal.
**Why it fits:** Similar to Delete Operation for Two Strings, but instead of counting deletions, you sum ASCII values. The DP recurrence adds ASCII values on mismatch instead of adding 1.
**The Twist:** The base cases are not just indices — the first row and column must accumulate the ASCII sums of the prefixes because deleting an entire prefix is required to match an empty string.
**Code Skeleton:**
```python
def minimumDeleteSum(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        dp[i][0] = dp[i - 1][0] + ord(s1[i - 1])
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j - 1] + ord(s2[j - 1])
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + ord(s1[i - 1]),
                    dp[i][j - 1] + ord(s2[j - 1])
                )
    return dp[m][n]
```

---

## Checklist
- [ ] Can write LCS from scratch without looking
- [ ] Can distinguish 0/1 knapsack (backward loop) from unbounded (forward loop)
- [ ] Can explain why Coin Change 2 iterates coins outer for combinations
- [ ] Can reverse a grid DP (Dungeon Game)
- [ ] Can handle `*` in regex and wildcard matching DP transitions
