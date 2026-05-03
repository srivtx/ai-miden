# Pattern 14: 2-D DP — Drills Part 3

> **5 Near Misses + 5 Pattern Blends + 5 Interview Simulation**
> Focus: Recognize 2-D DP when disguised as other problems, and blend it with additional constraints.

---

## Near Misses

### 1. LeetCode 120. Triangle
**Archetype:** 14.1 Grid Path
**Type:** Near Miss
**Statement:** Given a triangle array, find the minimum path sum from top to bottom where you can only move to adjacent numbers on the row below.
**Why it fits:** It looks like a grid path problem but the triangular structure makes the indexing tricky. `dp[i][j]` = min path sum to reach row `i`, column `j`.
**The Twist:** You can solve it bottom-up with O(n) space by modifying the triangle in-place. The near miss is trying to allocate a full 2-D table when the input is already jagged.
**Code Skeleton:**
```python
def minimumTotal(triangle: list[list[int]]) -> int:
    # Bottom-up in-place on a copy of the last row
    dp = triangle[-1][:]
    for row in range(len(triangle) - 2, -1, -1):
        for col in range(len(triangle[row])):
            dp[col] = triangle[row][col] + min(dp[col], dp[col + 1])
    return dp[0]
```

---

### 2. LeetCode 1049. Last Stone Weight II
**Archetype:** 14.4 Knapsack 0/1
**Type:** Near Miss
**Statement:** Given an array of stone weights, repeatedly smash two stones together. Return the smallest possible weight of the last stone.
**Why it fits:** The problem hides a 0/1 knapsack. Smashing stones `a` and `b` produces `|a - b|`, which is equivalent to partitioning stones into two groups with minimum sum difference. This is exactly Partition Equal Subset Sum with a different story.
**The Twist:** The stones do not disappear — they transform. Recognizing that the final weight equals `abs(sum(group1) - sum(group2))` is the key reduction.
**Code Skeleton:**
```python
def lastStoneWeightII(stones: list[int]) -> int:
    total = sum(stones)
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True
    for stone in stones:
        for t in range(target, stone - 1, -1):
            dp[t] = dp[t] or dp[t - stone]
    # Find largest achievable sum <= target
    for t in range(target, -1, -1):
        if dp[t]:
            return total - 2 * t
    return 0
```

---

### 3. LeetCode 377. Combination Sum IV
**Archetype:** 14.5 Knapsack Unbounded
**Type:** Near Miss
**Statement:** Given distinct integers and a target, return the number of possible combinations that add up to target. Different sequences count as different combinations.
**Why it fits:** This is Coin Change 2 but with permutations instead of combinations. Swapping the loop order (amounts outer, coins inner) turns a combination counter into a permutation counter.
**The Twist:** The order of elements matters. This changes the DP from unbounded knapsack combinations to a pure 1-D DP where each amount builds on all previous amounts using any coin.
**Code Skeleton:**
```python
def combinationSum4(nums: list[int], target: int) -> int:
    dp = [0] * (target + 1)
    dp[0] = 1
    for t in range(1, target + 1):
        for num in nums:
            if t >= num:
                dp[t] += dp[t - num]
    return dp[target]
```

---

### 4. LeetCode 1092. Shortest Common Supersequence
**Archetype:** 14.3 LCS Variations
**Type:** Near Miss
**Statement:** Given two strings, return the shortest string that has both strings as subsequences.
**Why it fits:** The answer is built from the LCS of the two strings. Characters in the LCS appear once; non-LCS characters from both strings are appended around the LCS in order.
**The Twist:** You must reconstruct the actual string, not just return its length. This requires backtracking through the LCS DP table while preserving the order of non-matching characters from both inputs.
**Code Skeleton:**
```python
def shortestCommonSupersequence(str1: str, str2: str) -> str:
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # Backtrack to build SCS
    i, j = m, n
    result = []
    while i > 0 and j > 0:
        if str1[i - 1] == str2[j - 1]:
            result.append(str1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            result.append(str1[i - 1])
            i -= 1
        else:
            result.append(str2[j - 1])
            j -= 1
    while i > 0:
        result.append(str1[i - 1])
        i -= 1
    while j > 0:
        result.append(str2[j - 1])
        j -= 1
    return ''.join(reversed(result))
```

