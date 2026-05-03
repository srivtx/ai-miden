# Pattern 15: Greedy — Drills Part 2

> **5 Warm-ups + 10 Core Drills**
> Focus: Master the greedy choice property and common sorting-based strategies.

---

## Warm-ups

### 1. LeetCode 435. Non-overlapping Intervals
**Archetype:** 15.1 Interval Scheduling
**Type:** Warm-Up
**Statement:** Given intervals, find the minimum number of intervals to remove to make the rest non-overlapping.
**Why it fits:** The canonical interval scheduling problem. Sort by end time, greedily keep the interval that ends earliest, and discard overlapping ones. This proves the greedy choice property for intervals.
**The Twist:** None — this is the archetype. The answer can also be framed as `n - max_non_overlapping`, which connects to the next problems.
**Code Skeleton:**
```python
def eraseOverlapIntervals(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[1])
    count = 1
    end = intervals[0][1]
    for i in range(1, len(intervals)):
        if intervals[i][0] >= end:
            count += 1
            end = intervals[i][1]
    return len(intervals) - count
```

---

### 2. LeetCode 55. Jump Game
**Archetype:** 15.2 Jump Game
**Type:** Warm-Up
**Statement:** Given max jump lengths from each position, determine if you can reach the last index.
**Why it fits:** Track the farthest reachable index. If at any point your current index exceeds the farthest reach, you are stuck. This greedy single-pass solution outperforms DP for feasibility.
**The Twist:** You do not need the minimum jumps — just whether the end is reachable. This makes greedy valid; for minimum jumps you need a BFS/greedy hybrid (Jump Game II).
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

### 3. LeetCode 763. Partition Labels
**Archetype:** 15.3 Partition/Rearrange
**Type:** Warm-Up
**Statement:** Partition a string into as many parts as possible so that each letter appears in only one part. Return the sizes.
**Why it fits:** First pass records the last occurrence of each character. Second pass greedily expands the current partition to cover all last occurrences of characters seen so far. When the scan index reaches the boundary, cut.
**The Twist:** The partition boundary is determined by the maximum last-occurrence of all characters in the current window, not just the current character.
**Code Skeleton:**
```python
def partitionLabels(s: str) -> list[int]:
    last = {ch: i for i, ch in enumerate(s)}
    result = []
    start = end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:
            result.append(end - start + 1)
            start = i + 1
    return result
```

---

### 4. LeetCode 122. Best Time to Buy and Sell Stock II
**Archetype:** 15.4 Two-Choice Greedy
**Type:** Warm-Up
**Statement:** Maximize profit with unlimited transactions. You must sell before buying again.
**Why it fits:** The greedy choice is to capture every upward price movement. Summing all positive daily differences is optimal because there is no transaction cost or limit.
**The Twist:** The two choices (hold or sell) collapse into a simple sum because unlimited transactions remove the constraint that makes stock problems hard.
**Code Skeleton:**
```python
def maxProfit(prices: list[int]) -> int:
    profit = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            profit += prices[i] - prices[i - 1]
    return profit
```

---

### 5. LeetCode 406. Queue Reconstruction by Height
**Archetype:** 15.5 Queue/Line Problems
**Type:** Warm-Up
**Statement:** Reconstruct a queue from a list of people `[h, k]` where `k` is the number of people in front with height >= h.
**Why it fits:** Sort by descending height, then ascending k. Greedily insert each person at index `k`. Taller people are placed first so shorter people do not affect their k-count.
**The Twist:** The sorting order is double-key (height desc, k asc). The insertion index is exactly `k` because all previously placed people are taller.
**Code Skeleton:**
```python
def reconstructQueue(people: list[list[int]]) -> list[list[int]]:
    people.sort(key=lambda x: (-x[0], x[1]))
    result = []
    for h, k in people:
        result.insert(k, [h, k])
    return result
```

---

## Core Drills

### 6. LeetCode 45. Jump Game II
**Archetype:** 15.2 Jump Game
**Type:** Core Drill
**Statement:** Given max jump lengths, find the minimum number of jumps to reach the last index.
**Why it fits:** Greedy BFS on a level-by-level basis. Track the farthest reachable index of the current jump range. When the scan hits the end of the current range, increment jumps and expand the range.
**The Twist:** This is not Dijkstra — it is a greedy level expansion because all edges have weight 1. The farthest variable acts as the boundary of the next BFS level.
**Code Skeleton:**
```python
def jump(nums: list[int]) -> int:
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

### 7. LeetCode 452. Minimum Number of Arrows to Burst Balloons
**Archetype:** 15.1 Interval Scheduling
**Type:** Core Drill
**Statement:** Given balloons as horizontal intervals, find the minimum arrows needed to burst all of them. An arrow at x bursts any balloon where `start <= x <= end`.
**Why it fits:** Sort by end coordinate, then shoot an arrow at the end of the first balloon. Skip all balloons burst by that arrow. This is identical to interval scheduling but framed as "points covering intervals."
**The Twist:** Overlapping intervals can be burst by a single arrow placed at the rightmost start of the overlap region. Sorting by end time ensures you do not miss balloons that end early.
**Code Skeleton:**
```python
def findMinArrowShots(points: list[list[int]]) -> int:
    if not points:
        return 0
    points.sort(key=lambda x: x[1])
    arrows = 1
    end = points[0][1]
    for i in range(1, len(points)):
        if points[i][0] > end:
            arrows += 1
            end = points[i][1]
    return arrows
