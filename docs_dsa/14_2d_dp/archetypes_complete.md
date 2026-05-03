# Pattern 14: 2-D DP — Complete Archetype Map

> **Pattern Recognition:** When you see "grid", "two strings", "edit distance", "knapsack", "interval", "burst balloons", "regex matching" — the state depends on two indices or dimensions. Brute force is exponential. A 2-D table turns it into polynomial time.
>
> **Fundamental Insight:** If the problem has optimal substructure and the state naturally has two dimensions (i, j), (row, col), (string index, pattern index), (weight, item), build a dp table where each cell represents the optimal answer for a subproblem defined by those two coordinates.

---

## Archetype 14.1: Grid Path

### Recognition Signal (10 seconds)
Words: **"grid", "path", "robot", "unique paths", "minimum path sum", "obstacles", "triangle", "falling"**

The question: **"Move from top-left to bottom-right (or top to bottom) with certain rules. Count ways or minimize/maximize sum."**

### Core Structure
```python
def grid_dp(grid):
    rows, cols = len(grid), len(grid[0])
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = grid[0][0]  # or 1 for counting paths
    
    for i in range(rows):
        for j in range(cols):
            if i > 0:
                dp[i][j] = combine(dp[i][j], dp[i-1][j])
            if j > 0:
                dp[i][j] = combine(dp[i][j], dp[i][j-1])
    return dp[rows-1][cols-1]
```

### The Invariant
`dp[i][j]` represents the optimal answer (max sum, min sum, or count of paths) to reach cell `(i, j)`. Every path to `(i, j)` must pass through either `(i-1, j)` or `(i, j-1)`, so the optimal substructure is guaranteed.

### Canonical Problem: Unique Paths (LeetCode 62)
**Statement:** A robot is located at the top-left corner of a `m x n` grid. The robot can only move down or right. How many possible unique paths are there?

```python
def unique_paths(m, n):
    # dp[i][j] = number of unique paths to reach cell (i, j)
    dp = [[0] * n for _ in range(m)]
    
    # Base case: first row and first column have exactly 1 path
    for i in range(m):
        dp[i][0] = 1
    for j in range(n):
        dp[0][j] = 1
    
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    
    return dp[m - 1][n - 1]
```

### Variation Family

**V1: Unique Paths II (LeetCode 63)**
- **Twist:** Grid contains obstacles marked as 1
- **Change:** If `grid[i][j] == 1`, set `dp[i][j] = 0`. Also check base cases for obstacles.
- **Key insight:** Obstacles break paths. Any cell with an obstacle contributes 0 paths.

```python
def unique_paths_with_obstacles(obstacle_grid):
    if not obstacle_grid or obstacle_grid[0][0] == 1:
        return 0
    
    rows, cols = len(obstacle_grid), len(obstacle_grid[0])
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = 1
    
    for i in range(rows):
        for j in range(cols):
            if obstacle_grid[i][j] == 1:
                dp[i][j] = 0
                continue
            if i > 0:
                dp[i][j] += dp[i - 1][j]
            if j > 0:
                dp[i][j] += dp[i][j - 1]
    
    return dp[rows - 1][cols - 1]
```

**V2: Minimum Path Sum (LeetCode 64)**
- **Twist:** Each cell has a cost. Find path from top-left to bottom-right with minimum sum.
- **Change:** `dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])`
- **Key insight:** Same grid structure, different recurrence (min instead of sum).

**V3: Triangle (LeetCode 120)**
- **Twist:** Triangle shape, move to adjacent numbers on the row below
- **Change:** `dp[i][j] = triangle[i][j] + min(dp[i+1][j], dp[i+1][j+1])` (bottom-up)
- **Key insight:** Work from bottom to top, or top to bottom with in-place modification.

**V4: Minimum Falling Path Sum (LeetCode 931)**
- **Twist:** Start anywhere in first row, end anywhere in last row. Move down-left, down, or down-right.
- **Change:** `dp[i][j] = matrix[i][j] + min(dp[i-1][j-1], dp[i-1][j], dp[i-1][j+1])` with boundary checks.
- **Key insight:** Same as grid path but with three predecessors and variable start/end.