---

### 5. LeetCode 1130. Minimum Cost Tree From Leaf Values
**Archetype:** 14.6 Interval DP
**Type:** Near Miss
**Statement:** Given an array of positive integers, build a binary tree where each non-leaf node value is the product of the largest leaf in each subtree. Minimize the sum of non-leaf node values.
**Why it fits:** `dp[i][j]` = min cost to build a tree from `arr[i..j]`. For each split point `k`, cost = `dp[i][k] + dp[k+1][j] + max(arr[i..k]) * max(arr[k+1..j])`.
**The Twist:** The leaf values are fixed; only the pairing order changes. Precomputing range maximums with a sparse table or simple array lookups is essential for O(n^3) to be acceptable.
**Code Skeleton:**
```python
def mctFromLeafValues(arr: list[int]) -> int:
    n = len(arr)
    # max_val[i][j] = max in arr[i..j]
    max_val = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            max_val[i][j] = max(arr[i:j + 1])
    
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                left = dp[i][k] if k > i else 0
                right = dp[k + 1][j] if k + 1 < j else 0
                cost = left + right + max_val[i][k] * max_val[k + 1][j]
                dp[i][j] = min(dp[i][j], cost)
    return dp[0][n - 1]
```

---

## Pattern Blends

### 6. LeetCode 474. Ones and Zeroes
**Archetype:** 14.4 Knapsack 0/1 + 2 Constraints
**Type:** Pattern Blend
**Statement:** Given an array of binary strings and integers m, n, find the maximum number of strings that can be formed with at most m 0s and n 1s.
**Why it fits:** This is 0/1 knapsack with two capacities instead of one. `dp[i][j]` = max subset size using `i` zeros and `j` ones. Each string can be chosen at most once.
**The Twist:** The two-dimensional capacity table is a direct extension of 1-D knapsack. Iterating both capacities backwards prevents reusing the same string.
**Code Skeleton:**
```python
def findMaxForm(strs: list[str], m: int, n: int) -> int:
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for s in strs:
        zeros = s.count('0')
        ones = len(s) - zeros
        for i in range(m, zeros - 1, -1):
            for j in range(n, ones - 1, -1):
                dp[i][j] = max(dp[i][j], dp[i - zeros][j - ones] + 1)
    return dp[m][n]
```

---

### 7. LeetCode 516. Longest Palindromic Subsequence
**Archetype:** 14.3 LCS + 14.6 Interval DP
**Type:** Pattern Blend
**Statement:** Given a string, find the length of the longest palindromic subsequence.
**Why it fits:** It can be solved as LCS of the string and its reverse (14.3), or as interval DP where `dp[i][j]` = LPS of substring `s[i..j]` (14.6). Both are valid and teach different perspectives.
**The Twist:** The interval DP approach is more elegant for reconstruction. If `s[i] == s[j]`, add 2 to `dp[i+1][j-1]`; otherwise take `max(dp[i+1][j], dp[i][j-1])`.
**Code Skeleton:**
```python
def longestPalindromeSubseq(s: str) -> int:
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = 2 + dp[i + 1][j - 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]
```

---

### 8. LeetCode 1312. Minimum Insertion Steps to Make a String Palindrome
**Archetype:** 14.3 LCS / 14.6 Interval DP
**Type:** Pattern Blend
**Statement:** Return the minimum number of insertions needed to make a string a palindrome.
**Why it fits:** The answer is `len(s) - LPS(s)`. Finding the LPS can be done via LCS with reverse (14.3) or interval DP (14.6). This blends string DP with palindrome properties.
**The Twist:** Insertions are equivalent to adding the missing characters from the reverse string. The minimum insertions correspond to characters not in the longest palindromic subsequence.
**Code Skeleton:**
```python
def minInsertions(s: str) -> int:
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = 2 + dp[i + 1][j - 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return n - dp[0][n - 1]
```

---

