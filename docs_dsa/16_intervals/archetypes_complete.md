# Pattern 16: Intervals — Complete Archetype Map

> **Pattern Recognition:** When you see "intervals", "overlapping", "merge", "meeting rooms", "intersection", "remove covered", "schedule" — think interval manipulation.
>
> **Fundamental Insight:** Most interval problems reduce to sorting by start or end time, then sweeping through with a pointer, stack, or heap. The key is understanding how intervals relate: overlap, containment, disjointness, and intersection.

---

## Archetype 16.1: Merge Overlapping

### Recognition Signal (10 seconds)
Words: **"merge intervals", "overlapping", "union", "combine", "collapse", "consolidate"**

The question: **"Given a collection of intervals, merge all overlapping intervals into disjoint intervals."**

### Core Structure
```python
def merge(intervals):
    if not intervals:
        return []
    
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for start, end in intervals[1:]:
        last_end = merged[-1][1]
        if start <= last_end:
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])
    
    return merged
```

### The Invariant
After processing the first `k` intervals, `merged` contains the correct merged representation of those `k` intervals. Because we sort by start time, any future interval that overlaps with the last merged interval must also overlap with the current interval if `start <= last_end`.

### Canonical Problem: Merge Intervals (LeetCode 56)
**Statement:** Given an array of intervals where `intervals[i] = [starti, endi]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

```python
def merge(intervals):
    if not intervals:
        return []
    
    # Sort by start time
    intervals.sort(key=lambda x: x[0])
    
    merged = [intervals[0]]
    
    for i in range(1, len(intervals)):
        start, end = intervals[i]
        last_start, last_end = merged[-1]
        
        if start <= last_end:
            # Overlap: extend the last interval
            merged[-1][1] = max(last_end, end)
        else:
            # No overlap: add new interval
            merged.append([start, end])
    
    return merged
```

### Variation Family

**V1: Insert Interval (LeetCode 57)**
- **Twist:** Insert a new interval into existing non-overlapping sorted intervals, merging if necessary
- **Change:** Find position with binary search or linear scan. Merge overlapping neighbors.
- **Key insight:** Only intervals overlapping with the new one need modification.

```python
def insert(intervals, new_interval):
    result = []
    i = 0
    n = len(intervals)
    
    # Add all intervals before new_interval (no overlap)
    while i < n and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1
    
    # Merge all overlapping intervals
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    result.append(new_interval)
    
    # Add remaining intervals
    while i < n:
        result.append(intervals[i])
        i += 1
    
    return result
```

**V2: Remove Interval (LeetCode 1272)**
- **Twist:** Remove all parts of intervals that overlap with a given interval to be removed
- **Change:** For each interval, if it overlaps with `toBeRemoved`, split or trim.
- **Key insight:** An interval can split into two non-overlapping pieces after removal.

**V3: Employee Free Time (LeetCode 759)**
- **Twist:** Given schedules of multiple employees (each is a list of intervals), find common free time
- **Change:** Flatten all intervals, merge, then find gaps between merged intervals.
- **Key insight:** Free time is the complement of merged busy time.

**V4: Add Bold Tag in String (LeetCode 616)**
- **Twist:** Given words, bold all occurrences in string. Overlapping bolds should merge.
- **Change:** Convert word occurrences to intervals, merge intervals, insert bold tags.
- **Key insight:** String formatting problem disguised as interval merging.

**Near Miss: Non-overlapping Intervals (LeetCode 435)**
- **Looks like:** Merge overlapping
- **But:** Greedy selection to minimize removals, not merging. Sort by end time and count kept intervals.
- **Lesson:** Merging combines; selecting picks a subset. Different goals, different algorithms.

---

## Archetype 16.2: Meeting Rooms

### Recognition Signal (10 seconds)
Words: **"meeting rooms", "minimum rooms", "conference rooms", "scheduling", "simultaneous", "overlap count"**

The question: **"What is the maximum number of overlapping intervals at any point in time?"**

### Core Structure
```python
def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    
    starts = sorted([i[0] for i in intervals])
    ends = sorted([i[1] for i in intervals])
    
    rooms = 0
    end_ptr = 0
    
    for start in starts:
        if start >= ends[end_ptr]:
            # Reuse a room
            end_ptr += 1
        else:
            # Need a new room
            rooms += 1
    
    return rooms
