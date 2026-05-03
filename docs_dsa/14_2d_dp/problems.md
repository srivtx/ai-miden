# Pattern 14: 2-D DP — Practice Problems

## Grid Path

### 62. Unique Paths
**Statement:** Paths from top-left to bottom-right.
**Code:**
```python
def unique_paths(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j-1]
    return dp[-1]
```

### 63. Unique Paths II
**Statement:** With obstacles.
**Intuition:** If obstacle, dp[j] = 0.

### 64. Minimum Path Sum
**Statement:** Min sum path in grid.
**Intuition:** dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1]).

### 174. Dungeon Game
**Statement:** Min initial health to rescue princess.
**Intuition:** Reverse DP. dp[i][j] = min health needed from (i,j) to end.

### 120. Triangle
**Statement:** Min path sum from top to bottom.
**Intuition:** Bottom-up. dp[i][j] = triangle[i][j] + min(dp[i+1][j], dp[i+1][j+1]).

---

## Edit Distance

### 72. Edit Distance
**Statement:** Min operations to convert word1 to word2.
**Code:**
```python
def min_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[m][n]
```

### 583. Delete Operation for Two Strings
**Statement:** Min deletions to make two strings equal.
**Intuition:** m + n - 2 * LCS.

### 712. Minimum ASCII Delete Sum for Two Strings
**Statement:** Min ASCII sum of deleted characters.
**Intuition:** Similar to edit distance. Cost is ASCII value.

---

## LCS

### 1143. Longest Common Subsequence
**Statement:** LCS of two strings.
**Code:**
```python
def longest_common_subsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = 1 + dp[i-1][j-1]
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```

### 1035. Uncrossed Lines
**Statement:** Max uncrossed lines between two arrays.
**Intuition:** Same as LCS.

### 1092. Shortest Common Supersequence
**Statement:** Shortest string containing both as subsequences.
**Intuition:** Build from LCS table.

---

## Knapsack

### 416. Partition Equal Subset Sum
**Statement:** Can array be partitioned into two equal sum subsets?
**Code:**
```python
def can_partition(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True
    for num in nums:
        for j in range(target, num - 1, -1):
            dp[j] = dp[j] or dp[j - num]
    return dp[target]
```

### 494. Target Sum
**Statement:** Ways to assign + or - to reach target.
**Intuition:** subset sum. (sum - target) / 2 must be achievable.

### 322. Coin Change
**Statement:** Fewest coins to make amount.
**Intuition:** Unbounded knapsack. Forward iteration.
**Code:**
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for j in range(coin, amount + 1):
            dp[j] = min(dp[j], dp[j - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

### 518. Coin Change 2
**Statement:** Number of ways to make amount.
**Intuition:** dp[j] += dp[j - coin]. Order of loops matters.

### 377. Combination Sum IV
**Statement:** Number of permutations to make target.
**Intuition:** Outer loop on target, inner on coins (opposite of Coin Change 2).

---

## Interval DP

### 312. Burst Balloons
**Statement:** Max coins by bursting balloons.
**Intuition:** dp[i][j] = max coins from bursting all in (i,j). Try each k as last to burst.

### 664. Strange Printer
**Statement:** Min turns to print string.
**Intuition:** dp[i][j] = min turns for s[i:j+1]. If s[i] == s[k], can print together.

---

## String Matching

### 10. Regular Expression Matching
**Statement:** Match string with pattern (. and *).
**Intuition:** dp[i][j] = first i chars of s match first j of p.

### 44. Wildcard Matching
**Statement:** Match with ? and *.
**Intuition:** ? matches one char. * matches any sequence.

---

## Mixed Drill Set

1. 62 — Unique paths
2. 72 — Edit distance
3. 1143 — LCS
4. 416 — Partition equal subset
5. 322 — Coin change
6. 312 — Burst balloons
7. 64 — Min path sum
8. 10 — Regex matching
9. 494 — Target sum
10. 174 — Dungeon game
11. 120 — Triangle
12. 518 — Coin change 2
