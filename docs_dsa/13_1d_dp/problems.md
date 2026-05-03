# Pattern 13: 1-D DP — Practice Problems

## Linear Choice

### 198. House Robber
**Statement:** Max money without robbing adjacent houses.
**Code:**
```python
def rob(nums):
    prev2, prev1 = 0, 0
    for num in nums:
        current = max(prev1, prev2 + num)
        prev2, prev1 = prev1, current
    return prev1
```

### 213. House Robber II
**Statement:** Houses in circle. Can't rob first and last.
**Intuition:** max(rob(0 to n-2), rob(1 to n-1)).

### 53. Maximum Subarray
**Statement:** Max sum contiguous subarray.
**Intuition:** Kadane's. max_ending_here = max(num, max_ending_here + num).
**Code:**
```python
def max_sub_array(nums):
    max_so_far = max_ending_here = nums[0]
    for num in nums[1:]:
        max_ending_here = max(num, max_ending_here + num)
        max_so_far = max(max_so_far, max_ending_here)
    return max_so_far
```

### 740. Delete and Earn
**Statement:** Delete num to earn points. All num-1 and num+1 deleted.
**Intuition:** Group by number. Earn = num * count. Same as House Robber.

---

## Climbing / Jump

### 70. Climbing Stairs
**Statement:** Ways to climb n stairs (1 or 2 steps).
**Code:**
```python
def climb_stairs(n):
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b
```

### 55. Jump Game
**Statement:** Can reach last index?
**Intuition:** Greedy. Track max reachable.
**Code:**
```python
def can_jump(nums):
    max_reach = 0
    for i, num in enumerate(nums):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + num)
    return True
```

### 45. Jump Game II
**Statement:** Min jumps to reach end.
**Intuition:** Greedy BFS. Track current end and farthest.

### 746. Min Cost Climbing Stairs
**Statement:** Min cost to reach top.
**Intuition:** dp[i] = min cost to reach step i. dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2]).

---

## Partition / Word Break

### 139. Word Break
**Statement:** Can s be segmented into dictionary words?
**Code:**
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

### 91. Decode Ways
**Statement:** Ways to decode digits to letters (1-26).
**Intuition:** dp[i] = dp[i-1] if s[i-1] != '0' + dp[i-2] if 10 <= int(s[i-2:i]) <= 26.

### 132. Palindrome Partitioning II
**Statement:** Min cuts for palindrome partitioning.
**Intuition:** dp[i] = min cuts for s[0:i]. Check all j < i where s[j:i] is palindrome.

---

## Stock Problems

### 121. Best Time to Buy and Sell Stock
**Statement:** One transaction. Max profit.
**Intuition:** Track min price. Max profit = max(current - min_price).

### 122. Best Time to Buy and Sell Stock II
**Statement:** Unlimited transactions.
**Intuition:** Sum all positive differences.

### 123. Best Time to Buy and Sell Stock III
**Statement:** At most 2 transactions.
**Intuition:** Forward and backward passes. max(first_transaction[0:i] + second_transaction[i:]).

### 188. Best Time to Buy and Sell Stock IV
**Statement:** At most k transactions.
**Intuition:** DP[k][n]. If k >= n/2, same as unlimited.

### 309. Best Time to Buy and Sell Stock with Cooldown
**Statement:** 1 day cooldown after selling.
**Intuition:** State machine. hold, sold, rest.

### 714. Best Time to Buy and Sell Stock with Transaction Fee
**Statement:** Pay fee per transaction.
**Intuition:** State machine. cash (not holding), hold.

---

## LIS

### 300. Longest Increasing Subsequence
**Statement:** Length of LIS.
**Code (Patience sorting):**
```python
import bisect

def length_of_lis(nums):
    tails = []
    for num in nums:
        idx = bisect.bisect_left(tails, num)
        if idx == len(tails):
            tails.append(num)
        else:
            tails[idx] = num
    return len(tails)
```

### 354. Russian Doll Envelopes
**Statement:** Max envelopes nested.
**Intuition:** Sort by width ascending, height descending. LIS on heights.

---

## Mixed Drill Set

1. 198 — House robber
2. 70 — Climbing stairs
3. 53 — Max subarray (Kadane)
4. 139 — Word break
5. 121 — Stock I
6. 122 — Stock II (unlimited)
7. 309 — Stock with cooldown
8. 300 — LIS
9. 55 — Jump game
10. 91 — Decode ways
11. 213 — House robber II (circular)
12. 132 — Palindrome partition II
