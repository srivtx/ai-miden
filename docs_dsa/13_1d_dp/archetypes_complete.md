# Pattern 13: 1-D DP — Complete Archetype Map

> **Pattern Recognition:** When you see "maximum/minimum", "count ways", "can you achieve", "optimal substructure", "overlapping subproblems", "linear array", "decision at each step" — think 1-D DP.
>
> **Fundamental Insight:** If the optimal solution to a problem can be constructed from optimal solutions to smaller instances of the same problem, and those subproblems overlap, use DP. Store answers in an array to avoid recomputation.

---

## Archetype 13.1: Linear Choice (Pick or Skip)

### Recognition Signal (10 seconds)
Words: **"rob houses", "maximum sum", "non-adjacent", "pick or skip", "cannot pick adjacent", "weighted interval"**

The question is always: **"At each position, decide whether to include the current element (and skip the previous) or exclude it (and carry forward the best so far)."**

### Core Structure
```python
def linear_choice(nums):
    if not nums:
        return 0
    prev2 = 0  # dp[i-2]
    prev1 = 0  # dp[i-1]
    for num in nums:
        curr = max(prev1, prev2 + num)  # Skip or pick
        prev2 = prev1
        prev1 = curr
    return prev1
```

### The Invariant
`dp[i]` represents the optimal value considering the first i elements. The decision at i only depends on `dp[i-1]` (skip i) and `dp[i-2] + nums[i]` (pick i). Because subproblems overlap in this exact way, we compress to two variables.

### Canonical Problem: House Robber (LeetCode 198)
**Statement:** Given non-negative integers representing money in houses, rob maximum amount without robbing adjacent houses.

```python
def rob(nums):
    prev2 = 0
    prev1 = 0
    for num in nums:
        curr = max(prev1, prev2 + num)
        prev2 = prev1
        prev1 = curr
    return prev1
```

### Variation Family

**V1: House Robber II (LeetCode 213)**
- **Twist:** Houses are arranged in a circle (first and last are adjacent)
- **Change:** Run linear DP twice: once excluding first house, once excluding last. Take max.

```python
def rob_ii(nums):
    if len(nums) == 1:
        return nums[0]
    def linear(houses):
        prev2, prev1 = 0, 0
        for h in houses:
            prev2, prev1 = prev1, max(prev1, prev2 + h)
        return prev1
    return max(linear(nums[:-1]), linear(nums[1:]))
```

**V2: Maximum Sum Circular Subarray (LeetCode 918)**
- **Twist:** Subarray can wrap around the end to the beginning
- **Change:** Max subarray = max(Kadane on array, total_sum - min_subarray_sum). Handle all-negative edge case.

```python
def maxSubarraySumCircular(nums):
    total = 0
    max_sum = cur_max = float('-inf')
    min_sum = cur_min = float('inf')
    for x in nums:
        total += x
        cur_max = max(x, cur_max + x)
        max_sum = max(max_sum, cur_max)
        cur_min = min(x, cur_min + x)
        min_sum = min(min_sum, cur_min)
    if max_sum < 0:
        return max_sum  # All negative
    return max(max_sum, total - min_sum)
```

**V3: Delete and Earn (LeetCode 740)**
- **Twist:** Pick a number, earn its value * count, but you cannot pick num-1 or num+1
- **Change:** Transform to House Robber on frequency array. `points[i] = i * freq[i]`.

```python
def deleteAndEarn(nums):
    if not nums:
        return 0
    max_val = max(nums)
    points = [0] * (max_val + 1)
    for num in nums:
        points[num] += num
    prev2, prev1 = 0, 0
    for p in points:
        prev2, prev1 = prev1, max(prev1, prev2 + p)
    return prev1
```

**V4: Longest Turbulent Subarray (LeetCode 978)**
- **Twist:** Subarray where comparison sign flips between adjacent elements
- **Change:** Two DP arrays: up[i] and down[i]. up[i] = down[i-1] + 1 if arr[i-1] < arr[i].

