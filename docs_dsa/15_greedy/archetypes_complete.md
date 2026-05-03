# Pattern 15: Greedy — Complete Archetype Map

> **Pattern Recognition:** When you see "maximum", "minimum", "schedule", "interval", "jump", "partition", "rearrange" and a proof sketch that a local optimal choice leads to global optimum — think greedy.
>
> **Fundamental Insight:** Greedy algorithms make the locally optimal choice at each step with the hope of finding a global optimum. They work when the problem has the "greedy choice property" and "optimal substructure." If you cannot prove the greedy property, use DP or backtracking instead.

---

## Archetype 15.1: Interval Scheduling

### Recognition Signal (10 seconds)
Words: **"non-overlapping", "meeting rooms", "schedule", "erase", "minimum intervals", "maximum number of events"**

The question: **"Select the maximum number of non-overlapping intervals, or remove the minimum to eliminate overlaps."**

### Core Structure
```python
def interval_scheduling(intervals):
    # Sort by end time (ascending)
    intervals.sort(key=lambda x: x[1])
    
    count = 0
    last_end = float('-inf')
    
    for start, end in intervals:
        if start >= last_end:
            count += 1
            last_end = end
    
    return count
```

### The Invariant
After processing the first `k` intervals, we have selected the maximum possible non-overlapping subset among them. By always picking the interval that ends earliest, we leave the most room for future intervals. This is the greedy choice property.

### Canonical Problem: Non-overlapping Intervals (LeetCode 435)
**Statement:** Given an array of intervals, return the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping.

```python
def erase_overlap_intervals(intervals):
    if not intervals:
        return 0
    
    # Sort by end time ascending
    intervals.sort(key=lambda x: x[1])
    
    keep = 1  # Always keep the first interval
    last_end = intervals[0][1]
    
    for i in range(1, len(intervals)):
        start, end = intervals[i]
        if start >= last_end:
            # No overlap, keep this interval
            keep += 1
            last_end = end
        # else: overlap, remove this interval (skip it)
    
    return len(intervals) - keep
```

### Variation Family

**V1: Minimum Number of Arrows to Burst Balloons (LeetCode 452)**
- **Twist:** Points on a line, each balloon spans an interval. One arrow at position x bursts all balloons covering x. Minimize arrows.
- **Change:** Sort by end. Shoot arrow at `last_end` of first balloon. Burst all overlapping. Move to next non-overlapping.
- **Key insight:** Equivalent to finding maximum overlapping groups; one arrow per group endpoint.

```python
def find_min_arrow_shots(points):
    if not points:
        return 0
    
    points.sort(key=lambda x: x[1])
    arrows = 1
    last_end = points[0][1]
    
    for start, end in points[1:]:
        if start > last_end:
            arrows += 1
            last_end = end
    
    return arrows
```

**V2: Merge Intervals (LeetCode 56)**
- **Twist:** Merge all overlapping intervals into disjoint intervals
- **Change:** Sort by start time. Iterate and merge if current.start <= last_merged.end.
- **Key insight:** Sorting by start makes merging linear. Greedy in the sense that we merge greedily as we go.

**V3: Video Stitching (LeetCode 1024)**
- **Twist:** Cover [0, T] with minimum clips. Each clip is an interval.
- **Change:** Sort by start time. Greedily extend coverage as far as possible with clips starting within current coverage.
- **Key insight:** Similar to jump game on intervals. At each step, pick the clip that starts within reach and ends farthest.

**V4: Maximum Length of Pair Chain (LeetCode 646)**
- **Twist:** Form longest chain of pairs where each next pair starts after previous ends
- **Change:** Sort by second element. Same as interval scheduling.
- **Key insight:** This IS the classic interval scheduling problem restated.

**Near Miss: Meeting Rooms II (LeetCode 253)**
- **Looks like:** Interval scheduling
- **But:** Requires a min-heap to track end times of ongoing meetings. Not a simple greedy pick; needs a priority queue.
- **Lesson:** When intervals can run in parallel (not just sequential selection), the greedy structure changes.

