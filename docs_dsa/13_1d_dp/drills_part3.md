# Pattern 13: 1-D DP — Drills Part 3

> **5 Near Misses + 5 Pattern Blends + 5 Interview Simulation**
> Focus: Recognize 1-D DP when the problem is disguised or mixed with other patterns.

---

## Near Misses

### 1. LeetCode 55. Jump Game
**Archetype:** 13.2 Climbing/Jump
**Type:** Near Miss
**Statement:** Given max jump length from each position, determine if you can reach the last index.
**Why it fits:** It uses the same reachability idea as Jump Game II, but here greedy outcompetes DP. The "near miss" is that beginners often write an O(n^2) DP when a single greedy pass suffices.
**The Twist:** You do not need the minimum number of jumps — just feasibility. A single `farthest` variable updated greedily solves it in O(n).
**Code Skeleton:**
```python
def canJump(nums: list[int]) -> bool:
    farthest = 0
    for i, jump in enumerate(nums):
        if i > farthest:
            return False
        farthest = max(farthest, i + jump)
    return True
```

---

### 2. LeetCode 413. Arithmetic Slices
**Archetype:** 13.5 Counting Ways
**Type:** Near Miss
**Statement:** Count the number of arithmetic subarrays (at least 3 elements with constant difference).
**Why it fits:** `dp[i]` = number of arithmetic slices ending at index `i`. The recurrence is `dp[i] = dp[i-1] + 1` if the current triplet continues the pattern, else `0`. It looks like a count but the recurrence is linear and additive.
**The Twist:** The recurrence only activates when `nums[i] - nums[i-1] == nums[i-1] - nums[i-2]`. Otherwise it resets to zero, making it a conditional counting DP.
**Code Skeleton:**
```python
def numberOfArithmeticSlices(nums: list[int]) -> int:
    n = len(nums)
    if n < 3:
        return 0
    total = 0
    current = 0
    for i in range(2, n):
        if nums[i] - nums[i - 1] == nums[i - 1] - nums[i - 2]:
            current += 1
            total += current
        else:
            current = 0
    return total
```

---

### 3. LeetCode 376. Wiggle Subsequence
**Archetype:** 13.6 LIS
**Type:** Near Miss
**Statement:** Find the length of the longest wiggle subsequence where differences between successive numbers strictly alternate between positive and negative.
**Why it fits:** It resembles LIS but the ordering constraint alternates. You track two states: `up` = longest wiggle ending with an up-step, `down` = longest ending with a down-step. This introduces dual-state 1-D DP.
**The Twist:** There is no binary search optimization because the sequence is not monotonic. The simple O(n) dual-state DP is optimal and cleaner than a full LIS formulation.
**Code Skeleton:**
```python
def wiggleMaxLength(nums: list[int]) -> int:
    if len(nums) < 2:
        return len(nums)
    up = down = 1
    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            up = down + 1
        elif nums[i] < nums[i - 1]:
            down = up + 1
        # If equal, both states stay unchanged
    return max(up, down)
```

---

### 4. LeetCode 714. Best Time to Buy and Sell Stock with Transaction Fee
**Archetype:** 13.7 State Machine / 13.4 Stock Problems
**Type:** Near Miss
**Statement:** Maximize profit with unlimited transactions, but each sale incurs a fixed fee.
**Why it fits:** This is a stock state machine with a cost on the `sold` transition. It looks like the cooldown problem but the fee penalizes selling rather than forcing a wait.
**The Twist:** The fee is deducted on sell, not on buy. This changes the `sold` recurrence to `hold[i-1] + price - fee` instead of `hold[i-1] + price`.
**Code Skeleton:**
```python
def maxProfit(prices: list[int], fee: int) -> int:
    # cash = max profit on day i with no stock
    # hold = max profit on day i with stock
    cash, hold = 0, -prices[0]
    for price in prices[1:]:
        cash = max(cash, hold + price - fee)
        hold = max(hold, cash - price)
    return cash
```

---