```

### The Invariant
The two-pointer sweep maintains that `rooms` is the number of meetings that have started but not yet ended. When a new meeting starts after the earliest ending meeting, we reuse that room. Otherwise, we need an additional room.

### Canonical Problem: Meeting Rooms II (LeetCode 253)
**Statement:** Given an array of meeting time intervals consisting of start and end times, find the minimum number of conference rooms required.

```python
def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    
    starts = sorted(interval[0] for interval in intervals)
    ends = sorted(interval[1] for interval in intervals)
    
    start_ptr = end_ptr = 0
    rooms = 0
    max_rooms = 0
    
    while start_ptr < len(intervals):
        if starts[start_ptr] < ends[end_ptr]:
            # A new meeting starts before the earliest ends
            rooms += 1
            start_ptr += 1
            max_rooms = max(max_rooms, rooms)
        else:
            # A meeting ended, free up a room
            rooms -= 1
            end_ptr += 1
    
    return max_rooms
```

### Variation Family

**V1: Meeting Rooms (LeetCode 252)**
- **Twist:** Can one person attend all meetings? (Are there NO overlaps?)
- **Change:** Sort by start time. Check if any interval overlaps with previous.
- **Key insight:** Simpler version. Just need to detect any overlap.

```python
def can_attend_meetings(intervals):
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return False
    return True
```

**V2: Car Pooling (LeetCode 1094)**
- **Twist:** Trip requests have [num_passengers, start, end]. Can all trips be completed with capacity?
- **Change:** Sweep line. Add passengers at start, remove at end. Track max concurrent passengers.
- **Key insight:** Convert interval problems to difference array / sweep line events.

```python
def car_pooling(trips, capacity):
    events = []
    for num, start, end in trips:
        events.append((start, num))
        events.append((end, -num))
    
    events.sort()
    current = 0
    for _, change in events:
        current += change
        if current > capacity:
            return False
    return True
```

**V3: Minimum Interval to Include Each Query (LeetCode 1851)**
- **Twist:** Given intervals and queries, for each query find the smallest interval containing it
- **Change:** Sort intervals and queries. Use min-heap of (size, end). Add intervals starting before query, remove expired ones.
- **Key insight:** Sweep line + priority queue. Process queries in sorted order.

**V4: My Calendar III (LeetCode 732)**
- **Twist:** Book events and return the maximum k-booking (maximum overlap at any time)
- **Change:** Sweep line with sorted map / difference array. Track running sum of active events.
- **Key insight:** K-booking is exactly the maximum number of concurrent intervals.

**Near Miss: My Calendar I (LeetCode 729)**
- **Looks like:** Meeting rooms
- **But:** Requires checking for double-booking and inserting in sorted order. Binary search or tree map needed.
- **Lesson:** When intervals must be maintained in a dynamic structure, simple sorting is insufficient.

---

## Archetype 16.3: Interval Intersection

### Recognition Signal (10 seconds)
Words: **"intersection", "common", "overlap between two lists", "intervals A and B", "shared"**

The question: **"Find all overlapping regions between two lists of intervals."**

### Core Structure
```python
def interval_intersection(a, b):
    i = j = 0
    result = []
    
    while i < len(a) and j < len(b):
        start = max(a[i][0], b[j][0])
        end = min(a[i][1], b[j][1])
        
        if start <= end:
            result.append([start, end])
        
        # Move pointer of interval that ends first
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    
    return result