---

## Archetype 15.2: Jump Game

### Recognition Signal (10 seconds)
Words: **"jump", "reach end", "minimum jumps", "furthest", "can reach", "max reach"**

The question: **"From each position, you can jump forward up to nums[i] steps. Can you reach the end? What's the minimum jumps?"**

### Core Structure
```python
def jump_game(nums):
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False  # Cannot reach this position
        max_reach = max(max_reach, i + jump)
    return True
```

### The Invariant
At each index `i`, `max_reach` stores the furthest index we can reach from any position `0..i`. If `i > max_reach`, the current position is unreachable. By greedily updating `max_reach`, we never miss a better path.

### Canonical Problem: Jump Game II (LeetCode 45)
**Statement:** Given an array of non-negative integers `nums`, you are initially positioned at the first index. Each element represents your maximum jump length at that position. Return the minimum number of jumps to reach the last index.

```python
def jump(nums):
    if len(nums) <= 1:
        return 0
    
    jumps = 0
    current_end = 0  # Furthest we can reach with current number of jumps
    farthest = 0     # Furthest we can reach with one more jump
    
    for i in range(len(nums) - 1):  # Don't need to jump from last index
        farthest = max(farthest, i + nums[i])
        
        if i == current_end:
            jumps += 1
            current_end = farthest
            
            # Early exit: if we can already reach the end
            if current_end >= len(nums) - 1:
                break
    
    return jumps
```

### Variation Family

**V1: Jump Game (LeetCode 55)**
- **Twist:** Just determine if you can reach the last index
- **Change:** Single pass tracking `max_reach`. Return False if `i > max_reach`.
- **Key insight:** Simpler version. Only need boolean result.

```python
def can_jump(nums):
    max_reach = 0
    for i, n in enumerate(nums):
        if i > max_reach:
            return False
        max_reach = max(max_reach, i + n)
    return True
```

**V2: Jump Game III (LeetCode 1306)**
- **Twist:** Can jump left or right by `arr[i]` from starting index. Can you reach value 0?
- **Change:** BFS/DFS with visited set. Not greedy because direction matters and you can revisit if not careful.
- **Key insight:** When movement is bidirectional, greedy fails. Use graph traversal.

**V3: Jump Game V (LeetCode 1340)**
- **Twist:** Jump to any index within distance `d` that has a lower value. Maximize number of indices visited.
- **Change:** DP with monotonic deque optimization. `dp[i] = 1 + max(dp[j])` for valid j.
- **Key insight:** Greedy doesn't work because local choices affect future options. Needs DP.

**V4: Jump Game VI (LeetCode 1696)**
- **Twist:** Each jump costs `nums[j]`. Maximize score reaching end with jumps up to length `k`.
- **Change:** DP with monotonic deque. `dp[i] = nums[i] + max(dp[i-k:i])`.
- **Key insight:** Sliding window maximum on DP states. Greedy fails because future high values may require current low values.

**Near Miss: Frog Jump (LeetCode 403)**
- **Looks like:** Jump game
- **But:** Next jump length is k-1, k, or k+1 from previous jump. Requires DP or DFS with memoization.
- **Lesson:** When jump length depends on previous jump, greedy local choice is insufficient.

---

## Archetype 15.3: Partition / Rearrange

### Recognition Signal (10 seconds)
Words: **"partition", "rearrange", "group", "labels", "segments", "into parts", "reorganize"**

The question: **"Split array/string into segments where each segment satisfies a property (all chars appear only in this segment, etc.)."**

### Core Structure
```python
def partition_labels(s):
    # Record last occurrence of each character
    last = {c: i for i, c in enumerate(s)}
    
    partitions = []
    start = end = 0
    
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:
            partitions.append(end - start + 1)
            start = i + 1
    
    return partitions
```