### 5. LeetCode 264. Ugly Number II
**Archetype:** 13.5 Counting Ways
**Type:** Near Miss
**Statement:** Find the nth ugly number (positive integer whose prime factors are limited to 2, 3, 5).
**Why it fits:** The sequence is built by multiplying previous ugly numbers by 2, 3, or 5. Three pointers track the next candidate for each prime. It is a multi-pointer DP rather than a simple recurrence.
**The Twist:** Three interleaved sequences merge into one sorted stream. Using three indices instead of one makes the state management more complex than standard 1-D counting DP.
**Code Skeleton:**
```python
def nthUglyNumber(n: int) -> int:
    ugly = [1] * n
    i2 = i3 = i5 = 0
    for i in range(1, n):
        next2, next3, next5 = 2 * ugly[i2], 3 * ugly[i3], 5 * ugly[i5]
        ugly[i] = min(next2, next3, next5)
        if ugly[i] == next2:
            i2 += 1
        if ugly[i] == next3:
            i3 += 1
        if ugly[i] == next5:
            i5 += 1
    return ugly[n - 1]
```

---

## Pattern Blends

### 6. LeetCode 123. Best Time to Buy and Sell Stock III
**Archetype:** 13.4 Stock Problems + 13.7 State Machine
**Type:** Pattern Blend
**Statement:** Maximize profit with at most two transactions.
**Why it fits:** It is exactly Stock IV with `k=2`, but solved more elegantly with four variables: `first_buy`, `first_sell`, `second_buy`, `second_sell`. This blends state machine reasoning with explicit transaction tracking.
**The Twist:** Because `k` is tiny, you can flatten the DP arrays into scalar variables. This is a common interview optimization: when k is bounded by a small constant, unroll the loops.
**Code Skeleton:**
```python
def maxProfit(prices: list[int]) -> int:
    first_buy = second_buy = float('-inf')
    first_sell = second_sell = 0
    for price in prices:
        first_buy = max(first_buy, -price)
        first_sell = max(first_sell, first_buy + price)
        second_buy = max(second_buy, first_sell - price)
        second_sell = max(second_sell, second_buy + price)
    return second_sell
```

---

### 7. LeetCode 1048. Longest String Chain
**Archetype:** 13.6 LIS + Hashing
**Type:** Pattern Blend
**Statement:** Given an array of words, find the longest chain where each word is a predecessor of the next (one letter inserted anywhere).
**Why it fits:** After sorting by length, this becomes LIS on strings where `wordA` is a predecessor of `wordB`. A hash map stores the best chain length for each word, turning the predecessor check into O(L) per word.
**The Twist:** The predecessor relation is not a simple numeric comparison. You must generate all possible predecessors by deleting one character at a time, then look them up in a dictionary.
**Code Skeleton:**
```python
def longestStrChain(words: list[str]) -> int:
    words.sort(key=len)
    dp = {}
    max_len = 1
    for word in words:
        dp[word] = 1
        for i in range(len(word)):
            predecessor = word[:i] + word[i+1:]
            if predecessor in dp:
                dp[word] = max(dp[word], dp[predecessor] + 1)
        max_len = max(max_len, dp[word])
    return max_len
```

---

### 8. LeetCode 368. Largest Divisible Subset
**Archetype:** 13.6 LIS + Number Theory
**Type:** Pattern Blend
**Statement:** Given a set of distinct positive integers, return the largest subset such that every pair `(Si, Sj)` satisfies `Si % Sj == 0` or `Sj % Si == 0`.
**Why it fits:** Sort the array, then `dp[i]` = size of largest divisible subset ending at `i`. For each pair `(j, i)` where `nums[i] % nums[j] == 0`, extend the subset. This is LIS with a modular divisibility predicate instead of `<`.
**The Twist:** You must also reconstruct the actual subset, not just its length. This requires tracking a parent pointer array alongside the DP table.
**Code Skeleton:**
```python
def largestDivisibleSubset(nums: list[int]) -> list[int]:
    if not nums:
        return []
    nums.sort()
    n = len(nums)
    dp = [1] * n
    parent = [-1] * n
    max_idx = 0
    for i in range(n):
        for j in range(i):
            if nums[i] % nums[j] == 0 and dp[i] < dp[j] + 1:
                dp[i] = dp[j] + 1
                parent[i] = j
        if dp[i] > dp[max_idx]:
            max_idx = i
    # Reconstruct subset
    result = []
    while max_idx != -1:
        result.append(nums[max_idx])
        max_idx = parent[max_idx]
    return result[::-1]
```

---