**Near Miss: Word Search (LeetCode 79)**
- **Looks like:** Grid path
- **But:** Requires exploring all directions with backtracking. No optimal substructure because revisiting is not allowed.
- **Lesson:** When movement is unrestricted in 4 directions and cells cannot be reused, use DFS/backtracking, not DP.

---

## Archetype 14.2: Edit Distance

### Recognition Signal (10 seconds)
Words: **"edit distance", "insert", "delete", "replace", "minimum operations", "convert word1 to word2"**

The question: **"Transform one string into another using insert/delete/replace operations. Minimize operations."**

### Core Structure
```python
def edit_distance(s, t):
    dp = [[0] * (len(t) + 1) for _ in range(len(s) + 1)]
    
    # Base cases: transforming to/from empty string
    for i in range(len(s) + 1):
        dp[i][0] = i  # delete all characters
    for j in range(len(t) + 1):
        dp[0][j] = j  # insert all characters
    
    for i in range(1, len(s) + 1):
        for j in range(1, len(t) + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # no operation needed
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # delete
                    dp[i][j - 1],      # insert
                    dp[i - 1][j - 1]   # replace
                )
    return dp[len(s)][len(t)]
```

### The Invariant
`dp[i][j]` is the minimum edit distance between `s[0:i]` and `t[0:j]`. If the last characters match, we carry forward the previous distance. If they don't match, we consider the cheapest of the three possible operations.

### Canonical Problem: Edit Distance (LeetCode 72)
**Statement:** Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.

```python
def min_distance(word1, word2):
    m, n = len(word1), len(word2)
    # dp[i][j] = min operations to convert word1[0:i] to word2[0:j]
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
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    
    return dp[m][n]
```

### Variation Family

**V1: Delete Operation for Two Strings (LeetCode 583)**
- **Twist:** Only delete operations allowed. Find minimum deletions to make two strings equal.
- **Change:** `dp[i][j] = dp[i-1][j-1] + 1` if match, else `max(dp[i-1][j], dp[i][j-1])`. This is actually LCS in disguise. Answer = `len(s) + len(t) - 2 * LCS`.
- **Key insight:** What remains after deletions is the longest common subsequence.

**V2: Minimum ASCII Delete Sum for Two Strings (LeetCode 712)**
- **Twist:** Each deletion has a cost equal to the ASCII value of the deleted character.
- **Change:** Similar to edit distance but costs are character ASCII values.
- **Key insight:** Still LCS variant. Maximize ASCII sum of LCS, or directly minimize delete costs.

**V3: One Edit Distance (LeetCode 161)**
- **Twist:** Determine if two strings are exactly one edit distance apart.
- **Change:** Early termination check. If lengths differ by > 1, return False. Otherwise scan and count mismatches.
- **Key insight:** Don't need full DP table; a linear scan with pointer manipulation suffices for "exactly one."

**V4: Distinct Subsequences (LeetCode 115)**
- **Twist:** Count how many times `s` appears as a subsequence of `t`.
- **Change:** `dp[i][j] = dp[i-1][j-1] + dp[i-1][j]` if match, else `dp[i-1][j]`.
- **Key insight:** When characters match, we can either use this occurrence or skip it.

**Near Miss: Word Break (LeetCode 139)**
- **Looks like:** String transformation
- **But:** 1D DP. `dp[i]` = can we segment `s[0:i]` using dictionary words. No second string.
- **Lesson:** Edit distance requires TWO strings. Single-string problems are usually 1D.

---

## Archetype 14.3: LCS Variations

### Recognition Signal (10 seconds)
Words: **"longest common subsequence", "longest palindromic subsequence", "delete to make equal", "uncrossed lines"**

The question: **"Find the longest sequence common to two strings, or use LCS to derive another property."**

### Core Structure
```python
def lcs(s, t):
    dp = [[0] * (len(t) + 1) for _ in range(len(s) + 1)]
    
    for i in range(1, len(s) + 1):
        for j in range(1, len(t) + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[len(s)][len(t)]
```

### The Invariant
`dp[i][j]` stores the length of the LCS of `s[0:i]` and `t[0:j]`. If characters match, we extend the LCS by 1. If not, we take the best result from skipping either character.

### Canonical Problem: Longest Common Subsequence (LeetCode 1143)
**Statement:** Given two strings `text1` and `text2`, return the length of their longest common subsequence.