### The Invariant
As we scan left to right, `end` tracks the furthest position any character in the current partition reaches. When `i == end`, all characters in `[start, end]` are contained within this segment, so we can cut here. The greedy choice is to make the earliest valid cut.

### Canonical Problem: Partition Labels (LeetCode 763)
**Statement:** You are given a string `s`. We want to partition the string into as many parts as possible so that each letter appears in at most one part. Return a list of integers representing the size of these parts.

```python
def partition_labels(s):
    # last[c] = last index where character c appears
    last = {c: i for i, c in enumerate(s)}
    
    partitions = []
    start = 0
    end = 0
    
    for i, c in enumerate(s):
        # Extend current partition if this character appears later
        end = max(end, last[c])
        
        # If we've reached the end of all characters in this partition, cut
        if i == end:
            partitions.append(end - start + 1)
            start = i + 1
    
    return partitions
```

### Variation Family

**V1: Reorganize String (LeetCode 767)**
- **Twist:** Rearrange string so no two adjacent characters are the same
- **Change:** Greedy by frequency. Place most frequent char at even indices, then fill odd indices.
- **Key insight:** If max frequency > (n+1)/2, impossible. Otherwise, greedy placement works.

```python
def reorganize_string(s):
    from collections import Counter
    count = Counter(s)
    max_count = max(count.values())
    
    if max_count > (len(s) + 1) // 2:
        return ""
    
    # Sort by frequency descending
    chars = sorted(count.keys(), key=lambda x: -count[x])
    result = [''] * len(s)
    idx = 0
    
    for c in chars:
        for _ in range(count[c]):
            result[idx] = c
            idx += 2
            if idx >= len(s):
                idx = 1
    
    return ''.join(result)
```

**V2: Task Scheduler (LeetCode 621)**
- **Twist:** Schedule tasks with cooling interval n between same tasks. Minimize total time.
- **Change:** Greedy: schedule most frequent task first, fill gaps with other tasks. Formula: max(len(tasks), (max_freq - 1) * (n + 1) + max_freq_count).
- **Key insight:** Greedy arrangement by frequency creates the minimum idle time.

**V3: Rearrange String k Distance Apart (LeetCode 358)**
- **Twist:** Rearrange string so same characters are at least k apart
- **Change:** Greedy with cooldown tracking. Place most frequent available char that is not in cooldown.
- **Key insight:** Extension of V1 with arbitrary distance constraint. Needs max-heap + wait queue.

**V4: String Without AAA or BBB (LeetCode 984)**
- **Twist:** Construct string with A's and B's without "AAA" or "BBB"
- **Change:** Greedy: append the character with higher remaining count, but break ties by avoiding triple repeats.
- **Key insight:** Local choice based on remaining counts and last two characters.

**Near Miss: Palindrome Partitioning (LeetCode 131)**
- **Looks like:** Partition string
- **But:** Need to find ALL valid palindrome partitions. Backtracking required, not greedy.
- **Lesson:** When the problem asks for "all ways" or exact partitions with a complex property, greedy usually fails.

---

## Archetype 15.4: Two-Choice Greedy

### Recognition Signal (10 seconds)
Words: **"gas station", "circuit", "circular", "two choices", "lemonade change", "valid starting point"**

The question: **"Make a choice between two options at each step, and prove the greedy choice maintains feasibility."**

### Core Structure
```python
def two_choice_greedy(choices):
    # Often involves tracking a running balance or deficit
    balance = 0
    start = 0
    
    for i, (cost, gain) in enumerate(choices):
        balance += gain - cost
        if balance < 0:
            # Cannot start from any station in [start, i]
            start = i + 1
            balance = 0
    
    return start
```

### The Invariant
If the total gas is greater than or equal to total cost, a solution exists. The greedy insight: if we cannot complete the circuit from station `i`, we cannot start from any station `j` in `[i, current]` either, because they would have even less gas. So we jump `start` to `current + 1`.

