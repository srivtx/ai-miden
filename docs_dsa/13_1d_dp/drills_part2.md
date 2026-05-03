# Pattern 13: 1-D DP — Drills Part 2

> **5 Warm-ups + 10 Core Drills**
> Focus: Master the foundational recurrence relations before tackling blends.

---

## Warm-ups

### 1. LeetCode 198. House Robber
**Archetype:** 13.1 Linear Choice (Pick or Skip)
**Type:** Warm-Up
**Statement:** Given an array of house values, find the max money you can rob without alerting police (no two adjacent houses).
**Why it fits:** This is the canonical "pick or skip" DP. `dp[i]` represents the maximum money robable up to house `i`. The recurrence `dp[i] = max(dp[i-1], dp[i-2] + nums[i])` captures the core 1-D DP decision at every step.
**The Twist:** None — this is the archetype itself. Master the space-optimized O(1) version.
**Code Skeleton:**
```python
def rob(nums: list[int]) -> int:
    # Edge case: empty street
    if not nums:
        return 0
    # dp[i] = max money up to house i
    prev2, prev1 = 0, 0
    for num in nums:
        current = max(prev1, prev2 + num)
        prev2, prev1 = prev1, current
    return prev1
```

---

### 2. LeetCode 70. Climbing Stairs
**Archetype:** 13.2 Climbing/Jump
**Type:** Warm-Up
**Statement:** Count distinct ways to reach the top of a staircase taking 1 or 2 steps at a time.
**Why it fits:** Pure Fibonacci-style counting DP. `dp[i]` = ways to reach step `i`. The state only depends on the previous two states, making it the simplest 1-D recurrence.
**The Twist:** None — this is the foundational counting template. Try the O(1) space version to build intuition.
**Code Skeleton:**
```python
def climbStairs(n: int) -> int:
    # Base cases: 1 way to stand still, 2 ways to reach step 2
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current
    return prev1
```

---

### 3. LeetCode 121. Best Time to Buy and Sell Stock
**Archetype:** 13.4 Stock Problems
**Type:** Warm-Up
**Statement:** Given daily prices, find the max profit from one buy and one sell.
**Why it fits:** The simplest stock DP. You only track the minimum price seen so far and the max profit achievable. It introduces the idea of maintaining a running state across the array.
**The Twist:** Only one transaction allowed, so you do not need a full DP table — a single pass with state tracking suffices.
**Code Skeleton:**
```python
def maxProfit(prices: list[int]) -> int:
    if not prices:
        return 0
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        # Update min price seen so far
        min_price = min(min_price, price)
        # Best profit if we sell today
        max_profit = max(max_profit, price - min_price)
    return max_profit
```

---

### 4. LeetCode 53. Maximum Subarray
**Archetype:** 13.1 Linear Choice (Pick or Skip)
**Type:** Warm-Up
**Statement:** Find the contiguous subarray with the largest sum.
**Why it fits:** Kadane's algorithm is a 1-D DP in disguise. `dp[i]` = max sum subarray ending at `i`. The decision is whether to extend the previous subarray or start fresh at `i`.
**The Twist:** The subarray must be contiguous, so this is actually a sliding-window/DP hybrid. It teaches the "start fresh vs extend" decision.
**Code Skeleton:**
```python
def maxSubArray(nums: list[int]) -> int:
    # Kadane's: track max subarray ending at current index
    current_sum = max_sum = nums[0]
    for num in nums[1:]:
        # Either extend the previous subarray or start new at num
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum
```

---

### 5. LeetCode 746. Min Cost Climbing Stairs
**Archetype:** 13.2 Climbing/Jump
**Type:** Warm-Up
**Statement:** Each step has a cost; pay it to climb. Find min cost to reach the top, starting from step 0 or 1.
**Why it fits:** Direct extension of climbing stairs with weighted edges. `dp[i]` = min cost to reach step `i`. Recurrence adds `cost[i]` to the cheaper of the two previous steps.
**The Twist:** You can start at index 0 or 1 for free, and you pay the cost of the step you are leaving. The "top" is past the last index.
**Code Skeleton:**
```python
def minCostClimbingStairs(cost: list[int]) -> int:
    n = len(cost)
    # dp[i] = min cost to reach step i
    prev2, prev1 = 0, 0  # cost to reach step 0 and 1 is 0
    for i in range(2, n + 1):
        # Pay cost to leave step i-1 or i-2
        current = min(prev1 + cost[i - 1], prev2 + cost[i - 2])
        prev2, prev1 = prev1, current
    return prev1
```

---

## Core Drills