```

### The Invariant
At each step, `a[i]` and `b[j]` are the current candidate intervals. Their intersection (if any) is `[max(starts), min(ends)]`. The interval that ends first cannot intersect with any future intervals from the other list (since they are sorted), so we advance its pointer.

### Canonical Problem: Interval List Intersections (LeetCode 986)
**Statement:** You are given two lists of closed intervals, `firstList` and `secondList`, where `firstList[i] = [starti, endi]` and `secondList[j] = [startj, endj]`. Return the intersection of these two interval lists.

```python
def interval_intersection(first_list, second_list):
    i = j = 0
    result = []
    
    while i < len(first_list) and j < len(second_list):
        a_start, a_end = first_list[i]
        b_start, b_end = second_list[j]
        
        # Intersection exists if max(start) <= min(end)
        start = max(a_start, b_start)
        end = min(a_end, b_end)
        
        if start <= end:
            result.append([start, end])
        
        # Advance the pointer with the smaller end value
        if a_end < b_end:
            i += 1
        else:
            j += 1
    
    return result
```

### Variation Family

**V1: Rectangle Overlap (LeetCode 836)**
- **Twist:** Two rectangles on a plane. Do they overlap?
- **Change:** 2D interval intersection. Overlap if x-intervals intersect AND y-intervals intersect.
- **Key insight:** Rectangle overlap is just interval intersection in two dimensions.

```python
def is_rectangle_overlap(rec1, rec2):
    # rec = [x1, y1, x2, y2]
    x_overlap = max(rec1[0], rec2[0]) < min(rec1[2], rec2[2])
    y_overlap = max(rec1[1], rec2[1]) < min(rec1[3], rec2[3])
    return x_overlap and y_overlap
```

**V2: Determine if Two Events Have Conflict (LeetCode 2446)**
- **Twist:** Two events as time strings. Do they conflict?
- **Change:** Parse time strings to minutes, then check interval intersection.
- **Key insight:** Time parsing + simple interval comparison.

**V3: Interval Intersections of Multiple Lists**
- **Twist:** Intersection of k lists of intervals
- **Change:** Iteratively intersect result with next list, or use a sweep line across all lists.
- **Key insight:** Intersection is associative; pairwise reduction works.

**V4: Range Module (LeetCode 715)**
- **Twist:** Add, remove, and query ranges dynamically
- **Change:** Maintain sorted list of disjoint intervals. Merge on add, split on remove.
- **Key insight:** Dynamic interval set requires maintaining invariants via merge and split operations.

**Near Miss: Merge Intervals (LeetCode 56)**
- **Looks like:** Interval intersection
- **But:** Merge operates on ONE list, finding unions. Intersection operates on TWO lists, finding overlaps.
- **Lesson:** Union vs intersection are opposite operations. Make sure you know which one the problem asks for.

---

## Archetype 16.4: Remove / Select Intervals

### Recognition Signal (10 seconds)
Words: **"remove", "erase", "minimum remove", "select intervals", "non-overlapping", "covered", "maximum set"**

The question: **"Remove or select intervals to satisfy a constraint (non-overlapping, no covering, maximum size)."**

### Core Structure
```python
def remove_covered_intervals(intervals):
    # Sort by start ascending, end descending
    intervals.sort(key=lambda x: (x[0], -x[1]))
    
    count = 0
    max_end = 0
    
    for start, end in intervals:
        if end <= max_end:
            # This interval is covered by a previous one
            count += 1
        else:
            max_end = end
    
    return len(intervals) - count
```

### The Invariant
By sorting by start ascending and end descending, any interval that comes later with `end <= max_end` is fully covered by an earlier interval. We greedily keep the interval with the largest end seen so far for each start position.

### Canonical Problem: Remove Covered Intervals (LeetCode 1288)
**Statement:** Given an array `intervals` where `intervals[i] = [li, ri]`, remove all intervals that are covered by another interval in the list. Return the number of remaining intervals.

```python
def remove_covered_intervals(intervals):
    # Sort by start ascending; if starts equal, sort by end descending
    intervals.sort(key=lambda x: (x[0], -x[1]))
    
    remaining = 0
    max_end = 0
    
    for start, end in intervals:
        if end > max_end:
            # Not covered by any previous interval
            remaining += 1
            max_end = end
        # else: covered, skip it
    
    return remaining