### Canonical Problem: Gas Station (LeetCode 134)
**Statement:** There are `n` gas stations along a circular route. Given two integer arrays `gas` and `cost`, return the starting gas station's index if you can travel around the circuit once in the clockwise direction, otherwise return `-1`.

```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1  # Total gas insufficient, impossible
    
    total = 0
    start = 0
    
    for i in range(len(gas)):
        total += gas[i] - cost[i]
        if total < 0:
            # Cannot reach station i+1 from start
            # Any station in [start, i] is also invalid
            start = i + 1
            total = 0
    
    return start
```

### Variation Family

**V1: Lemonade Change (LeetCode 860)**
- **Twist:** Sell lemonade for $5. Customers pay $5, $10, or $20. Can you make correct change?
- **Change:** Greedy: keep count of $5 and $10 bills. For $20, prefer giving $10 + $5 over three $5s.
- **Key insight:** $5 bills are more versatile, so save them. Greedy change-making works for this denomination set.

```python
def lemonade_change(bills):
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

**V2: Boats to Save People (LeetCode 881)**
- **Twist:** Each boat has limit. Pair heaviest with lightest if possible.
- **Change:** Sort. Two pointers. If `light + heavy <= limit`, boat both. Else heavy alone.
- **Key insight:** Always try to pair the heaviest remaining person. If they can't pair with the lightest, they must go alone.

**V3: Minimum Number of Taps to Open to Water a Garden (LeetCode 1326)**
- **Twist:** Taps cover intervals. Cover [0, n] with minimum taps.
- **Change:** Convert to jump game. Each tap gives a reach interval. Greedy extend coverage.
- **Key insight:** Preprocess taps into max reach at each point, then apply jump game greedy.

**V4: Valid Parenthesis String (LeetCode 678)**
- **Twist:** String contains `(`, `)`, and `*`. `*` can be `(`, `)`, or empty. Is string valid?
- **Change:** Greedy balance range. Track min and max possible open count. Valid if min can reach 0.
- **Key insight:** Greedy tracking of balance bounds handles the three choices of `*` efficiently.

**Near Miss: Candy (LeetCode 135)**
- **Looks like:** Greedy local choice
- **But:** Requires two-pass greedy (left-to-right then right-to-left). Single-pass greedy fails.
- **Lesson:** Some problems need multi-directional greedy. Don't assume one pass is always enough.

---

## Archetype 15.5: Queue / Line Problems

### Recognition Signal (10 seconds)
Words: **"queue", "reconstruct", "height", "line", "order", "greedy by attribute", "standing", "front"**

The question: **"Arrange people/objects in a line based on two attributes, using greedy insertion."**

### Core Structure
```python
def queue_reconstruction(people):
    # Sort by height descending, then by k ascending
    people.sort(key=lambda x: (-x[0], x[1]))
    
    result = []
    for height, k in people:
        # Insert at position k
        result.insert(k, (height, k))
    
    return result
```

### The Invariant
By sorting people from tallest to shortest, when we insert a person at position `k`, all people already in the result are taller or equal. So inserting at index `k` guarantees exactly `k` taller people in front. Shorter people inserted later do not affect this count.

### Canonical Problem: Queue Reconstruction by Height (LeetCode 406)
**Statement:** You are given an array of people, where `people[i] = [hi, ki]` represents the `i-th` person of height `hi` with exactly `ki` other people in front who have a height greater than or equal to `hi`. Reconstruct and return the queue.

```python
def reconstruct_queue(people):
    # Sort by height descending, then k ascending
    people.sort(key=lambda x: (-x[0], x[1]))
    
    result = []
    for height, k in people:
        result.insert(k, [height, k])
    
    return result
