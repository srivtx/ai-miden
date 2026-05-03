# Pattern 15: Greedy — Drills Part 3

> **5 Near Misses + 5 Pattern Blends + 5 Interview Simulation**
> Focus: Recognize greedy when it is disguised, blended with other patterns, or requires proof in an interview.

---

## Near Misses

### 1. LeetCode 605. Can Place Flowers
**Archetype:** 15.3 Partition/Rearrange
**Type:** Near Miss
**Statement:** Given a flowerbed array (0 = empty, 1 = planted), determine if n new flowers can be planted without adjacent flowers.
**Why it fits:** It looks like a greedy placement problem, but the greedy choice is trivial: plant at every valid spot as early as possible. The near miss is overcomplicating it with DP or backtracking.
**The Twist:** The edge cases at index 0 and index n-1 only need one neighbor check. The greedy choice is so simple that candidates sometimes look for a hidden constraint.
**Code Skeleton:**
```python
def canPlaceFlowers(flowerbed: list[int], n: int) -> bool:
    count = 0
    i = 0
    while i < len(flowerbed):
        if flowerbed[i] == 0:
            left = (i == 0) or (flowerbed[i - 1] == 0)
            right = (i == len(flowerbed) - 1) or (flowerbed[i + 1] == 0)
            if left and right:
                flowerbed[i] = 1
                count += 1
                if count >= n:
                    return True
        i += 1
    return count >= n
```

---

### 2. LeetCode 942. DI String Match
**Archetype:** 15.3 Partition/Rearrange / 15.5 Queue/Line Problems
**Type:** Near Miss
**Statement:** Given a string of 'D' (decrease) and 'I' (increase), return a permutation of `[0..n]` that satisfies the pattern.
**Why it fits:** Greedy construction: use the smallest remaining number for 'I' and the largest remaining for 'D'. This ensures the next element can always satisfy the constraint.
**The Twist:** The permutation length is `n+1` for a pattern of length `n`. The greedy choice is obvious in hindsight but requires trusting that extreme values always work.
**Code Skeleton:**
```python
def diStringMatch(s: str) -> list[int]:
    lo, hi = 0, len(s)
    result = []
    for ch in s:
        if ch == 'I':
            result.append(lo)
            lo += 1
        else:
            result.append(hi)
            hi -= 1
    result.append(lo)
    return result
```

---

### 3. LeetCode 11. Container With Most Water
**Archetype:** 15.4 Two-Choice Greedy
**Type:** Near Miss
**Statement:** Given heights, find two lines that form a container holding the most water.
**Why it fits:** The two-pointer greedy approach starts at both ends and moves the shorter line inward. The near miss is trying O(n^2) brute force or a complex stack approach.
**The Twist:** Moving the taller line inward can never increase the area because the width shrinks and the height is bounded by the shorter line. This proof is a common interview requirement.
**Code Skeleton:**
```python
def maxArea(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_area = 0
    while left < right:
        width = right - left
        if height[left] < height[right]:
            max_area = max(max_area, height[left] * width)
            left += 1
        else:
            max_area = max(max_area, height[right] * width)
            right -= 1
    return max_area
```

---

### 4. LeetCode 179. Largest Number
**Archetype:** 15.3 Partition/Rearrange
**Type:** Near Miss
**Statement:** Given integers, arrange them to form the largest possible number.
**Why it fits:** The greedy choice is a custom sort: `a+b > b+a`. Numbers are sorted by this comparator and concatenated. The near miss is standard numeric sorting or digit-based sorting.
**The Twist:** All inputs can be zeros (e.g., `[0, 0]`), so the output must be "0" not "00". The custom comparator must be applied carefully in Python using `functools.cmp_to_key`.
**Code Skeleton:**
```python
def largestNumber(nums: list[int]) -> str:
    from functools import cmp_to_key
    def compare(a, b):
        if a + b > b + a:
            return -1
        elif a + b < b + a:
            return 1
        return 0
    strs = sorted([str(n) for n in nums], key=cmp_to_key(compare))
    result = ''.join(strs)
    return '0' if result[0] == '0' else result
```