```python
def maxTurbulenceSize(arr):
    n = len(arr)
    if n == 1:
        return 1
    up = [1] * n
    down = [1] * n
    for i in range(1, n):
        if arr[i-1] < arr[i]:
            up[i] = down[i-1] + 1
        elif arr[i-1] > arr[i]:
            down[i] = up[i-1] + 1
    return max(max(up), max(down))
```

**Near Miss: Maximum Subarray (LeetCode 53)**
- **Looks like:** Linear choice on array
- **But:** Kadane's algorithm allows adjacent picks. It's a greedy/DP hybrid where the only choice is whether to start a new subarray at i.
- **Lesson:** "Pick or skip adjacent" is House Robber. "Contiguous subarray" is Kadane.

---

## Archetype 13.2: Climbing / Jump

### Recognition Signal (10 seconds)
Words: **"climbing stairs", "ways to reach", "jump", "steps", "frog", "minimum jumps", "reach end"**

The question is always: **"Count the number of ways to reach position N from 0, or find the minimum jumps needed, given certain step sizes."**

### Core Structure
```python
def climb_stairs(n):
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[0], dp[1] = 1, 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

### The Invariant
`dp[i]` represents the number of ways (or minimum cost/jumps) to reach position i. Transitions depend only on reachable previous positions. For counting, sum the ways. For minimum, take the min.

### Canonical Problem: Climbing Stairs (LeetCode 70)
**Statement:** Count distinct ways to climb to the top. Each time you can climb 1 or 2 steps.

```python
def climbStairs(n):
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1
```

### Variation Family

**V1: Jump Game (LeetCode 55)**
- **Twist:** Can you reach the last index given max jump lengths?
- **Change:** Greedy tracking of farthest reachable index. Or DP: `dp[i] = max(dp[i-1], i + nums[i])`.

```python
def canJump(nums):
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + jump)
    return True
```

**V2: Jump Game II (LeetCode 45)**
- **Twist:** Minimum number of jumps to reach the last index
- **Change:** Greedy BFS-like: track current end and farthest reachable in current jump count.

```python
def jump(nums):
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

**V3: Minimum Cost For Tickets (LeetCode 983)**
- **Twist:** Travel on given days. Buy 1-day, 7-day, or 30-day pass. Minimize cost.
- **Change:** DP on calendar days. For each travel day, `dp[i] = min(dp[i-1]+cost1, dp[max(0,i-7)]+cost7, dp[max(0,i-30)]+cost30)`.

```python
def mincostTickets(days, costs):
    day_set = set(days)
    last_day = days[-1]
    dp = [0] * (last_day + 1)
    for i in range(1, last_day + 1):
        if i not in day_set:
            dp[i] = dp[i-1]
        else:
            dp[i] = min(
                dp[max(0, i-1)] + costs[0],
                dp[max(0, i-7)] + costs[1],
                dp[max(0, i-30)] + costs[2]
            )
    return dp[last_day]
```

**V4: Frog Jump (LeetCode 403)**
- **Twist:** Frog jumps across stones. Next jump = k-1, k, or k+1 where k was last jump size.
- **Change:** DP state is (stone_position, last_jump_size). Use a hash map of sets.

```python
def canCross(stones):
    if stones[1] != 1:
        return False
    stone_set = set(stones)
    dp = {s: set() for s in stones}
    dp[1].add(1)
    for s in stones:
        for k in dp[s]:
            for step in (k-1, k, k+1):
                if step > 0 and s + step in stone_set:
                    dp[s + step].add(step)
    return bool(dp[stones[-1]])
```

**Near Miss: Unique Paths (LeetCode 62)**
- **Looks like:** Counting ways to reach a destination
- **But:** 2D grid movement (right/down). Classic combinatorics or 2D DP.
- **Lesson:** 1D jump problems model movement along a line. 2D grid problems need 2D DP (Pattern 14).

---

## Archetype 13.3: Partition / Cut

### Recognition Signal (10 seconds)
Words: **"word break", "palindrome partitioning", "cut", "split", "partition", "minimum cuts", "dictionary"**