### 6. LeetCode 213. House Robber II
**Archetype:** 13.1 Linear Choice (Pick or Skip)
**Type:** Core Drill
**Statement:** Houses are arranged in a circle; rob max money without robbing adjacent houses.
**Why it fits:** It extends the linear choice archetype by adding a circular constraint. The optimal solution either excludes the first house or excludes the last house — reducing to two linear House Robber problems.
**The Twist:** The first and last houses are adjacent, so you cannot simply run the linear DP on the whole array. You must run it twice on subarrays.
**Code Skeleton:**
```python
def rob(nums: list[int]) -> int:
    if len(nums) == 1:
        return nums[0]
    
    def rob_linear(houses: list[int]) -> int:
        prev2, prev1 = 0, 0
        for h in houses:
            prev2, prev1 = prev1, max(prev1, prev2 + h)
        return prev1
    
    # Either rob houses [0..n-2] or [1..n-1]
    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
```

---

### 7. LeetCode 91. Decode Ways
**Archetype:** 13.5 Counting Ways / 13.3 Partition/Cut
**Type:** Core Drill
**Statement:** A message containing letters A-Z is encoded to numbers. Count total ways to decode a digit string.
**Why it fits:** `dp[i]` = ways to decode up to index `i`. At each position you can take one digit (if it is not '0') or two digits (if they form 10-26). This is a canonical counting DP with branching decisions.
**The Twist:** '0' is not a valid single digit and can only pair with the preceding '1' or '2'. This breaks simple Fibonacci counting and requires careful condition checks.
**Code Skeleton:**
```python
def numDecodings(s: str) -> int:
    if not s or s[0] == '0':
        return 0
    n = len(s)
    prev2, prev1 = 1, 1  # dp[-1], dp[0]
    for i in range(1, n):
        current = 0
        # Single digit decode (if s[i] != '0')
        if s[i] != '0':
            current += prev1
        # Two digit decode (if s[i-1:i+1] is 10-26)
        two_digit = int(s[i-1:i+1])
        if 10 <= two_digit <= 26:
            current += prev2
        prev2, prev1 = prev1, current
        if current == 0:
            return 0
    return prev1
```

---

### 8. LeetCode 300. Longest Increasing Subsequence
**Archetype:** 13.6 LIS
**Type:** Core Drill
**Statement:** Find the length of the longest strictly increasing subsequence.
**Why it fits:** `dp[i]` = length of LIS ending at index `i`. For each element, scan all previous elements to find the best predecessor. This teaches the O(n^2) DP formulation before optimizing to O(n log n).
**The Twist:** The subsequence is not contiguous. The O(n log n) patience-sorting variant using binary search is a must-know optimization.
**Code Skeleton:**
```python
def lengthOfLIS(nums: list[int]) -> int:
    # O(n log n) using patience sorting (tails array)
    from bisect import bisect_left
    tails = []
    for num in nums:
        idx = bisect_left(tails, num)
        if idx == len(tails):
            tails.append(num)
        else:
            tails[idx] = num
    return len(tails)
```

---

### 9. LeetCode 139. Word Break
**Archetype:** 13.3 Partition/Cut
**Type:** Core Drill
**Statement:** Given a string and a dictionary, determine if the string can be segmented into dictionary words.
**Why it fits:** `dp[i]` = True if `s[0:i]` can be segmented. For each position, check all dictionary words to see if one ends at `i` and the prefix before it is also segmentable. Classic boolean DP over substrings.
**The Twist:** The dictionary can contain words of varying lengths, so the inner loop must check all word lengths, not just the previous character.
**Code Skeleton:**
```python
def wordBreak(s: str, wordDict: list[str]) -> bool:
    word_set = set(wordDict)
    max_len = max((len(w) for w in wordDict), default=0)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - max_len), i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[len(s)]
```

---

### 10. LeetCode 122. Best Time to Buy and Sell Stock II
**Archetype:** 13.4 Stock Problems
**Type:** Core Drill
**Statement:** Maximize profit with unlimited transactions; you must sell before buying again.
**Why it fits:** This introduces the idea of summing all positive daily differences. The greedy interpretation (sum all upswings) has an equivalent DP formulation where you track the max profit at each day with/without stock.
**The Twist:** Unlimited transactions simplify the state machine to just adding positive price deltas. It bridges the gap from one-transaction to k-transaction stock DP.
**Code Skeleton:**
```python
def maxProfit(prices: list[int]) -> int:
    # Equivalent to summing all positive daily differences
    profit = 0
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        if delta > 0:
            profit += delta
    return profit
```

---

### 11. LeetCode 309. Best Time to Buy and Sell Stock with Cooldown
**Archetype:** 13.7 State Machine / 13.4 Stock Problems
**Type:** Core Drill
**Statement:** Maximize profit with unlimited transactions, but after selling you cannot buy for one day.
**Why it fits:** This requires explicit state tracking: `hold`, `sold`, and `rest` states transition based on actions. It is the canonical introduction to state-machine DP.
**The Twist:** The cooldown creates a dependency that skips a day after selling, so the `sold` state feeds into `rest` before it can become `hold` again.
**Code Skeleton:**
```python
def maxProfit(prices: list[int]) -> int:
    if not prices:
        return 0
    # States: hold = holding stock, sold = just sold, rest = cooldown/idle
    hold, sold, rest = -prices[0], 0, 0
    for price in prices[1:]:
        prev_hold, prev_sold, prev_rest = hold, sold, rest
        hold = max(prev_hold, prev_rest - price)
        sold = prev_hold + price
        rest = max(prev_rest, prev_sold)
    return max(sold, rest)
```