### 9. LeetCode 790. Domino and Tromino Tiling
**Archetype:** 13.5 Counting Ways + Recurrence Design
**Type:** Pattern Blend
**Statement:** Count ways to tile a 2 x n board with dominoes (2x1) and trominoes (L-shaped).
**Why it fits:** The recurrence involves three states: fully tiled, top row protruding by one, bottom row protruding by one. This extends simple Fibonacci counting into a 3-state linear recurrence.
**The Twist:** The L-shaped tromino creates asymmetric states that must be tracked separately. The recurrence is `dp[i] = 2*dp[i-1] + dp[i-3]`, which is not obvious without drawing state transitions.
**Code Skeleton:**
```python
def numTilings(n: int) -> int:
    MOD = 10**9 + 7
    if n <= 2:
        return n
    # dp[i][0] = fully covered up to column i
    # dp[i][1] = top cell of column i+1 is covered (bottom protrudes)
    # dp[i][2] = bottom cell of column i+1 is covered (top protrudes)
    dp = [[0, 0, 0] for _ in range(n + 1)]
    dp[0][0] = 1
    dp[1][0] = 1
    for i in range(2, n + 1):
        dp[i][0] = (dp[i-1][0] + dp[i-2][0] + dp[i-1][1] + dp[i-1][2]) % MOD
        dp[i][1] = (dp[i-2][0] + dp[i-1][2]) % MOD
        dp[i][2] = (dp[i-2][0] + dp[i-1][1]) % MOD
    return dp[n][0]
```

---

### 10. LeetCode 279. Perfect Squares
**Archetype:** 13.5 Counting Ways + BFS Disguise
**Type:** Pattern Blend
**Statement:** Given n, find the least number of perfect square numbers that sum to n.
**Why it fits:** `dp[i]` = min squares to sum to `i`. For each `i`, try all square numbers `<= i` and take `1 + dp[i - square]`. This is unbounded knapsack (1-D DP) on square numbers.
**The Twist:** Lagrange's four-square theorem guarantees the answer is at most 4, but the DP solution is the expected interview answer. The BFS solution is also valid and sometimes preferred.
**Code Skeleton:**
```python
def numSquares(n: int) -> int:
    dp = [float('inf')] * (n + 1)
    dp[0] = 0
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], dp[i - j * j] + 1)
            j += 1
    return dp[n]
```

---

## Interview Simulation

### 11. LeetCode 256. Paint House
**Archetype:** 13.7 State Machine
**Type:** Interview Sim
**Statement:** Paint a row of houses such that no two adjacent houses have the same color, minimizing total cost. Three colors available.
**Why it fits:** For each house, you track the min cost to paint it red, blue, or green based on the previous house's costs. This is a small, fixed-size state machine.
**The Twist:** The number of colors is small and fixed, so you can use three variables instead of arrays. Interviewers often extend this to `k` colors (Paint House II), forcing an O(n*k) solution with optimization to O(n*k) using min tracking.
**Code Skeleton:**
```python
def minCost(costs: list[list[int]]) -> int:
    if not costs:
        return 0
    # costs[i][0]=red, [1]=blue, [2]=green
    prev_red, prev_blue, prev_green = costs[0]
    for i in range(1, len(costs)):
        red = costs[i][0] + min(prev_blue, prev_green)
        blue = costs[i][1] + min(prev_red, prev_green)
        green = costs[i][2] + min(prev_red, prev_blue)
        prev_red, prev_blue, prev_green = red, blue, green
    return min(prev_red, prev_blue, prev_green)
```

---

### 12. LeetCode 1937. Maximum Number of Points with Cost
**Archetype:** 13.1 Linear Choice + Optimization
**Type:** Interview Sim
**Statement:** Given a matrix of points, pick one cell per row such that if you pick column `c` in row `r` and column `c'` in row `r+1`, you lose `abs(c - c')` points. Maximize total points.
**Why it fits:** A naive DP would be O(m * n^2). The optimal solution uses left-to-right and right-to-left prefix maximums to compute the column transition penalty in O(n) per row.
**The Twist:** The penalty term `abs(c - c')` makes the transition non-local. The optimization to O(m*n) using running maxima from both directions is the key interview differentiator.
**Code Skeleton:**
```python
def maxPoints(points: list[list[int]]) -> int:
    rows, cols = len(points), len(points[0])
    prev = points[0][:]
    for r in range(1, rows):
        left = [0] * cols
        right = [0] * cols
        left[0] = prev[0]
        for c in range(1, cols):
            left[c] = max(left[c - 1], prev[c] + c)
        right[cols - 1] = prev[cols - 1] - (cols - 1)
        for c in range(cols - 2, -1, -1):
            right[c] = max(right[c + 1], prev[c] - c)
        for c in range(cols):
            prev[c] = points[r][c] + max(left[c] - c, right[c] + c)
    return max(prev)
```