The question is always: **"Can we partition the string/array into valid segments? If so, what's the minimum number of cuts?"**

### Core Structure
```python
def word_break(s, wordDict):
    word_set = set(wordDict)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[len(s)]
```

### The Invariant
`dp[i]` is True if the prefix `s[0:i]` can be segmented into dictionary words. We check all possible last cuts `j`. If `dp[j]` is True and `s[j:i]` is a word, then `dp[i]` is True.

### Canonical Problem: Word Break (LeetCode 139)
**Statement:** Given a string and a dictionary, determine if the string can be segmented into dictionary words.

```python
def wordBreak(s, wordDict):
    word_set = set(wordDict)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[len(s)]
```

### Variation Family

**V1: Word Break II (LeetCode 140)**
- **Twist:** Return all possible valid sentences
- **Change:** DP + backtracking / memoized DFS. Build sentences from valid prefixes.

```python
def wordBreakII(s, wordDict):
    word_set = set(wordDict)
    memo = {}
    def backtrack(start):
        if start in memo:
            return memo[start]
        if start == len(s):
            return [""]
        res = []
        for end in range(start + 1, len(s) + 1):
            word = s[start:end]
            if word in word_set:
                for sub in backtrack(end):
                    res.append(word + (" " if sub else "") + sub)
        memo[start] = res
        return res
    return backtrack(0)
```

**V2: Palindrome Partitioning II (LeetCode 132)**
- **Twist:** Minimum cuts needed so that every substring is a palindrome
- **Change:** `cuts[i]` = min cuts for prefix `s[0:i+1]`. Precompute palindrome table.

```python
def minCut(s):
    n = len(s)
    # pal[i][j] = True if s[i:j+1] is palindrome
    pal = [[False] * n for _ in range(n)]
    for i in range(n-1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i <= 2 or pal[i+1][j-1]):
                pal[i][j] = True

    cuts = [i for i in range(n)]  # worst case: cut every character
    for i in range(n):
        if pal[0][i]:
            cuts[i] = 0
        else:
            for j in range(i):
                if pal[j+1][i]:
                    cuts[i] = min(cuts[i], cuts[j] + 1)
    return cuts[n-1]
```

**V3: Decode Ways II (LeetCode 639)**
- **Twist:** Decode string with '*' wildcard (can be 1-9)
- **Change:** DP with modulo arithmetic. Handle single and double digit cases with '*' combinatorics.

**V4: Boolean Parenthesization / Burst Balloons**
- **Twist:** Optimal evaluation order / maximum coins
- **Change:** Interval DP (Pattern 14), not pure 1D. Shows how partition problems escalate.

**Near Miss: Longest Palindromic Substring (LeetCode 5)**
- **Looks like:** Palindromes in a string
- **But:** Expand-around-center or Manacher's algorithm is O(n^2) or O(n). DP is O(n^2) and overkill.
- **Lesson:** Partition/cut problems need DP. Finding one palindrome may not.

---

## Archetype 13.4: Stock Problems

### Recognition Signal (10 seconds)
Words: **"stock", "buy", "sell", "profit", "transactions", "cooldown", "fee", "best time"**

The question is always: **"Maximize profit given constraints on number of transactions, cooldown, or transaction fees."**

### Core Structure
```python
def max_profit_one_transaction(prices):
    min_price = float('inf')
    max_profit = 0
    for p in prices:
        min_price = min(min_price, p)
        max_profit = max(max_profit, p - min_price)
    return max_profit
```

### The Invariant
For one transaction, track the minimum price seen so far. For multiple transactions, track states: `hold[i]` = max profit on day i holding a stock; `not_hold[i]` = max profit on day i not holding.

### Canonical Problem: Best Time to Buy and Sell Stock (LeetCode 121)
**Statement:** Maximize profit with at most one transaction.

```python
def maxProfit(prices):
    min_price = float('inf')
    max_profit = 0
    for p in prices:
        min_price = min(min_price, p)
        max_profit = max(max_profit, p - min_price)
    return max_profit
```

### Variation Family