```

---

### 8. LeetCode 134. Gas Station
**Archetype:** 15.3 Partition/Rearrange
**Type:** Core Drill
**Statement:** Given gas and cost arrays for a circular route, find the starting gas station index if you can travel around the circuit once.
**Why it fits:** Track total gas minus total cost. If the total is negative, no solution exists. Otherwise, greedily find the starting point by resetting whenever the tank goes negative.
**The Twist:** The route is circular, so a local deficit cannot be recovered by backtracking. The proof that resetting at `i+1` after a deficit at `i` is safe is a common interview follow-up.
**Code Skeleton:**
```python
def canCompleteCircuit(gas: list[int], cost: list[int]) -> int:
    total_tank = curr_tank = 0
    start = 0
    for i in range(len(gas)):
        total_tank += gas[i] - cost[i]
        curr_tank += gas[i] - cost[i]
        if curr_tank < 0:
            start = i + 1
            curr_tank = 0
    return start if total_tank >= 0 else -1
```

---

### 9. LeetCode 135. Candy
**Archetype:** 15.5 Queue/Line Problems / 15.3 Partition/Rearrange
**Type:** Core Drill
**Statement:** Distribute candies to children in a line such that each child with a higher rating than their neighbor gets more candies. Minimize total candies.
**Why it fits:** A single left-to-right or right-to-left pass is insufficient. Two passes are needed: left-to-right to satisfy `rating[i] > rating[i-1]`, then right-to-left for `rating[i] > rating[i+1]`. Each child gets the max of the two passes.
**The Twist:** The two-pass greedy is necessary because local constraints propagate in both directions. A single pass fails on peaks and valleys.
**Code Skeleton:**
```python
def candy(ratings: list[int]) -> int:
    n = len(ratings)
    candies = [1] * n
    # Left to right: higher rating than left neighbor gets more
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1
    # Right to left: higher rating than right neighbor gets more
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)
    return sum(candies)
```

---

### 10. LeetCode 646. Maximum Length of Pair Chain
**Archetype:** 15.1 Interval Scheduling
**Type:** Core Drill
**Statement:** Given pairs `[left, right]`, find the longest chain where each pair's left is greater than the previous pair's right.
**Why it fits:** Sort by right endpoint, then greedily pick the next pair whose left is strictly greater than the current end. This maximizes the number of pairs by leaving as much room as possible.
**The Twist:** The chain requires strict inequality (`left > previous_right`), unlike non-overlapping intervals which use `>=`. This small difference affects edge cases with touching intervals.
**Code Skeleton:**
```python
def findLongestChain(pairs: list[list[int]]) -> int:
    pairs.sort(key=lambda x: x[1])
    count = 1
    end = pairs[0][1]
    for i in range(1, len(pairs)):
        if pairs[i][0] > end:
            count += 1
            end = pairs[i][1]
    return count
```

---

### 11. LeetCode 1005. Maximize Sum Of Array After K Negations
**Archetype:** 15.4 Two-Choice Greedy
**Type:** Core Drill
**Statement:** Choose an index and negate `nums[i]` exactly `k` times. Maximize the sum of the array.
**Why it fits:** Greedy strategy: negate the most negative number first. If k remains after all numbers are non-negative, flip the smallest number (which may be zero) the remaining times.
**The Twist:** If k is odd and there is no zero, the smallest positive number will be negated once. Sorting helps but a min-heap gives O(k log n) cleanly.
**Code Skeleton:**
```python
def largestSumAfterKNegations(nums: list[int], k: int) -> int:
    import heapq
    heapq.heapify(nums)
    while k > 0 and nums[0] < 0:
        smallest = heapq.heappop(nums)
        heapq.heappush(nums, -smallest)
        k -= 1
    if k % 2 == 1:
        nums[0] = -nums[0]
    return sum(nums)