```

### Variation Family

**V1: Non-overlapping Intervals (LeetCode 435)**
- **Twist:** Remove minimum intervals to make the rest non-overlapping
- **Change:** Greedy by end time. Keep track of last_end. Count removals.
- **Key insight:** Already covered in Greedy pattern (Archetype 15.1). Interval selection is fundamentally greedy.

**V2: Data Stream as Disjoint Intervals (LeetCode 352)**
- **Twist:** Values added one by one. Maintain disjoint intervals.
- **Change:** Use sorted map (TreeMap / bisect) to find neighbors and merge.
- **Key insight:** Dynamic interval maintenance with neighbor lookup and merge.

**V3: Find Right Interval (LeetCode 436)**
- **Twist:** For each interval, find the interval with minimum start that is >= current end
- **Change:** Sort starts with original indices. Binary search for each end.
- **Key insight:** Preprocessing + binary search transforms O(n^2) to O(n log n).

**V4: Maximum Profit in Job Scheduling (LeetCode 1235)**
- **Twist:** Weighted interval scheduling. Each job has profit. Maximize profit with non-overlapping jobs.
- **Change:** Sort by end time. DP: `dp[i] = max(dp[i-1], profit[i] + dp[j])` where j is last non-overlapping job.
- **Key insight:** This is the weighted version. Greedy fails when profits differ. Use DP + binary search.

**Near Miss: Minimum Number of Arrows to Burst Balloons (LeetCode 452)**
- **Looks like:** Remove intervals
- **But:** Arrows burst all overlapping balloons, not selecting a subset. The goal is minimum points, not maximum subset.
- **Lesson:** Understand the exact operation: selecting subset (keep) vs covering set (arrows) vs merging (union).

---

## Pattern 16 Mastery Checklist

Before moving to Pattern 17, confirm you can:

- [ ] Merge overlapping: sort by start, compare current with last merged
- [ ] Meeting rooms: two-pointer sweep on sorted starts and ends
- [ ] Interval intersection: two pointers, advance the one with smaller end
- [ ] Remove covered: sort by (start asc, end desc), track max_end
- [ ] Sweep line: convert intervals to events (+1 at start, -1 at end)
- [ ] Dynamic intervals: use sorted map / bisect for insert and merge
- [ ] Weighted scheduling: sort by end + DP + binary search for last non-overlap
- [ ] Distinguish: merge (one list, union) vs intersection (two lists, overlap) vs select (greedy subset)

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Forgetting to sort intervals | Wrong merge or overlap detection | Always sort by start (or end, depending on algorithm) |
| Using <= vs < for overlap | Off-by-one errors with boundary touching | Clarify if [1,2] and [2,3] overlap (they don't in "strict" but do in "closed") |
| Not handling empty input | IndexError or wrong result | Check `if not intervals: return []` at start |
| Confusing merge with intersection | Wrong output entirely | Merge = union of one list; Intersection = overlap of two lists |
| Two-pointer sweep with unsorted arrays | Missed overlaps or wrong room count | Sort both arrays before sweeping |
| Using O(n^2) for dynamic intervals | TLE on large inputs | Use balanced BST, bisect, or sorted containers for O(log n) operations |

---

## Pattern Blends (What Comes Next)

Intervals do not live in isolation. They blend with:

- **Greedy:** Interval scheduling, non-overlapping intervals, video stitching
- **Heap:** Meeting rooms II, minimum interval queries
- **DP:** Weighted interval scheduling, maximum profit job scheduling
- **Binary Search:** Find right interval, inserting into sorted intervals
- **Sweep Line:** Car pooling, skyline problem, rectangle area

---

*Next: Pattern 17 — Math & Geometry*