**V1: Best Time to Buy and Sell Stock II (LeetCode 122)**
- **Twist:** Unlimited transactions
- **Change:** Sum all positive daily differences.

```python
def maxProfitII(prices):
    profit = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            profit += prices[i] - prices[i-1]
    return profit
```

**V2: Best Time to Buy and Sell Stock III (LeetCode 123)**
- **Twist:** At most 2 transactions
- **Change:** Track 4 states: first buy, first sell, second buy, second sell.

```python
def maxProfitIII(prices):
    first_buy = second_buy = float('-inf')
    first_sell = second_sell = 0
    for p in prices:
        first_buy = max(first_buy, -p)
        first_sell = max(first_sell, first_buy + p)
        second_buy = max(second_buy, first_sell - p)
        second_sell = max(second_sell, second_buy + p)
    return second_sell
```

**V3: Best Time to Buy and Sell Stock IV (LeetCode 188)**
- **Twist:** At most k transactions
- **Change:** Generalize to k transactions. If k >= n/2, equivalent to unlimited transactions.

```python
def maxProfitIV(k, prices):
    n = len(prices)
    if k >= n // 2:
        return sum(max(0, prices[i] - prices[i-1]) for i in range(1, n))
    buy = [float('-inf')] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for i in range(1, k + 1):
            buy[i] = max(buy[i], sell[i-1] - p)
            sell[i] = max(sell[i], buy[i] + p)
    return sell[k]
```

**V4: Best Time to Buy and Sell Stock with Transaction Fee (LeetCode 714)**
- **Twist:** Pay a fee for each transaction
- **Change:** State machine. `hold = max(hold, cash - price)`. `cash = max(cash, hold + price - fee)`.

```python
def maxProfitWithFee(prices, fee):
    cash, hold = 0, -prices[0]
    for p in prices[1:]:
        cash = max(cash, hold + p - fee)
        hold = max(hold, cash - p)
    return cash
```

**Near Miss: Maximum Subarray (LeetCode 53)**
- **Looks like:** Maximize profit/gain over an array
- **But:** Kadane's algorithm finds max sum contiguous subarray. Stock problems add buy/sell semantics.
- **Lesson:** Stock problems are a specialized family with state machine structure.

---

## Archetype 13.5: Counting Ways

### Recognition Signal (10 seconds)
Words: **"count ways", "number of ways", "decode", "distinct subsequences", "paint fence", "tiling", "climbing"**

The question is always: **"Count the number of valid ways to achieve a target, where each step has defined choices."**

### Core Structure
```python
def count_ways(n, choices):
    dp = [0] * (n + 1)
    dp[0] = 1  # Base case: one way to do nothing
    for i in range(1, n + 1):
        for c in choices:
            if i - c >= 0:
                dp[i] += dp[i - c]
    return dp[n]
```

### The Invariant
`dp[i]` accumulates ways from all valid previous states. The order of iteration matters: we build up from smaller targets to larger ones, ensuring all subproblems are solved before they are needed.

### Canonical Problem: Decode Ways (LeetCode 91)
**Statement:** A message containing letters A-Z is encoded to numbers using '1'-'26'. Count total number of ways to decode a digit string.

```python
def numDecodings(s):
    if not s or s[0] == '0':
        return 0
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        one_digit = int(s[i-1])
        two_digit = int(s[i-2:i])
        if 1 <= one_digit <= 9:
            dp[i] += dp[i-1]
        if 10 <= two_digit <= 26:
            dp[i] += dp[i-2]
    return dp[n]
```

### Variation Family

**V1: Decode Ways II (LeetCode 639)**
- **Twist:** '*' can represent 1-9
- **Change:** Combinatorics per position. Handle single '*' (9 ways), double '1*'/'2*' (15/6 ways), '**' (15 ways), etc.

**V2: Distinct Subsequences (LeetCode 115)**
- **Twist:** Count distinct subsequences of s that equal t
- **Change:** 2D DP, but can be optimized to 1D. `dp[j]` = ways to form `t[:j]` from processed prefix of s.