---

### 5. LeetCode 56. Merge Intervals
**Archetype:** 15.1 Interval Scheduling
**Type:** Near Miss
**Statement:** Given intervals, merge all overlapping intervals.
**Why it fits:** Sort by start time, then greedily extend the current merged interval as long as overlaps continue. This is a prerequisite for almost all interval DP/greedy problems.
**The Twist:** It is so fundamental that candidates often rush and forget to sort, or mishandle the case where one interval completely contains another.
**Code Skeleton:**
```python
def merge(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    result = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
```

---

## Pattern Blends

### 6. LeetCode 2335. Minimum Amount of Time to Fill Cups
**Archetype:** 15.3 Partition/Rearrange + 15.4 Two-Choice Greedy
**Type:** Pattern Blend
**Statement:** Given three integers representing cold, warm, and hot water cups, find the minimum seconds to fill all cups. You can fill up to 2 different cups per second.
**Why it fits:** The greedy strategy is to always fill the two cup types with the most remaining. If one type dominates, the answer is simply its count. Otherwise, the time is `ceil(total / 2)`.
**The Twist:** The blend of counting and two-choice greedy means you must check if the largest count exceeds the sum of the other two — a tie-break condition that changes the formula.
**Code Skeleton:**
```python
def fillCups(amount: list[int]) -> int:
    amount.sort()
    # If the largest is greater than or equal to sum of others, answer is largest
    if amount[2] >= amount[0] + amount[1]:
        return amount[2]
    # Otherwise we can pair them up almost perfectly
    return (sum(amount) + 1) // 2
```

---

### 7. LeetCode 1578. Minimum Time to Make Rope Colorful
**Archetype:** 15.3 Partition/Rearrange + 15.4 Two-Choice Greedy
**Type:** Pattern Blend
**Statement:** Given a string of balloon colors and removal times, remove the minimum total time so that no two adjacent balloons have the same color.
**Why it fits:** Group consecutive same-color balloons. In each group, keep the one with max removal time and remove all others. This blends partition labels with a two-choice (keep/remove) greedy.
**The Twist:** You cannot simply remove all duplicates; you must keep the cheapest-to-keep (most expensive-to-remove) balloon in each run.
**Code Skeleton:**
```python
def minCost(colors: str, neededTime: list[int]) -> int:
    total = 0
    i = 0
    while i < len(colors):
        j = i
        group_sum = group_max = 0
        while j < len(colors) and colors[j] == colors[i]:
            group_sum += neededTime[j]
            group_max = max(group_max, neededTime[j])
            j += 1
        if j - i > 1:
            total += group_sum - group_max
        i = j
    return total
```

---

### 8. LeetCode 1833. Maximum Ice Cream Bars
**Archetype:** 15.4 Two-Choice Greedy + Sorting
**Type:** Pattern Blend
**Statement:** Given costs of ice cream bars and coins, return the maximum number of bars you can buy.
**Why it fits:** Sort costs ascending, then greedily buy the cheapest available until you run out of coins. This is a direct application of the "pick cheapest first" greedy principle.
**The Twist:** The problem is trivial once sorted, but in an interview you should justify why sorting and greedy is optimal (any swap with a more expensive bar would not improve the count).
**Code Skeleton:**
```python
def maxIceCream(costs: list[int], coins: int) -> int:
    costs.sort()
    count = 0
    for cost in costs:
        if coins >= cost:
            coins -= cost
            count += 1
        else:
            break
    return count
```

---