### 9. LeetCode 1035. Uncrossed Lines
**Archetype:** 14.3 LCS in Disguise
**Type:** Pattern Blend
**Statement:** Draw lines between equal numbers in two arrays such that lines do not cross. Find the maximum number of lines.
**Why it fits:** The non-crossing constraint is exactly the definition of a common subsequence. This problem is literally LCS with a different narrative.
**The Twist:** The problem never uses the words "subsequence" or "common." You must recognize that connecting equal numbers without crossing preserves relative order, which is the definition of a subsequence.
**Code Skeleton:**
```python
def maxUncrossedLines(nums1: list[int], nums2: list[int]) -> int:
    m, n = len(nums1), len(nums2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if nums1[i - 1] == nums2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

---

### 10. LeetCode 87. Scramble String
**Archetype:** 14.2 Edit Distance + Recursion / 14.7 String Matching
**Type:** Pattern Blend
**Statement:** Given two strings, determine if one is a scrambled string of the other (recursively swap children of binary tree partitions).
**Why it fits:** `dp[i][j][len]` = is `s1[i:i+len]` a scramble of `s2[j:j+len]`? This is a 3-D DP over string intervals with a recursive decomposition condition.
**The Twist:** For each partition length `k`, you must check both the straight match and the swapped match. This makes the transition O(n) per state, leading to O(n^4) overall.
**Code Skeleton:**
```python
def isScramble(s1: str, s2: str) -> bool:
    n = len(s1)
    if n != len(s2) or sorted(s1) != sorted(s2):
        return False
    # dp[i][j][l] = True if s1[i:i+l] is a scramble of s2[j:j+l]
    dp = [[[False] * (n + 1) for _ in range(n)] for __ in range(n)]
    for i in range(n):
        for j in range(n):
            dp[i][j][1] = (s1[i] == s2[j])
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            for j in range(n - length + 1):
                for k in range(1, length):
                    if (dp[i][j][k] and dp[i + k][j + k][length - k]) or \
                       (dp[i][j + length - k][k] and dp[i + k][j][length - k]):
                        dp[i][j][length] = True
                        break
    return dp[0][0][n]