```python
def numDistinct(s, t):
    m, n = len(t), len(s)
    dp = [0] * (m + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(m, 0, -1):
            if s[i-1] == t[j-1]:
                dp[j] += dp[j-1]
    return dp[m]
```

**V3: Paint Fence (LeetCode 276)**
- **Twist:** Paint fence with k colors, no more than 2 adjacent posts same color
- **Change:** `same[i]` = ways where i and i-1 same color. `diff[i]` = ways where different.

```python
def numWays(n, k):
    if n == 0:
        return 0
    if n == 1:
        return k
    same = k  # first two are same (but only 1 way for 2 posts: pick 1 color)
    diff = k * (k - 1)
    for _ in range(3, n + 1):
        same, diff = diff, (same + diff) * (k - 1)
    return same + diff
```

**V4: Domino and Tromino Tiling (LeetCode 790)**
- **Twist:** Count ways to tile a 2xn board with dominoes and trominoes
- **Change:** Track states for fully covered vs partially covered columns.

```python
def numTilings(n):
    MOD = 10**9 + 7
    dp = [0] * (n + 1)
    dp[0], dp[1] = 1, 1
    if n >= 2:
        dp[2] = 2
    for i in range(3, n + 1):
        dp[i] = (2 * dp[i-1] + dp[i-3]) % MOD
    return dp[n]
```

**Near Miss: Coin Change (LeetCode 322)**
- **Looks like:** Counting ways
- **But:** Asks for minimum coins, not number of ways. Similar recurrence but uses min instead of sum.
- **Lesson:** "Count ways" = sum of subproblems. "Minimum coins" = min of subproblems.

---

## Archetype 13.6: LIS (Longest Increasing Subsequence)

### Recognition Signal (10 seconds)
Words: **"longest increasing", "longest decreasing", "subsequence", "patience sorting", "dolls", "envelopes", "Russian dolls"**

The question is always: **"Find the length of the longest subsequence where elements are strictly increasing (or non-decreasing)."**

### Core Structure (DP O(n^2))
```python
def length_of_lis(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

### Core Structure (Binary Search O(n log n))
```python
import bisect

def length_of_lis_fast(nums):
    tails = []
    for num in nums:
        idx = bisect.bisect_left(tails, num)
        if idx == len(tails):
            tails.append(num)
        else:
            tails[idx] = num
    return len(tails)
```

### The Invariant
`dp[i]` (in O(n^2)) is the length of LIS ending at i. `tails[i]` (in O(n log n)) is the smallest tail value of all increasing subsequences of length i+1. A smaller tail allows more future extensions.

### Canonical Problem: Longest Increasing Subsequence (LeetCode 300)
**Statement:** Given integer array, return length of LIS.

```python
import bisect

class Solution:
    def lengthOfLIS(self, nums):
        tails = []
        for num in nums:
            idx = bisect.bisect_left(tails, num)
            if idx == len(tails):
                tails.append(num)
            else:
                tails[idx] = num
        return len(tails)
```

### Variation Family

**V1: Russian Doll Envelopes (LeetCode 354)**
- **Twist:** 2D LIS. Width and height. One envelope fits in another only if both dimensions are strictly larger.
- **Change:** Sort by width ascending, height descending (to prevent same-width nesting). Then LIS on heights.

```python
import bisect

def maxEnvelopes(envelopes):
    envelopes.sort(key=lambda x: (x[0], -x[1]))
    tails = []
    for _, h in envelopes:
        idx = bisect.bisect_left(tails, h)
        if idx == len(tails):
            tails.append(h)
        else:
            tails[idx] = h
    return len(tails)
```

**V2: Longest Continuous Increasing Subsequence (LeetCode 674)**
- **Twist:** Contiguous, not subsequence
- **Change:** Simple linear scan tracking current streak.

**V3: Number of Longest Increasing Subsequence (LeetCode 673)**
- **Twist:** Count how many LIS exist
- **Change:** Track `count[i]` alongside `length[i]`. If `length[j] + 1 > length[i]`, set count[i] = count[j]. If equal, accumulate.

```python
def findNumberOfLIS(nums):
    n = len(nums)
    if n <= 1:
        return n
    lengths = [1] * n
    counts = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if lengths[j] + 1 > lengths[i]:
                    lengths[i] = lengths[j] + 1
                    counts[i] = counts[j]
                elif lengths[j] + 1 == lengths[i]:
                    counts[i] += counts[j]
    max_len = max(lengths)
    return sum(c for l, c in zip(lengths, counts) if l == max_len)