```python
def longest_common_subsequence(text1, text2):
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

### Variation Family

**V1: Longest Palindromic Subsequence (LeetCode 516)**
- **Twist:** Find longest palindromic subsequence in a single string
- **Change:** LCS of `s` and `reversed(s)`
- **Key insight:** A palindrome reads the same forwards and backwards.

```python
def longest_palindrome_subseq(s):
    return longest_common_subsequence(s, s[::-1])
```

**V2: Minimum Insertion Steps to Make a String Palindrome (LeetCode 1312)**
- **Twist:** Min insertions to make string a palindrome
- **Change:** Answer = `len(s) - LPS(s)` where LPS is longest palindromic subsequence
- **Key insight:** Characters not in the LPS must be mirrored.

**V3: Uncrossed Lines (LeetCode 1035)**
- **Twist:** Draw lines between equal numbers in two arrays without crossing
- **Change:** This is exactly LCS applied to integer arrays
- **Key insight:** "Uncrossed" means the relative order is preserved, which is the definition of a subsequence.

**V4: Shortest Common Supersequence (LeetCode 1092)**
- **Twist:** Find shortest string that has both strings as subsequences
- **Change:** Build from LCS table. Answer length = `len(s) + len(t) - LCS(s, t)`.
- **Key insight:** The supersequence includes all characters from both strings, sharing the LCS portion.

**Near Miss: Longest Palindromic Substring (LeetCode 5)**
- **Looks like:** Palindromic sequence
- **But:** Requires contiguous substring, not subsequence. Use expand-around-center or Manacher's algorithm.
- **Lesson:** Subsequence allows skipping; substring does not. The problems have very different solutions.

---

## Archetype 14.4: Knapsack (0/1)

### Recognition Signal (10 seconds)
Words: **"subset sum", "partition equal", "knapsack", "target sum", "each item once", "can you form"**

The question: **"Select a subset of items (each used at most once) to achieve a target (sum, count, or value)."**

### Core Structure
```python
def knapsack_01(weights, values, capacity):
    dp = [0] * (capacity + 1)
    
    for i in range(len(weights)):
        # Iterate BACKWARDS to ensure each item used at most once
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]
```

### The Invariant
`dp[w]` represents the maximum value achievable with capacity `w`. Iterating backwards ensures we don't reuse the current item in the same iteration. Each item is a binary choice: take it or leave it.

### Canonical Problem: Partition Equal Subset Sum (LeetCode 416)
**Statement:** Given an integer array `nums`, return `true` if you can partition the array into two subsets such that the sum of elements in both subsets is equal.

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False
    
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True
    
    for num in nums:
        # Iterate backwards: 0/1 knapsack constraint
        for w in range(target, num - 1, -1):
            dp[w] = dp[w] or dp[w - num]
    
    return dp[target]
```

### Variation Family

**V1: Target Sum (LeetCode 494)**
- **Twist:** Assign + or - to each number to reach target. Count ways.
- **Change:** Transform to subset sum. Let P = positive subset, N = negative subset. `P - N = target`, `P + N = total`. So `P = (target + total) / 2`. Count subsets summing to P.
- **Key insight:** Mathematical transformation turns sign assignment into subset sum.

**V2: Last Stone Weight II (LeetCode 1049)**
- **Twist:** Smash stones together. Minimize final weight.
- **Change:** Same as partition equal subset sum. Minimize `total - 2 * subset_sum` where `subset_sum <= total / 2`.
- **Key insight:** Smashing is equivalent to partitioning into two groups and taking the difference.

**V3: Ones and Zeroes (LeetCode 474)**
- **Twist:** 2D knapsack. Each item (string) has cost in 0s and 1s. Maximize number of items.
- **Change:** `dp[m][n] = max(dp[m][n], dp[m - zeros][n - ones] + 1)`
- **Key insight:** Multiple constraints extend naturally to multi-dimensional DP.

**V4: Profitable Schemes (LeetCode 879)**
- **Twist:** Count schemes with at least P profit and at most G members
- **Change:** 2D DP over profit and members. Count instead of max.
- **Key insight:** When counting valid combinations, DP stores counts rather than max values.

**Near Miss: Coin Change (LeetCode 322)**
- **Looks like:** Subset sum
- **But:** Unlimited supply of each coin. Requires unbounded knapsack (forward iteration).
- **Lesson:** The direction of the inner loop distinguishes 0/1 from unbounded knapsack.