```

### Variation Family

**V1: Dota2 Senate (LeetCode 649)**
- **Twist:** Radiant and Dire senators ban each other in round-robin. Predict winner.
- **Change:** Two queues. Greedy: each senator bans the next opposing senator. Process in order.
- **Key insight:** Queue-based simulation of greedy banning. Senators act in round-roban order.

```python
def predict_party_victory(senate):
    from collections import deque
    n = len(senate)
    radiant = deque()
    dire = deque()
    
    for i, s in enumerate(senate):
        if s == 'R':
            radiant.append(i)
        else:
            dire.append(i)
    
    while radiant and dire:
        r = radiant.popleft()
        d = dire.popleft()
        if r < d:
            radiant.append(r + n)
        else:
            dire.append(d + n)
    
    return "Radiant" if radiant else "Dire"
```

**V2: Reveal Cards In Increasing Order (LeetCode 950)**
- **Twist:** Reveal cards in increasing order using a specific dealing process
- **Change:** Simulate backwards. Start with sorted deck. Insert next largest card at front, then move last card to front.
- **Key insight:** Reverse simulation reveals the greedy construction pattern.

**V3: Number of Students Unable to Eat Lunch (LeetCode 1700)**
- **Twist:** Students prefer certain sandwiches. First student takes top sandwich if preference matches; otherwise goes to end of queue.
- **Change:** Count preferences. If no student wants the top sandwich, break.
- **Key insight:** Greedy simulation. Track counts to avoid actual queue operations for efficiency.

**V4: Time Needed to Buy Tickets (LeetCode 2073)**
- **Twist:** Queue of people buying tickets. Each person buys one ticket at a time. How long until person at index k finishes?
- **Change:** Math instead of simulation. Time = sum(min(tickets[i], tickets[k]) for i <= k) + sum(min(tickets[i], tickets[k] - 1) for i > k).
- **Key insight:** Greedy observation: people before k go `tickets[k]` times, people after k go `tickets[k] - 1` times.

**Near Miss: Design Circular Queue (LeetCode 622)**
- **Looks like:** Queue problem
- **But:** Pure data structure implementation. No greedy algorithm involved.
- **Lesson:** Not every queue mention is a greedy queue problem. Look for ordering/insertion/reconstruction keywords.

---

## Pattern 15 Mastery Checklist

Before moving to Pattern 16, confirm you can:

- [ ] Interval scheduling: sort by end time, greedily pick non-overlapping
- [ ] Jump game: track max_reach or farthest in current jump range
- [ ] Partition labels: scan and extend partition to last occurrence
- [ ] Gas station: reset start when balance drops below zero
- [ ] Queue reconstruction: sort by height desc, k asc; insert at position k
- [ ] Prove when greedy works: greedy choice property + optimal substructure
- [ ] Recognize when greedy fails: need to try all choices (use DP/backtracking)
- [ ] Distinguish: greedy interval pick vs heap-based meeting rooms

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Sorting intervals by start instead of end | More removals than necessary | Sort by end time for selection; by start time for merging |
| Resetting jump count at wrong boundary | Wrong minimum jumps | Only increment jumps when `i == current_end` |
| Using greedy when DP is needed | Wrong answer on counterexamples | Test with small examples; if local choice blocks future optimal, use DP |
| Forgetting to check total feasibility in gas station | Returns invalid start index | First check `sum(gas) >= sum(cost)` |
| One-pass greedy when two-pass is needed | Wrong candy distribution or mountain array | Some problems require left-to-right and right-to-left passes |
| Confusing "minimum remove" with "minimum arrows" | Wrong logic | Arrows burst ALL overlapping; removals select a subset |

---

## Pattern Blends (What Comes Next)

Greedy does not live in isolation. It blends with:

- **Two Pointers:** Boats to save people, container with most water
- **Heap / Priority Queue:** Task scheduler, meeting rooms II, rearrange string k distance apart
- **DP:** Jump game V/VI, valid parenthesis string can also be solved with DP
- **Intervals:** Merge intervals, non-overlapping intervals, video stitching
- **Sorting:** Almost every greedy problem starts with sorting by some key

---

*Next: Pattern 16 — Intervals*