---

### 12. LeetCode 45. Jump Game II
**Archetype:** 13.2 Climbing/Jump
**Type:** Core Drill
**Statement:** Given max jump length from each position, find the minimum number of jumps to reach the last index.
**Why it fits:** `dp[i]` = min jumps to reach index `i`. For each position, scan all reachable previous positions and take the minimum jumps + 1. This is O(n^2) DP; the greedy BFS optimization to O(n) is a critical follow-up.
**The Twist:** Greedy BFS makes this O(n), but the DP formulation builds intuition for reachability problems. The twist is realizing greedy works here because all jumps are non-negative.
**Code Skeleton:**
```python
def jump(nums: list[int]) -> int:
    # Greedy BFS: track current reachable boundary and farthest reachable
    jumps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            jumps += 1
            current_end = farthest
    return jumps
```

---

### 13. LeetCode 740. Delete and Earn
**Archetype:** 13.1 Linear Choice (Pick or Skip)
**Type:** Core Drill
**Statement:** Given an array of integers, when you pick `nums[i]`, you earn its value but must delete all instances of `nums[i]-1` and `nums[i]+1`. Maximize earnings.
**Why it fits:** It reduces to House Robber by grouping values into buckets. `earn[v]` = total value of all occurrences of `v`. Then picking `v` prevents picking `v-1`, identical to the no-adjacent rule.
**The Twist:** The input is not sorted by value; you must bucket/count first, then run the linear DP on the value domain rather than the input index.
**Code Skeleton:**
```python
def deleteAndEarn(nums: list[int]) -> int:
    if not nums:
        return 0
    max_val = max(nums)
    points = [0] * (max_val + 1)
    for num in nums:
        points[num] += num
    # Now this is exactly House Robber on the points array
    prev2, prev1 = 0, 0
    for p in points:
        prev2, prev1 = prev1, max(prev1, prev2 + p)
    return prev1
```

---

### 14. LeetCode 132. Palindrome Partitioning II
**Archetype:** 13.3 Partition/Cut
**Type:** Core Drill
**Statement:** Given a string, partition it so every substring is a palindrome. Return the minimum cuts needed.
**Why it fits:** `dp[i]` = min cuts for prefix `s[0:i]`. For each `i`, scan all `j < i` where `s[j:i]` is a palindrome and take `dp[j] + 1`. Combines boolean palindrome checking with partition DP.
**The Twist:** Precomputing a palindrome table with expansion is crucial for O(n^2) time; a naive palindrome check inside the DP makes it O(n^3).
**Code Skeleton:**
```python
def minCut(s: str) -> int:
    n = len(s)
    # is_pal[i][j] = True if s[i..j] is a palindrome
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i <= 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
    
    # dp[i] = min cuts for s[0..i]
    dp = [float('inf')] * n
    for i in range(n):
        if is_pal[0][i]:
            dp[i] = 0
        else:
            for j in range(1, i + 1):
                if is_pal[j][i]:
                    dp[i] = min(dp[i], dp[j - 1] + 1)
    return dp[n - 1]
```

---

### 15. LeetCode 188. Best Time to Buy and Sell Stock IV
**Archetype:** 13.4 Stock Problems
**Type:** Core Drill
**Statement:** Maximize profit with at most `k` transactions.
**Why it fits:** This is the most general stock DP. You maintain two arrays: `buy[j]` = max profit up to day `i` with at most `j` transactions and holding stock; `sell[j]` = max profit with at most `j` transactions and not holding.
**The Twist:** When `k >= n // 2`, it reduces to unlimited transactions (Stock II). The general case requires O(n * k) time, which is too slow for large `k` without the optimization.
**Code Skeleton:**
```python
def maxProfit(k: int, prices: list[int]) -> int:
    n = len(prices)
    if n < 2 or k == 0:
        return 0
    # Optimization: unlimited transactions case
    if k >= n // 2:
        profit = 0
        for i in range(1, n):
            profit += max(0, prices[i] - prices[i - 1])
        return profit
    
    # dp for at most k transactions
    buy = [-prices[0]] * k
    sell = [0] * k
    for price in prices[1:]:
        for j in range(k):
            # Either buy today (using profit from previous sell) or keep holding
            buy[j] = max(buy[j], (sell[j - 1] if j > 0 else 0) - price)
            # Either sell today or keep not holding
            sell[j] = max(sell[j], buy[j] + price)
    return sell[k - 1]
```

---

## Checklist
- [ ] Can write House Robber in O(1) space without looking
- [ ] Can explain why Decode Ways is not Fibonacci
- [ ] Can derive the O(n log n) LIS algorithm
- [ ] Can map a stock problem to buy/sell arrays
- [ ] Can reduce Delete and Earn to House Robber