---

## Archetype 14.5: Knapsack (Unbounded)

### Recognition Signal (10 seconds)
Words: **"unlimited coins", "complete knapsack", "ways to make change", "combinations", "coin change", "perfect squares"**

The question: **"Items can be reused unlimited times. Find min/max ways or value to reach target."**

### Core Structure
```python
def unbounded_knapsack(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for coin in coins:
        # Iterate FORWARDS because coins can be reused
        for w in range(coin, amount + 1):
            dp[w] = min(dp[w], dp[w - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1
```

### The Invariant
`dp[w]` represents the optimal answer for amount `w`. Forward iteration allows using the current coin multiple times because `dp[w - coin]` may have already been updated with the current coin in this same outer loop.

### Canonical Problem: Coin Change II (LeetCode 518)
**Statement:** You are given an integer array `coins` representing coins of different denominations and an integer `amount`. Return the number of combinations that make up that amount.

```python
def change(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1  # One way to make amount 0: use no coins
    
    for coin in coins:
        for w in range(coin, amount + 1):
            dp[w] += dp[w - coin]
    
    return dp[amount]
```

### Variation Family

**V1: Coin Change (LeetCode 322)**
- **Twist:** Minimum number of coins to make amount
- **Change:** `dp[w] = min(dp[w], dp[w - coin] + 1)`. Initialize with infinity.
- **Key insight:** Same structure, different aggregation function (min instead of sum).

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for w in range(coin, amount + 1):
            dp[w] = min(dp[w], dp[w - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

**V2: Combination Sum IV (LeetCode 377)**
- **Twist:** Permutations matter. Different orderings count as different combinations.
- **Change:** Swap loops: iterate amount outer, coins inner. `dp[w] += dp[w - coin]`.
- **Key insight:** Outer loop over amount considers all orderings; outer loop over coins considers combinations only.

**V3: Perfect Squares (LeetCode 279)**
- **Twist:** Min number of perfect square numbers that sum to n
- **Change:** Generate squares `[1, 4, 9, ...]` and run unbounded knapsack for min count.
- **Key insight:** Squares are the "coins," n is the "amount."

**V4: Form Largest Integer With Digits That Add up to Target (LeetCode 1449)**
- **Twist:** Digits have costs (mapping 1-9 to costs). Form largest number with exact target cost.
- **Change:** DP stores the longest string (or best numeric value) for each cost. Compare lexicographically.
- **Key insight:** Unbounded knapsack where the "value" is string comparison, not integer max.

**Near Miss: Combination Sum (LeetCode 39)**
- **Looks like:** Unbounded knapsack
- **But:** Requires listing all combinations, not just counting or minimizing. Use backtracking.
- **Lesson:** DP counts or optimizes; backtracking enumerates.

---

## Archetype 14.6: Interval DP

### Recognition Signal (10 seconds)
Words: **"burst balloons", "matrix chain multiplication", "remove boxes", "optimal binary search tree", "interval", "range dp"**

The question: **"Optimal answer for a range [i, j] depends on splitting at some point k in [i, j]."**

### Core Structure
```python
def interval_dp(arr):
    n = len(arr)
    dp = [[0] * n for _ in range(n)]
    
    for length in range(2, n + 1):  # length of interval
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j + 1):
                # Split at k and combine left and right subproblems
                left = dp[i][k - 1] if k > i else 0
                right = dp[k + 1][j] if k < j else 0
                dp[i][j] = max(dp[i][j], left + right + cost(arr, i, j, k))
    
    return dp[0][n - 1]
```

### The Invariant
`dp[i][j]` represents the optimal answer for the subarray `arr[i:j+1]`. We try every possible split point `k` within the interval. The optimal solution for `[i, j]` is derived from optimal solutions of `[i, k-1]` and `[k+1, j]` plus the cost of the split itself.

### Canonical Problem: Burst Balloons (LeetCode 312)
**Statement:** You are given `n` balloons, indexed from `0` to `n - 1`. Each balloon is painted with a number on it represented by an array `nums`. You are asked to burst all the balloons. If you burst the `i-th` balloon, you will get `nums[i - 1] * nums[i] * nums[i + 1]` coins. Return the maximum coins you can collect.

```python
def max_coins(nums):
    # Pad with 1 on both ends
    balloons = [1] + nums + [1]
    n = len(balloons)
    dp = [[0] * n for _ in range(n)]
    
    # length is the gap between left and right boundary
    for length in range(2, n):
        for left in range(n - length):
            right = left + length
            # Try bursting every balloon between left and right LAST
            for i in range(left + 1, right):
                coins = balloons[left] * balloons[i] * balloons[right]
                coins += dp[left][i] + dp[i][right]
                dp[left][right] = max(dp[left][right], coins)
    
    return dp[0][n - 1]
```

### Variation Family

**V1: Minimum Cost Tree From Leaf Values (LeetCode 1130)**
- **Twist:** Build binary tree from array. Non-leaf node value = max(left subtree) * max(right subtree). Minimize sum of non-leaf nodes.
- **Change:** `dp[i][j] = min(dp[i][k] + dp[k+1][j] + max(arr[i:k+1]) * max(arr[k+1:j+1]))`
- **Key insight:** Similar to matrix chain multiplication. Precompute max values for efficiency.

**V2: Guess Number Higher or Lower II (LeetCode 375)**
- **Twist:** Minimize worst-case cost in a guessing game
- **Change:** `dp[i][j] = min(k + max(dp[i][k-1], dp[k+1][j]))` for all k in [i, j]
- **Key insight:** We pay k if wrong, then face the worse of the two remaining intervals.

**V3: Minimum Cost to Merge Stones (LeetCode 1000)**
- **Twist:** Merge K consecutive piles into one. Cost = sum of those K piles.
- **Change:** 3D DP or 2D with prefix sums. `dp[i][j]` = min cost to merge `arr[i:j+1]` into as few piles as possible.
- **Key insight:** Interval DP with the additional constraint of merging exactly K piles at a time.

**V4: Predict the Winner (LeetCode 486)**
- **Twist:** Two players take turns picking from ends of array. Predict if first player wins.
- **Change:** `dp[i][j] = max(nums[i] - dp[i+1][j], nums[j] - dp[i][j-1])`
- **Key insight:** Interval DP where the state represents the score difference between current player and opponent.

**Near Miss: Non-overlapping Intervals (LeetCode 435)**
- **Looks like:** Interval problem
- **But:** Greedy by end time. No need for O(n^2) interval DP.
- **Lesson:** If the problem is just about selecting non-overlapping intervals, greedy is usually optimal and much faster.

---

## Archetype 14.7: String Matching

### Recognition Signal (10 seconds)
Words: **"regex matching", "wildcard matching", "regular expression", "is match", "interleaving string", "pattern matching"**

The question: **"Does string s match pattern p where p contains special characters like *, ?, ."**

### Core Structure
```python
def string_match(s, p):
    dp = [[False] * (len(p) + 1) for _ in range(len(s) + 1)]
    dp[0][0] = True
    
    # Initialize empty string vs pattern with *
    for j in range(1, len(p) + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]
    
    for i in range(1, len(s) + 1):
        for j in range(1, len(p) + 1):
            if p[j - 1] == '.' or p[j - 1] == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            elif p[j - 1] == '*':
                # Zero occurrences of preceding element
                dp[i][j] = dp[i][j - 2]
                # One or more occurrences
                if p[j - 2] == '.' or p[j - 2] == s[i - 1]:
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
    
    return dp[len(s)][len(p)]
```

### The Invariant
`dp[i][j]` indicates whether `s[0:i]` matches `p[0:j]`. Special characters create branching states: `.` matches any single character, `*` matches zero or more of the preceding element.

### Canonical Problem: Regular Expression Matching (LeetCode 10)
**Statement:** Given an input string `s` and a pattern `p`, implement regular expression matching with support for `.` and `*`. `.` matches any single character. `*` matches zero or more of the preceding element.

```python
def is_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    
    # Pattern like a*b*c* can match empty string
    for j in range(1, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '.' or p[j - 1] == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            elif p[j - 1] == '*':
                # Zero occurrences of char before *
                dp[i][j] = dp[i][j - 2]
                # One or more occurrences
                if p[j - 2] == '.' or p[j - 2] == s[i - 1]:
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
    
    return dp[m][n]
```

### Variation Family

**V1: Wildcard Matching (LeetCode 44)**
- **Twist:** Pattern contains `?` (matches any single char) and `*` (matches any sequence including empty)
- **Change:** `*` can match ANY sequence. `dp[i][j] = dp[i][j-1] or dp[i-1][j]` when `p[j-1] == '*'`.
- **Key insight:** `*` is more powerful here than in regex. It acts like a sequence wildcard, not repetition.

```python
def is_match_wildcard(s, p):
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
                # * matches empty sequence OR * matches s[i-1] and continues
                dp[i][j] = dp[i][j - 1] or dp[i - 1][j]
    
    return dp[m][n]
```

**V2: Interleaving String (LeetCode 97)**
- **Twist:** Is `s3` formed by interleaving `s1` and `s2` preserving relative order?
- **Change:** `dp[i][j] = (dp[i-1][j] and s1[i-1]==s3[i+j-1]) or (dp[i][j-1] and s2[j-1]==s3[i+j-1])`
- **Key insight:** 2D DP where dimensions are indices into s1 and s2.

**V3: Distinct Subsequences (LeetCode 115)**
- **Twist:** Count how many times `s` appears as a subsequence of `t`
- **Change:** Already covered in Edit Distance variations. `dp[i][j]` = count for `s[0:i]` in `t[0:j]`.
- **Key insight:** When characters match, add counts from both using and not using the character.

**V4: Word Break (LeetCode 139)**
- **Twist:** Can string be segmented into dictionary words?
- **Change:** 1D DP `dp[i] = any(dp[j] and s[j:i] in word_set for j in range(i))`
- **Key insight:** Not strictly 2D, but string matching against a set of patterns.

**Near Miss: Find the Index of the First Occurrence in a String (LeetCode 28)**
- **Looks like:** String matching
- **But:** Exact substring search. Built-in or KMP algorithm is O(n+m), not O(nm) DP.
- **Lesson:** When there are no special pattern characters, use KMP or Rabin-Karp, not DP.

---

## Pattern 14 Mastery Checklist

Before moving to Pattern 15, confirm you can:

- [ ] Grid path: fill dp[i][j] from top/left with obstacles and edge cases
- [ ] Edit distance: initialize base cases and handle insert/delete/replace
- [ ] LCS: write recurrence and reconstruct the actual sequence from the table
- [ ] 0/1 Knapsack: iterate weights BACKWARDS; explain why
- [ ] Unbounded Knapsack: iterate weights FORWARDS; explain why
- [ ] Interval DP: try every split point k in [i, j]; explain O(n^3) complexity
- [ ] String matching: handle `*`, `?`, `.` in patterns with proper base cases
- [ ] Distinguish: 0/1 vs unbounded knapsack (loop direction)
- [ ] Space optimize: reduce 2D table to 1D or rolling array when possible

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Wrong loop direction in knapsack | 0/1 items reused (unbounded behavior) | 0/1: iterate backwards; Unbounded: iterate forwards |
| Forgetting base cases in string matching | Empty string vs pattern `a*` gives wrong answer | Initialize `dp[0][j]` for patterns with `*` |
| Off-by-one in grid DP | Access `dp[-1]` or wrong indices | Careful with `dp[i-1][j-1]` vs `grid[i][j]` |
| Using O(n^3) interval DP when greedy works | TLE on large inputs | Check if greedy works for interval selection first |
| Not padding array in Burst Balloons | Boundary coins missing in calculation | Add virtual balloons with value 1 at both ends |
| Confusing substring vs subsequence | Wrong recurrence or wrong problem type | Substring = contiguous (expand around center); Subsequence = ordered but not contiguous (LCS) |

---

## Pattern Blends (What Comes Next)

2-D DP does not live in isolation. It blends with:

- **1-D DP:** Many 2-D problems can be space-optimized to 1-D (knapsack, edit distance with two rows)
- **Backtracking:** Reconstruct the actual solution path from the DP table (e.g., shortest common supersequence)
- **Greedy:** Some interval problems look like interval DP but are actually greedy (non-overlapping intervals)
- **Bit Manipulation:** State compression DP uses bitmasks to represent subsets in one dimension
- **Math:** Number theory problems (e.g., GCD/LCM) sometimes need DP for counting

---

*Next: Pattern 15 — Greedy*