```

**V4: Largest Divisible Subset (LeetCode 368)**
- **Twist:** Subset where every pair is divisible
- **Change:** Sort. DP where `dp[i]` = largest divisible subset ending at i. If `nums[i] % nums[j] == 0`, extend `dp[j]`.

**Near Miss: Longest Common Subsequence (LeetCode 1143)**
- **Looks like:** Longest subsequence
- **But:** Requires two strings. Classic 2D DP.
- **Lesson:** LIS is 1D. LCS is 2D. Don't confuse them.

---

## Archetype 13.7: State Machine DP

### Recognition Signal (10 seconds)
Words: **"cooldown", "transaction fee", "rest", "active", "inactive", "sell", "buy", "states", "machine"**

The question is always: **"Model the problem as a set of states with transitions, where the choice at step i depends on the state carried over from step i-1."**

### Core Structure
```python
def state_machine(prices):
    # Two states: hold (holding stock), not_hold (not holding)
    hold = float('-inf')
    not_hold = 0
    for p in prices:
        hold, not_hold = max(hold, not_hold - p), max(not_hold, hold + p)
    return not_hold
```

### The Invariant
At each step, every possible state must be updated using the best possible previous state. The transition function encodes the problem constraints (cooldown, fee, limit on transactions).

### Canonical Problem: Best Time to Buy and Sell Stock with Cooldown (LeetCode 309)
**Statement:** After selling, you cannot buy on the next day (1-day cooldown).

```python
def maxProfitCooldown(prices):
    if not prices:
        return 0
    n = len(prices)
    hold = [0] * n
    not_hold = [0] * n
    hold[0] = -prices[0]
    not_hold[0] = 0

    for i in range(1, n):
        hold[i] = max(hold[i-1], (not_hold[i-2] if i >= 2 else 0) - prices[i])
        not_hold[i] = max(not_hold[i-1], hold[i-1] + prices[i])
    return not_hold[n-1]
```

**Space-optimized version:**
```python
def maxProfitCooldownOpt(prices):
    if not prices:
        return 0
    prev_not_hold = 0      # not_hold[i-1]
    prev_prev_not_hold = 0 # not_hold[i-2]
    hold = -prices[0]
    for p in prices[1:]:
        new_not_hold = max(prev_not_hold, hold + p)
        hold = max(hold, prev_prev_not_hold - p)
        prev_prev_not_hold = prev_not_hold
        prev_not_hold = new_not_hold
    return prev_not_hold
```

### Variation Family

**V1: Best Time to Buy and Sell Stock with Transaction Fee (LeetCode 714)**
- **Twist:** Pay fee on each sell
- **Change:** `cash = max(cash, hold + price - fee)`. `hold = max(hold, cash - price)`.

```python
def maxProfitWithFee(prices, fee):
    cash, hold = 0, -prices[0]
    for p in prices[1:]:
        cash = max(cash, hold + p - fee)
        hold = max(hold, cash - p)
    return cash
```

**V2: Maximum Sum of 3 Non-Overlapping Subarrays (LeetCode 689)**
- **Twist:** Pick 3 non-overlapping subarrays of length k with maximum sum
- **Change:** DP with state = number of subarrays selected so far. Precompute window sums.

```python
def maxSumOfThreeSubarrays(nums, k):
    n = len(nums)
    window_sum = [0] * (n - k + 1)
    cur = sum(nums[:k])
    window_sum[0] = cur
    for i in range(k, n):
        cur += nums[i] - nums[i - k]
        window_sum[i - k + 1] = cur

    left = [0] * len(window_sum)
    best = 0
    for i in range(len(window_sum)):
        if window_sum[i] > window_sum[best]:
            best = i
        left[i] = best

    right = [0] * len(window_sum)
    best = len(window_sum) - 1
    for i in range(len(window_sum) - 1, -1, -1):
        if window_sum[i] >= window_sum[best]:
            best = i
        right[i] = best

    ans = [-1, -1, -1]
    for j in range(k, len(window_sum) - k):
        i, l = left[j - k], right[j + k]
        if ans == [-1, -1, -1] or (window_sum[i] + window_sum[j] + window_sum[l] >
                                     window_sum[ans[0]] + window_sum[ans[1]] + window_sum[ans[2]]):
            ans = [i, j, l]
    return ans
