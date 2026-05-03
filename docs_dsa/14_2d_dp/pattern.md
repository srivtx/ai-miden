# Pattern 14: 2-D Dynamic Programming

> **Pattern Recognition:** When you see "grid", "matrix", "two strings", "edit distance", "LCS", "knapsack", "dungeon" — think 2-D DP.
>
> **Fundamental Insight:** When the state depends on two dimensions (e.g., position in grid, indices in two strings), use a 2-D table `dp[i][j]`. The answer is usually in the bottom-right cell.

---

## Archetype 14.1: Grid Path

### Recognition Signal
Words: **"unique paths", "min path sum", "grid", "robot", "obstacles"**

### Template
```python
def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[m-1][n-1]
```

**Space optimization:** Only need previous row.

```python
def unique_paths_optimized(m, n):
    dp = [1] * n
    for i in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j-1]
    return dp[n-1]
```

### Problems
- Unique Paths (LeetCode 62)
- Unique Paths II (LeetCode 63) — with obstacles
- Minimum Path Sum (LeetCode 64)
- Dungeon Game (LeetCode 174) — reverse DP
- Triangle (LeetCode 120)

---

## Archetype 14.2: Edit Distance

### Recognition Signal
Words: **"edit distance", "delete", "insert", "replace", "minimum operations"**

### Template
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
                dp[i][j] = 1 + min(dp[i-1][j],    # delete
                                   dp[i][j-1],    # insert
                                   dp[i-1][j-1])  # replace
    return dp[m][n]
```

### Problems
- Edit Distance (LeetCode 72)
- Delete Operation for Two Strings (LeetCode 583)
- Minimum ASCII Delete Sum for Two Strings (LeetCode 712)

---

## Archetype 14.3: LCS Variations

### Recognition Signal
Words: **"longest common subsequence", "LCS", "uncrossed lines", "max dot product"**

### Template
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

### Problems
- Longest Common Subsequence (LeetCode 1143)
- Uncrossed Lines (LeetCode 1035)
- Max Dot Product of Two Subsequences (LeetCode 1458)
- Shortest Common Supersequence (LeetCode 1092)

---

## Archetype 14.4: Knapsack (0/1)

### Recognition Signal
Words: **"knapsack", "subset sum", "partition", "target sum", "can be formed"**

### Template
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

**Key insight:** Iterate target backwards to prevent reusing same item.

### Problems
- Partition Equal Subset Sum (LeetCode 416)
- Target Sum (LeetCode 494)
- Ones and Zeroes (LeetCode 474) — 2D knapsack
- Last Stone Weight II (LeetCode 1049)

---

## Archetype 14.5: Knapsack (Unbounded)

### Recognition Signal
Words: **"coin change", "unlimited", "combination sum", "ways to make change"**

### Template
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for j in range(coin, amount + 1):
            dp[j] = min(dp[j], dp[j - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

**Key insight:** Iterate target forwards (unlimited reuse).

### Problems
- Coin Change (LeetCode 322)
- Coin Change 2 (LeetCode 518) — count ways
- Combination Sum IV (LeetCode 377) — permutations
- Perfect Squares (LeetCode 279)

---

## Archetype 14.6: Interval DP

### Recognition Signal
Words: **"burst balloons", "remove boxes", "strange printer", "matrix chain"**

The state depends on an interval [i, j], not a single index.

### Template
```python
def interval_dp(nums):
    n = len(nums)
    dp = [[0] * n for _ in range(n)]
    
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            # dp[i][j] = some function of dp[i][k] and dp[k+1][j]
    
    return dp[0][n-1]
```

### Problems
- Burst Balloons (LeetCode 312)
- Strange Printer (LeetCode 664)
- Minimum Cost Tree From Leaf Values (LeetCode 1130)

---

## Archetype 14.7: String Matching

### Recognition Signal
Words: **"regular expression", "wildcard matching", "is match", "pattern"**

### Problems
- Regular Expression Matching (LeetCode 10)
- Wildcard Matching (LeetCode 44)

---

## Mastery Checklist
- [ ] Grid path: unique paths, min path sum
- [ ] Edit distance: insert, delete, replace
- [ ] LCS: longest common subsequence
- [ ] 0/1 Knapsack: subset sum, partition
- [ ] Unbounded knapsack: coin change
- [ ] Interval DP: burst balloons
- [ ] Space optimization: 1D array instead of 2D

---

## Space Optimization Pattern

**2D to 1D:** If `dp[i][j]` only depends on previous row (`dp[i-1][...]`), use 1D array.

```python
# 2D
dp[i][j] = f(dp[i-1][j], dp[i][j-1])

# 1D
dp[j] = f(dp[j], dp[j-1])  # dp[j] is old dp[i-1][j], dp[j-1] is new dp[i][j-1]
```

---

## Common Traps

**Trap:** Forgetting to initialize base cases (first row/column).
- Fix: Initialize before nested loops.

**Trap:** Off-by-one in string DP (i-1 for character access).
- Fix: dp[i][j] represents first i characters of word1 and first j of word2.

**Trap:** Using forward iteration for 0/1 knapsack.
- Fix: 0/1 knapsack goes backwards. Unbounded goes forwards.

**Near Miss: Longest Palindromic Subsequence**
- Looks like LCS
- Actually LCS of string and its reverse
- Can also be solved with interval DP