```

---

### 12. LeetCode 767. Reorganize String
**Archetype:** 15.3 Partition/Rearrange
**Type:** Core Drill
**Statement:** Rearrange a string so that no two adjacent characters are the same. Return any valid rearrangement.
**Why it fits:** Greedy by character frequency. Place the most frequent character first, alternating with the next most frequent. If the max frequency exceeds `(n + 1) // 2`, it is impossible.
**The Twist:** A max-heap (or sorting) is used to always pick the two highest remaining frequencies. After placing a character, decrement its count and reinsert it if still > 0.
**Code Skeleton:**
```python
def reorganizeString(s: str) -> str:
    from collections import Counter
    import heapq
    counts = Counter(s)
    max_freq = max(counts.values())
    if max_freq > (len(s) + 1) // 2:
        return ""
    heap = [(-cnt, ch) for ch, cnt in counts.items()]
    heapq.heapify(heap)
    result = []
    while len(heap) >= 2:
        cnt1, ch1 = heapq.heappop(heap)
        cnt2, ch2 = heapq.heappop(heap)
        result.extend([ch1, ch2])
        if cnt1 + 1 < 0:
            heapq.heappush(heap, (cnt1 + 1, ch1))
        if cnt2 + 1 < 0:
            heapq.heappush(heap, (cnt2 + 1, ch2))
    if heap:
        result.append(heap[0][1])
    return ''.join(result)
```

---

### 13. LeetCode 621. Task Scheduler
**Archetype:** 15.3 Partition/Rearrange
**Type:** Core Drill
**Statement:** Given tasks and a cooldown n, find the least number of units of time to finish all tasks. Identical tasks must be separated by at least n intervals.
**Why it fits:** Greedy scheduling by frequency. The most frequent task dictates the framework: `(max_count - 1) * (n + 1) + number_of_tasks_with_max_count`. This is the minimum time if no other tasks fill the idle slots.
**The Twist:** If there are enough other tasks to fill all idle slots, the answer is simply `len(tasks)`. You must take the max of the formula and the total task count.
**Code Skeleton:**
```python
def leastInterval(tasks: list[str], n: int) -> int:
    from collections import Counter
    counts = Counter(tasks)
    max_count = max(counts.values())
    max_tasks = sum(1 for v in counts.values() if v == max_count)
    part_count = max_count - 1
    part_length = n + 1
    empty_slots = part_count * (part_length - max_tasks)
    available_tasks = len(tasks) - max_count * max_tasks
    idles = max(0, empty_slots - available_tasks)
    return len(tasks) + idles
```

---

### 14. LeetCode 860. Lemonade Change
**Archetype:** 15.4 Two-Choice Greedy
**Type:** Core Drill
**Statement:** Sell lemonade for $5. Customers pay with $5, $10, or $20. Return True if you can provide correct change for every customer.
**Why it fits:** Greedy: always prefer giving one $10 + one $5 for $20 change rather than three $5s. This preserves smaller bills for future $10 change requests.
**The Twist:** The greedy choice for $20 change is the only non-trivial decision. Tracking just the counts of $5 and $10 bills is sufficient.
**Code Skeleton:**
```python
def lemonadeChange(bills: list[int]) -> bool:
    five = ten = 0
    for bill in bills:
        if bill == 5:
            five += 1
        elif bill == 10:
            if five == 0:
                return False
            five -= 1
            ten += 1
        else:  # bill == 20
            if ten > 0 and five > 0:
                ten -= 1
                five -= 1
            elif five >= 3:
                five -= 3
            else:
                return False
    return True
```

---

### 15. LeetCode 738. Monotone Increasing Digits
**Archetype:** 15.4 Two-Choice Greedy / 15.3 Partition/Rearrange
**Type:** Core Drill
**Statement:** Given a non-negative integer N, find the largest number less than or equal to N with monotone increasing digits.
**Why it fits:** Scan left to right. When a digit drops (`digits[i] < digits[i-1]`), decrease the previous digit by 1 and set all following digits to 9. This is a digit-level greedy with a single correction pass.
**The Twist:** The correction might propagate leftwards (e.g., 332 becomes 329, then 299). You need to track the position of the leftmost drop and fill 9s from there onward.
**Code Skeleton:**
```python
def monotoneIncreasingDigits(n: int) -> int:
    digits = list(str(n))
    mark = len(digits)
    for i in range(len(digits) - 1, 0, -1):
        if digits[i] < digits[i - 1]:
            mark = i
            digits[i - 1] = str(int(digits[i - 1]) - 1)
    for i in range(mark, len(digits)):
        digits[i] = '9'
    return int(''.join(digits))
```

---

## Checklist
- [ ] Can prove why sorting by end time works for intervals
- [ ] Can explain the two-pass greedy for Candy
- [ ] Can derive the idle-slot formula for Task Scheduler
- [ ] Can recognize when greedy fails and DP is needed
- [ ] Can handle circular greedy problems (Gas Station)
