# Pattern 13: 1-D Dynamic Programming

> **Pattern Recognition:** When you see "maximize", "minimize", "ways to reach", "decision at each step", "optimal substructure", "climbing stairs", "house robber", "stock" — think 1-D DP.
>
> **Fundamental Insight:** DP = recursion + memoization. If a problem has overlapping subproblems and optimal substructure, cache the results. The 1-D array `dp[i]` usually represents "the best answer up to position i."

---

## Archetype 13.1: Linear Choice (Pick or Skip)

### Recognition Signal
Words: **"house robber", "max sum", "cannot pick adjacent", "non-adjacent"**

### Template
```python
def rob(nums):
    if not nums:
        return 0
    if len(nums) <= 2:
        return max(nums)
    
    dp = [0] * len(nums)
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])
    
    for i in range(2, len(nums)):
        dp[i] = max(dp[i-1], dp[i-2] + nums[i])
    
    return dp[-1]
```

**Space optimization:** Only need `dp[i-1]` and `dp[i-2]`.

```python
def rob_optimized(nums):
    prev2, prev1 = 0, 0
    for num in nums:
        current = max(prev1, prev2 + num)
        prev2, prev1 = prev1, current
    return prev1
```

### Problems
- House Robber (LeetCode 198)
- House Robber II (LeetCode 213) — circular
- Maximum Subarray (LeetCode 53) — Kadane's algorithm
- Delete and Earn (LeetCode 740)

---

## Archetype 13.2: Climbing / Jump

### Recognition Signal
Words: **"climbing stairs", "ways to reach", "jump", "step", "distinct ways"**

### Template
```python
def climb_stairs(n):
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

### Problems
- Climbing Stairs (LeetCode 70)
- Jump Game (LeetCode 55) — can reach end?
- Jump Game II (LeetCode 45) — min jumps
- Min Cost Climbing Stairs (LeetCode 746)
- Unique Paths (LeetCode 62) — grid but same idea

---

## Archetype 13.3: Partition / Cut

### Recognition Signal
Words: **"partition", "word break", "cut", "split", "minimum cuts"**

### Problems
- Word Break (LeetCode 139)
- Word Break II (LeetCode 140)
- Palindrome Partitioning II (LeetCode 132)
- Decode Ways (LeetCode 91)

**Word Break:**
```python
def word_break(s, word_dict):
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for word in word_dict:
            if i >= len(word) and s[i-len(word):i] == word and dp[i-len(word)]:
                dp[i] = True
                break
    return dp[len(s)]
```

---

## Archetype 13.4: Stock Problems

### Recognition Signal
Words: **"stock", "buy", "sell", "profit", "transaction", "cooldown"**

### Problems
- Best Time to Buy and Sell Stock (LeetCode 121) — one transaction
- Best Time to Buy and Sell Stock II (LeetCode 122) — unlimited
- Best Time to Buy and Sell Stock III (LeetCode 123) — at most 2
- Best Time to Buy and Sell Stock IV (LeetCode 188) — at most k
- Best Time to Buy and Sell Stock with Cooldown (LeetCode 309)
- Best Time to Buy and Sell Stock with Transaction Fee (LeetCode 714)

**State machine approach for cooldown:**
```python
def max_profit_with_cooldown(prices):
    if not prices:
        return 0
    n = len(prices)
    hold = [0] * n
    sold = [0] * n
    rest = [0] * n
    
    hold[0] = -prices[0]
    sold[0] = 0
    rest[0] = 0
    
    for i in range(1, n):
        hold[i] = max(hold[i-1], rest[i-1] - prices[i])
        sold[i] = hold[i-1] + prices[i]
        rest[i] = max(rest[i-1], sold[i-1])
    
    return max(sold[-1], rest[-1])
```

---

## Archetype 13.5: Counting Ways

### Recognition Signal
Words: **"count ways", "number of ways", "distinct ways", "tribonacci", "tiling"**

### Problems
- Decode Ways (LeetCode 91)
- Domino and Tromino Tiling (LeetCode 790)
- Number of Ways to Build Sturdy Brick Wall (LeetCode 2184)

---

## Archetype 13.6: Longest Increasing Subsequence (LIS)

### Recognition Signal
Words: **"longest increasing subsequence", "longest decreasing", "patience sorting"**

### Template: Binary Search (O(n log n))
```python
def length_of_lis(nums):
    tails = []
    for num in nums:
        idx = bisect_left(tails, num)
        if idx == len(tails):
            tails.append(num)
        else:
            tails[idx] = num
    return len(tails)
```

### Problems
- Longest Increasing Subsequence (LeetCode 300)
- Largest Divisible Subset (LeetCode 368)
- Russian Doll Envelopes (LeetCode 354) — sort + LIS

---

## Archetype 13.7: State Machine DP

### Recognition Signal
Words: **"state", "hold", "sold", "rest", "active", "inactive"**

The question involves multiple states that transition between each other.

### Problems
- Best Time to Buy and Sell Stock with Cooldown (309)
- Best Time to Buy and Sell Stock with Transaction Fee (714)
- Paint House (LeetCode 256)
- Paint Fence (LeetCode 276)

---

## Mastery Checklist
- [ ] House robber: pick or skip adjacent
- [ ] Climbing stairs: count ways
- [ ] Word break: boolean DP
- [ ] Stock problems: state machine
- [ ] LIS: patience sorting / binary search
- [ ] Space optimization: O(1) or O(k) instead of O(n)

---

## The 1-D DP Template

```python
def dp_solve(nums):
    n = len(nums)
    dp = [0] * n  # or n+1 depending on problem
    
    # Base cases
    dp[0] = ...
    if n > 1:
        dp[1] = ...
    
    # Recurrence
    for i in range(2, n):
        dp[i] = some_function_of(dp[i-1], dp[i-2], nums[i])
    
    return dp[n-1]
```

**Key questions:**
1. What does `dp[i]` represent?
2. What is the recurrence relation?
3. What are the base cases?
4. Can I optimize space?

---

## Common Traps

**Trap:** Off-by-one in base cases.
- Fix: Test with n=0, n=1, n=2 manually.

**Trap:** Using O(n) space when O(1) suffices.
- Fix: Check if you only need last k values.

**Trap:** Confusing subarray (contiguous) with subsequence (not necessarily contiguous).
- Subarray → usually Kadane's or sliding window
- Subsequence → usually DP

**Near Miss: Fibonacci**
- Climbing stairs is Fibonacci
- But "count ways to reach n with steps 1,2,3" is Tribonacci
- Generalize: ways[n] = sum(ways[n-step] for step in allowed_steps)