### 9. LeetCode 1405. Longest Happy String
**Archetype:** 15.3 Partition/Rearrange + Priority Queue
**Type:** Pattern Blend
**Statement:** Given counts of a, b, and c, return the longest possible happy string (no three identical consecutive letters).
**Why it fits:** Greedy pick the most frequent remaining character, but do not place it if it would create a triple. Use a max-heap to always access the most frequent. This blends greedy frequency scheduling with heap management.
**The Twist:** You must track the last two placed characters to avoid triples. If the most frequent character would form a triple, temporarily pick the second most frequent.
**Code Skeleton:**
```python
def longestDiverseString(a: int, b: int, c: int) -> str:
    import heapq
    heap = []
    for count, ch in [(-a, 'a'), (-b, 'b'), (-c, 'c')]:
        if count < 0:
            heapq.heappush(heap, (count, ch))
    result = []
    while heap:
        count1, ch1 = heapq.heappop(heap)
        if len(result) >= 2 and result[-1] == result[-2] == ch1:
            if not heap:
                break
            count2, ch2 = heapq.heappop(heap)
            result.append(ch2)
            count2 += 1
            if count2 < 0:
                heapq.heappush(heap, (count2, ch2))
            heapq.heappush(heap, (count1, ch1))
        else:
            result.append(ch1)
            count1 += 1
            if count1 < 0:
                heapq.heappush(heap, (count1, ch1))
    return ''.join(result)
```

---

### 10. LeetCode 2294. Partition Array Such That Maximum Difference Is K
**Archetype:** 15.1 Interval Scheduling + 15.3 Partition/Rearrange
**Type:** Pattern Blend
**Statement:** Given an array and integer k, partition it into the minimum number of subsequences where the difference between max and min in each subsequence is <= k.
**Why it fits:** Sort the array. Greedily extend the current subsequence as long as `current_max - current_min <= k`. When the difference exceeds k, start a new subsequence. This blends sorting with interval partitioning.
**The Twist:** The partition is not about contiguous subarrays — it is about grouping elements after sorting. The greedy proof relies on sorting making the min and max of any group adjacent.
**Code Skeleton:**
```python
def partitionArray(nums: list[int], k: int) -> int:
    nums.sort()
    if not nums:
        return 0
    subsequences = 1
    start = nums[0]
    for num in nums[1:]:
        if num - start > k:
            subsequences += 1
            start = num
    return subsequences
```

---

## Interview Simulation

### 11. LeetCode 502. IPO
**Archetype:** 15.4 Two-Choice Greedy + Heap
**Type:** Interview Sim
**Statement:** Given projects with capital requirements and profits, start with initial capital W. Pick at most k projects to maximize final capital. You can only start a project if you have enough capital.
**Why it fits:** Two-step greedy: sort projects by capital requirement, then use a max-heap to always pick the most profitable project you can afford. Repeat k times.
**The Twist:** The set of affordable projects grows as you gain capital, so a single sort is insufficient. The heap dynamically tracks available projects after each selection.
**Code Skeleton:**
```python
def findMaximizedCapital(k: int, w: int, profits: list[int], capital: list[int]) -> int:
    import heapq
    projects = sorted(zip(capital, profits))
    max_heap = []
    i = 0
    for _ in range(k):
        while i < len(projects) and projects[i][0] <= w:
            heapq.heappush(max_heap, -projects[i][1])
            i += 1
        if not max_heap:
            break
        w += -heapq.heappop(max_heap)
    return w
```

---

### 12. LeetCode 871. Minimum Number of Refueling Stops
**Archetype:** 15.2 Jump Game + Heap
**Type:** Interview Sim
**Statement:** A car travels from position 0 to target with initial fuel. Stations are at positions with fuel amounts. Find the minimum refueling stops needed.
**Why it fits:** This is Jump Game with weighted stations. Greedily drive past stations, pushing their fuel into a max-heap. When you run out of fuel, refuel at the station with the most fuel you passed.
**The Twist:** You do not decide whether to stop at a station when you pass it — you postpone the decision until you actually need fuel, then pick the best station you skipped.
**Code Skeleton:**
```python
def minRefuelStops(target: int, startFuel: int, stations: list[list[int]]) -> int:
    import heapq
    max_heap = []
    stations.append([target, 0])
    fuel = startFuel
    stops = 0
    prev = 0
    for position, gas in stations:
        distance = position - prev
        fuel -= distance
        while fuel < 0 and max_heap:
            fuel += -heapq.heappop(max_heap)
            stops += 1
        if fuel < 0:
            return -1
        heapq.heappush(max_heap, -gas)
        prev = position
    return stops
```

