# Pattern 15: Greedy — Practice Problems

## Interval Scheduling

### 435. Non-overlapping Intervals
**Statement:** Min intervals to remove for no overlaps.
**Code:**
```python
def erase_overlap_intervals(intervals):
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

### 452. Minimum Number of Arrows to Burst Balloons
**Statement:** Min arrows to burst all balloons.
**Intuition:** Same as interval scheduling. Sort by end. Shoot at end if next starts after.

### 646. Maximum Length of Pair Chain
**Statement:** Max chain length where pairs[i][0] > pairs[j][1].
**Intuition:** Sort by second element. Greedy chain.

---

## Jump Game

### 55. Jump Game
**Statement:** Can reach last index?
**Intuition:** Greedy. Track max reach.
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
**Statement:** Min jumps.
**Intuition:** Greedy BFS. Track current end and farthest.
**Code:**
```python
def jump(nums):
    jumps = current_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            jumps += 1
            current_end = farthest
    return jumps
```

---

## Partition / Rearrange

### 763. Partition Labels
**Statement:** Partition so each letter appears in at most one part.
**Intuition:** Track last occurrence. When current index == max last occurrence, partition.
**Code:**
```python
def partition_labels(s):
    last = {c: i for i, c in enumerate(s)}
    result = []
    start = end = 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:
            result.append(end - start + 1)
            start = end + 1
    return result
```

### 134. Gas Station
**Statement:** Starting gas station's index to complete circuit.
**Intuition:** If total gas >= total cost, solution exists. Track tank. If negative, start from next station.

### 135. Candy
**Statement:** Min candies. Higher rating gets more than neighbors.
**Intuition:** Two passes. Left to right (higher than left gets more). Right to left (higher than right gets more). Max of both.

---

## Two-Choice

### 122. Best Time to Buy and Sell Stock II
**Statement:** Unlimited transactions.
**Intuition:** Sum all positive differences.

### 1005. Maximize Sum Of Array After K Negations
**Statement:** Flip signs of K elements to maximize sum.
**Intuition:** Flip smallest negatives first. If K remains, flip smallest absolute value (even K: no effect, odd K: subtract 2*min).

---

## Queue

### 406. Queue Reconstruction by Height
**Statement:** Reconstruct queue from [[h,k],...].
**Intuition:** Sort by height descending, then k ascending. Insert at position k.
**Code:**
```python
def reconstruct_queue(people):
    people.sort(key=lambda x: (-x[0], x[1]))
    result = []
    for h, k in people:
        result.insert(k, [h, k])
    return result
```

---

## Mixed Drill Set

1. 435 — Non-overlapping intervals
2. 55 — Jump game
3. 45 — Jump game II
4. 763 — Partition labels
5. 134 — Gas station
6. 122 — Stock II (unlimited)
7. 406 — Queue reconstruction
8. 452 — Burst balloons
9. 135 — Candy
10. 646 — Max pair chain