```

**V3: Paint House (LeetCode 256)**
- **Twist:** Paint houses red/blue/green with no two adjacent same color. Minimize cost.
- **Change:** Three states (last color). `dp[color] = cost[i][color] + min(dp[other_colors])`.

```python
def minCost(costs):
    if not costs:
        return 0
    r, b, g = costs[0]
    for i in range(1, len(costs)):
        nr = costs[i][0] + min(b, g)
        nb = costs[i][1] + min(r, g)
        ng = costs[i][2] + min(r, b)
        r, b, g = nr, nb, ng
    return min(r, b, g)
```

**V4: House Robber III (LeetCode 337)**
- **Twist:** Houses arranged in a binary tree
- **Change:** Tree DP. Two states per node: rob this node (cannot rob children) or skip this node (can rob children).

```python
def rob(root):
    def dfs(node):
        if not node:
            return (0, 0)  # (rob, skip)
        left = dfs(node.left)
        right = dfs(node.right)
        rob = node.val + left[1] + right[1]
        skip = max(left) + max(right)
        return (rob, skip)
    return max(dfs(root))
```

**Near Miss: Maximum Subarray (LeetCode 53)**
- **Looks like:** State-based optimization over an array
- **But:** Only one state (max ending here). No complex transitions or cooldowns.
- **Lesson:** State machine DP is needed when there are mutually exclusive states with transition rules.

---

## Pattern 13 Mastery Checklist

Before moving to Pattern 14, confirm you can:

- [ ] Write House Robber with O(1) space
- [ ] Solve Climbing Stairs and Jump Game variants
- [ ] Implement Word Break and Palindrome Partitioning II
- [ ] Solve all stock variants up to k transactions
- [ ] Count decode ways with handling of '0' edge cases
- [ ] Write LIS in both O(n^2) and O(n log n)
- [ ] Model cooldown/fee problems as state machines
- [ ] Distinguish "subsequence" vs "subarray" vs "subset" in DP formulation

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Off-by-one in DP initialization | Wrong base case propagates | Explicitly test n=0, n=1, n=2 |
| Using subarray when problem asks subsequence | Wrong answer or TLE | Subsequence = non-contiguous. Subarray = contiguous |
| Not handling '0' in Decode Ways | "01" counted as valid | Skip leading zeros. Only count 10-26 |
| Space-optimized DP overwriting needed values | Logic error in compressed loop | Use temporary variables or iterate in correct direction |
| Confusing LIS binary search condition | Wrong length or incorrect strictness | Use `bisect_left` for non-decreasing, `bisect_right` for strictly increasing when needed |
| State machine missing a transition | Impossible states or missed optima | Draw state diagram before coding |

---

## Pattern Blends (What Comes Next)

1-D DP does not live in isolation. It blends with:

- **Sliding Window:** DP on fixed-size subarrays (e.g., max sum of m non-overlapping subarrays)
- **Binary Search:** Optimize DP parameters (e.g., split array largest sum)
- **Monotonic Stack/Deque:** Optimize DP transitions from a sliding range (e.g., jump game with constraints)
- **Trie:** Word Break uses a trie to test valid prefixes efficiently
- **Graph:** Shortest path in unweighted graph is BFS, but in weighted graph it's DP on DAG or Dijkstra
- **2D DP:** Many 1D DP problems generalize to grids, strings, or trees

---

*Next: Pattern 14 — 2-D DP*