---

### 13. LeetCode 1481. Least Number of Unique Integers after K Removals
**Archetype:** 15.3 Partition/Rearrange + Frequency Analysis
**Type:** Interview Sim
**Statement:** Given an array and integer k, find the least number of unique integers after removing exactly k elements.
**Why it fits:** Greedy removal of the least frequent elements first preserves the most frequent (and thus most unique values). Count frequencies, sort by frequency, and remove until k is exhausted.
**The Twist:** You might not be able to fully remove a frequency group. The greedy is optimal because removing a higher-frequency element never reduces unique count faster than removing a lower-frequency one.
**Code Skeleton:**
```python
def findLeastNumOfUniqueInts(arr: list[int], k: int) -> int:
    from collections import Counter
    freq = Counter(arr)
    # Sort frequencies ascending and greedily remove
    for count in sorted(freq.values()):
        if k >= count:
            k -= count
            del freq[list(freq.keys())[list(freq.values()).index(count)]]
        else:
            break
    # More robust implementation:
    frequencies = sorted(freq.values())
    unique = len(frequencies)
    for count in frequencies:
        if k >= count:
            k -= count
            unique -= 1
        else:
            break
    return unique
```

---

### 14. LeetCode 1963. Minimum Number of Swaps to Make the String Balanced
**Archetype:** 15.3 Greedy Scan
**Type:** Interview Sim
**Statement:** Given a balanced string of brackets with some `]` before `[`, find the minimum swaps to make it balanced.
**Why it fits:** Track the balance of brackets. Every time the balance goes negative, you need a swap. Greedy: the earliest possible swap fixes the most future imbalance.
**The Twist:** You do not need to simulate actual swaps. Counting imbalance depth and using `ceil(imbalance / 2)` gives the answer because one swap fixes two misplaced brackets.
**Code Skeleton:**
```python
def minSwaps(s: str) -> int:
    imbalance = 0
    max_imbalance = 0
    for ch in s:
        if ch == '[':
            imbalance -= 1
        else:
            imbalance += 1
        max_imbalance = max(max_imbalance, imbalance)
    return (max_imbalance + 1) // 2
```

---

### 15. LeetCode 1686. Stone Game VI
**Archetype:** 15.4 Two-Choice Greedy + Game Theory
**Type:** Interview Sim
**Statement:** Alice and Bob take turns removing stones. Each stone has an aliceValue and bobValue. The player gets their value plus the opponent gets the other's value for that stone. Both play optimally. Determine the winner.
**Why it fits:** The combined value of picking stone `i` is `aliceValue[i] + bobValue[i]`. Greedy: always pick the stone with highest combined value. This maximizes your gain relative to the opponent.
**The Twist:** The game is zero-sum in combined value. Sorting by combined value and alternating picks is optimal for both players because each pick denies the opponent that stone's combined value.
**Code Skeleton:**
```python
def stoneGameVI(aliceValues: list[int], bobValues: list[int]) -> int:
    n = len(aliceValues)
    combined = sorted([(aliceValues[i] + bobValues[i], aliceValues[i], bobValues[i]) for i in range(n)], reverse=True)
    alice = bob = 0
    for i in range(n):
        if i % 2 == 0:
            alice += combined[i][1]
        else:
            bob += combined[i][2]
    if alice > bob:
        return 1
    elif alice < bob:
        return -1
    return 0
```

---

## Checklist
- [ ] Can prove greedy choice property for interval problems
- [ ] Can recognize when a heap is needed to augment greedy (IPO, Refueling)
- [ ] Can handle two-pass greedy with proof (Candy, Rope Colorful)
- [ ] Can reduce game theory problems to sorting by combined value
- [ ] Can distinguish greedy feasibility from greedy optimization (Jump Game vs Jump Game II)