---

### 13. LeetCode 1987. Number of Unique Good Subsequences
**Archetype:** 13.5 Counting Ways + State Machine
**Type:** Interview Sim
**Statement:** Given a binary string, return the number of unique good subsequences (non-empty, no leading zeros unless it is "0").
**Why it fits:** Track `ends_with_0` and `ends_with_1`: the number of unique subsequences ending in each digit. Adding a new digit appends it to all existing subsequences, but duplicates must be avoided.
**The Twist:** Leading zeros are forbidden, so '0' can only appear alone. Also, appending '0' to all existing subsequences duplicates those already ending in '0', so you must subtract the old count.
**Code Skeleton:**
```python
def numberOfUniqueGoodSubsequences(binary: str) -> int:
    MOD = 10**9 + 7
    ends_with_0 = ends_with_1 = 0
    has_zero = 0
    for ch in binary:
        if ch == '0':
            ends_with_0 = (ends_with_0 + ends_with_1) % MOD
            has_zero = 1
        else:
            ends_with_1 = (ends_with_0 + ends_with_1 + 1) % MOD
    return (ends_with_0 + ends_with_1 + has_zero) % MOD
```

---

### 14. LeetCode 673. Number of Longest Increasing Subsequence
**Archetype:** 13.6 LIS + Counting
**Type:** Interview Sim
**Statement:** Find the number of longest increasing subsequences.
**Why it fits:** Extends LIS by tracking both length (`dp_len[i]`) and count (`dp_cnt[i]`). When a longer subsequence is found, reset the count; when an equal-length subsequence is found, accumulate the count.
**The Twist:** You must carefully handle the case where the same length is reached through different paths. Updating counts only when `len[j] + 1 == len[i]` avoids double counting.
**Code Skeleton:**
```python
def findNumberOfLIS(nums: list[int]) -> int:
    n = len(nums)
    if n == 0:
        return 0
    length = [1] * n
    count = [1] * n
    max_len = 1
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if length[j] + 1 > length[i]:
                    length[i] = length[j] + 1
                    count[i] = count[j]
                elif length[j] + 1 == length[i]:
                    count[i] += count[j]
        max_len = max(max_len, length[i])
    return sum(c for l, c in zip(length, count) if l == max_len)
```

---

### 15. LeetCode 2370. Longest Ideal Subsequence
**Archetype:** 13.6 LIS Variant
**Type:** Interview Sim
**Statement:** Given a string and an integer k, return the length of the longest ideal subsequence where adjacent characters differ by at most k in alphabet order.
**Why it fits:** It generalizes LIS from a global ordering constraint to a bounded difference constraint. Instead of a single tails array, you maintain `best[char]` = longest subsequence ending with that character.
**The Twist:** The alphabet constraint reduces the search space to 26 letters. For each character, you only need to check the window `[ch - k, ch + k]` in the alphabet, making it O(n * 26) rather than O(n^2).
**Code Skeleton:**
```python
def longestIdealString(s: str, k: int) -> int:
    best = [0] * 26
    for ch in s:
        idx = ord(ch) - ord('a')
        # Look back and forward within k letters
        lo = max(0, idx - k)
        hi = min(25, idx + k)
        best[idx] = 1 + max(best[lo:hi + 1])
    return max(best)
```

---

## Checklist
- [ ] Can recognize when greedy beats 1-D DP (Jump Game)
- [ ] Can design multi-state 1-D DP (Domino Tiling, Paint House)
- [ ] Can blend LIS with hash maps or alphabet constraints
- [ ] Can optimize O(n^2) transitions with prefix maxima (Points with Cost)
- [ ] Can handle counting + length tracking simultaneously (Number of LIS)
