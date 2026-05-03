# Pattern 15: Greedy

> **Pattern Recognition:** When you see "minimum intervals", "maximum non-overlapping", "always pick cheapest", "local optimal", "activity selection" — think greedy.
>
> **Fundamental Insight:** Greedy makes the locally optimal choice at each step, hoping it leads to global optimum. It works when the problem has the "greedy choice property" — a global optimum can be reached by choosing local optima.

---

## Archetype 15.1: Interval Scheduling

### Recognition Signal
Words: **"non-overlapping", "meeting rooms", "erase overlaps", "maximum intervals"**

### Core Idea
Sort by end time. Pick the interval that ends earliest, then the next that starts after that.

### Template
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

### Problems
- Non-overlapping Intervals (LeetCode 435)
- Minimum Number of Arrows to Burst Balloons (LeetCode 452)
- Maximum Length of Pair Chain (LeetCode 646)

---

## Archetype 15.2: Jump Game

### Recognition Signal
Words: **"jump", "reach end", "minimum jumps", "maximum reach"**

### Problems
- Jump Game (LeetCode 55) — can reach?
- Jump Game II (LeetCode 45) — min jumps (greedy BFS)

**Jump Game II greedy:**
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

---

## Archetype 15.3: Partition / Rearrange

### Recognition Signal
Words: **"partition labels", "reorganize", "string", "groups"**

### Problems
- Partition Labels (LeetCode 763)
- Reorganize String (LeetCode 767) — also heap
- Gas Station (LeetCode 134)
- Candy (LeetCode 135) — two-pass greedy

---

## Archetype 15.4: Two-Choice Greedy

### Recognition Signal
Words: **"best time to buy/sell", "max profit", "unlimited transactions"**

### Problems
- Best Time to Buy and Sell Stock II (LeetCode 122)
- Maximize Sum Of Array After K Negations (LeetCode 1005)

---

## Archetype 15.5: Queue / Line Problems

### Recognition Signal
Words: **"queue", "reconstruction", "height", "order", "k people"**

### Problems
- Queue Reconstruction by Height (LeetCode 406)
- Candy (LeetCode 135)

---

## Mastery Checklist
- [ ] Interval scheduling: sort by end time
- [ ] Jump game: greedy BFS
- [ ] Partition labels: last occurrence tracking
- [ ] Gas station: check if total gas >= total cost
- [ ] Queue reconstruction: sort by height descending, insert by k

---

## When Greedy Works

**Greedy works when:**
1. Optimal substructure: optimal solution contains optimal sub-solutions
2. Greedy choice property: local optimal leads to global optimal

**Test if greedy works:** Try to find a counterexample where greedy fails.

**Famous greedy algorithms:**
- Dijkstra's shortest path
- Prim's / Kruskal's MST
- Huffman coding
- Activity selection

---

## Common Traps

**Trap:** Assuming greedy works when it doesn't.
- Fix: Always verify with a counterexample. If unsure, use DP.

**Trap:** Sorting by wrong key.
- Fix: For intervals, usually sort by end time (not start time).

**Trap:** Forgetting edge cases (empty input, single element).
- Fix: Handle explicitly.

**Near Miss: 0/1 Knapsack**
- Greedy by value/weight ratio fails for 0/1 knapsack
- Must use DP
- Fractional knapsack can use greedy