```

---

## Interview Simulation

### 11. LeetCode 1458. Max Dot Product of Two Subsequences
**Archetype:** 14.3 LCS + Signed Values
**Type:** Interview Sim
**Statement:** Given two arrays, find the max dot product of two non-empty subsequences of the same length.
**Why it fits:** Similar to LCS but instead of maximizing length, you maximize the sum of products. The recurrence must handle negative products by allowing skipping even if the current product is positive.
**The Twist:** Negative numbers complicate the recurrence because a large negative product might be necessary to set up a future large positive product. You cannot simply greedily skip negative pairwise products.
**Code Skeleton:**
```python
def maxDotProduct(nums1: list[int], nums2: list[int]) -> int:
    m, n = len(nums1), len(nums2)
    dp = [[float('-inf')] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            product = nums1[i - 1] * nums2[j - 1]
            dp[i][j] = max(
                product,
                dp[i - 1][j],
                dp[i][j - 1],
                dp[i - 1][j - 1] + product,
                dp[i - 1][j - 1]
            )
    return dp[m][n]
```

---

### 12. LeetCode 1235. Maximum Profit in Job Scheduling
**Archetype:** 14.1 Grid Path + Binary Search / 14.6 Feel
**Type:** Interview Sim
**Statement:** Given jobs with start time, end time, and profit, find the max profit subset of non-overlapping jobs.
**Why it fits:** Sort jobs by end time. `dp[i]` = max profit using first `i` jobs. For each job, binary search the last non-conflicting job. This blends 1-D DP with binary search for efficient transition.
**The Twist:** The state transition is not just `dp[i-1]`; it requires a binary search to find `dp[j]` where `job[j].end <= job[i].start`. This is a classic weighted interval scheduling problem.
**Code Skeleton:**
```python
def jobScheduling(startTime: list[int], endTime: list[int], profit: list[int]) -> int:
    jobs = sorted(zip(endTime, startTime, profit))
    n = len(jobs)
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        end, start, prof = jobs[i - 1]
        # Binary search for last job that ends <= start
        lo, hi = 0, i - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if jobs[mid - 1][0] <= start:
                lo = mid
            else:
                hi = mid - 1
        include = prof + dp[lo]
        exclude = dp[i - 1]
        dp[i] = max(include, exclude)
    return dp[n]
```

---

### 13. LeetCode 1787. Make the XOR of All Segments Equal to Zero
**Archetype:** 14.4 Knapsack + XOR State
**Type:** Interview Sim
**Statement:** Given an array and integer k, change elements so that the XOR of every contiguous subarray of length k equals 0. Return the minimum number of changes.
**Why it fits:** Elements at positions `i, i+k, i+2k...` must all be equal in the final array. For each residue class mod k, you choose a target value. The cost is the number of changes. This is a multi-set knapsack over XOR values.
**The Twist:** The state is an XOR value (0..1023) rather than a sum. The DP tracks the minimum changes to achieve each possible XOR for the processed residue classes.
**Code Skeleton:**
```python
def minChanges(nums: list[int], k: int) -> int:
    from collections import Counter
    n = len(nums)
    groups = [Counter() for _ in range(k)]
    for i, num in enumerate(nums):
        groups[i % k][num] += 1
    
    INF = float('inf')
    dp = [INF] * 1024
    dp[0] = 0
    for i in range(k):
        size = (n - i + k - 1) // k  # number of elements in this group
        min_prev = min(dp)
        new_dp = [min_prev + size] * 1024  # change all elements in group
        for xor_val in range(1024):
            if dp[xor_val] == INF:
                continue
            for num, freq in groups[i].items():
                new_dp[xor_val ^ num] = min(new_dp[xor_val ^ num], dp[xor_val] + size - freq)
        dp = new_dp
    return dp[0]
```

---

### 14. LeetCode 664. Strange Printer
**Archetype:** 14.6 Interval DP + String Compression
**Type:** Interview Sim
**Statement:** A strange printer can print a sequence of the same character in one turn, starting and ending at any position. Find the minimum turns needed to print a string.
**Why it fits:** `dp[i][j]` = min turns to print `s[i..j]`. If `s[i] == s[k]` for some `k` in `(i, j]`, you can print `s[i]` together with `s[k]`, saving a turn. This is interval DP with a matching optimization.
**The Twist:** The printer overwrites, so printing `s[i]` across the interval and then filling in the gaps is valid. The interval DP must account for matching characters that allow turn-sharing.
**Code Skeleton:**
```python
def strangePrinter(s: str) -> int:
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            dp[i][j] = dp[i][j - 1] + 1
            for k in range(i, j):
                if s[k] == s[j]:
                    dp[i][j] = min(dp[i][j], dp[i][k] + dp[k + 1][j - 1])
    return dp[0][n - 1]
```

---

### 15. LeetCode 97. Interleaving String
**Archetype:** 14.3 / 14.7 String Matching Variant
**Type:** Interview Sim
**Statement:** Given strings s1, s2, and s3, determine if s3 is formed by interleaving s1 and s2.
**Why it fits:** `dp[i][j]` = can `s3[0:i+j]` be formed by interleaving `s1[0:i]` and `s2[0:j]`? The recurrence checks if the next character of s3 matches the next character of s1 or s2.
**The Twist:** The index into s3 is derived from `i + j`, so the table is 2-D even though three strings are involved. Space can be optimized to 1-D because each row only depends on the previous row.
**Code Skeleton:**
```python
def isInterleave(s1: str, s2: str, s3: str) -> bool:
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    dp = [False] * (n + 1)
    dp[0] = True
    for j in range(1, n + 1):
        dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]
    for i in range(1, m + 1):
        dp[0] = dp[0] and s1[i - 1] == s3[i - 1]
        for j in range(1, n + 1):
            dp[j] = (dp[j] and s1[i - 1] == s3[i + j - 1]) or \
                    (dp[j - 1] and s2[j - 1] == s3[i + j - 1])
    return dp[n]
```

---

## Checklist
- [ ] Can recognize 0/1 knapsack in story problems (Last Stone Weight II)
- [ ] Can build 3-D DP when intervals plus length are needed (Scramble String)
- [ ] Can blend binary search with 1-D/2-D DP (Job Scheduling)
- [ ] Can handle non-standard state spaces like XOR (Make XOR Zero)
- [ ] Can reconstruct strings from LCS/Edit Distance tables
