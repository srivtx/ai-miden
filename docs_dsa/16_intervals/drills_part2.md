# Pattern 16: Intervals — Drills Part 2

> **Focus:** Warm-ups (5) + Core Drills (10)
>
> **Goal:** Build muscle memory for sorting by start/end, merging, two-pointer scanning, and greedy interval selection.

---

## Warm-Ups

### Problem 1. LeetCode 252. Meeting Rooms
**Archetype:** 16.2 Meeting Rooms
**Type:** Warm-Up
**Statement:** Determine if a person can attend all meetings given an array of intervals.
**Why it fits:** This is the canonical meeting-room predicate problem. Sorting by start time and checking for any overlap is the fundamental first step in the interval pattern.
**The Twist:** None — this is the pure template. The only nuance is that a meeting ending at time `t` and another starting at `t` do NOT overlap.
**Code Skeleton:**
```python
def can_attend_meetings(intervals):
    # Edge case: 0 or 1 meetings are always attendable
    if len(intervals) <= 1:
        return True

    # Sort by start time — the universal first step for interval problems
    intervals.sort(key=lambda x: x[0])

    for i in range(1, len(intervals)):
        # Overlap exists if current start is strictly less than previous end
        if intervals[i][0] < intervals[i - 1][1]:
            return False

    return True
```

---

### Problem 2. LeetCode 56. Merge Intervals
**Archetype:** 16.1 Merge Overlapping
**Type:** Warm-Up
**Statement:** Merge all overlapping intervals into a list of disjoint intervals.
**Why it fits:** This is the foundational interval-merge template. Sort by start, iterate, and either extend the last merged interval or append a new one. Nearly every harder interval problem builds on this.
**The Twist:** Pure template. The edge case to watch is `[[1,4],[4,5]]` — whether touching intervals merge depends on using `<=` vs `<`.
**Code Skeleton:**
```python
def merge(intervals):
    if not intervals:
        return []

    # Sort by start time
    intervals.sort(key=lambda x: x[0])

    result = [intervals[0]]
    for current in intervals[1:]:
        last = result[-1]
        # Overlap check: current start <= last end (inclusive merge)
        if current[0] <= last[1]:
            last[1] = max(last[1], current[1])
        else:
            result.append(current)

    return result
```

---

### Problem 3. LeetCode 986. Interval List Intersections
**Archetype:** 16.3 Interval Intersection
**Type:** Warm-Up
**Statement:** Return the intersection of two lists of closed intervals.
**Why it fits:** Introduces the two-pointer technique across two sorted interval lists. The intersection of `[a,b]` and `[c,d]` is `[max(a,c), min(b,d)]` if `max(a,c) <= min(b,d)`.
**The Twist:** Pure two-pointer template. You must advance the pointer whose interval ends first, because it cannot intersect with any later intervals from the other list.
**Code Skeleton:**
```python
def interval_intersection(first_list, second_list):
    i = j = 0
    result = []

    while i < len(first_list) and j < len(second_list):
        a_start, a_end = first_list[i]
        b_start, b_end = second_list[j]

        # Intersection exists if the ranges overlap at all
        lo = max(a_start, b_start)
        hi = min(a_end, b_end)

        if lo <= hi:
            result.append([lo, hi])

        # Advance the list with the earlier-ending interval
        if a_end < b_end:
            i += 1
        else:
            j += 1

    return result
```

---

### Problem 4. LeetCode 435. Non-overlapping Intervals
**Archetype:** 16.4 Remove/Select Intervals
**Type:** Warm-Up
**Statement:** Find the minimum number of intervals to remove so the rest are non-overlapping.
**Why it fits:** This teaches the greedy "sort by end time" strategy, which is the canonical approach for interval selection/removal. Choosing the interval that ends earliest leaves the most room for future intervals.
**The Twist:** Sorting by start time and using a standard merge approach gives the wrong answer. You must sort by end time to maximize remaining space.
**Code Skeleton:**
```python
def erase_overlap_intervals(intervals):
    if not intervals:
        return 0

    # Greedy: sort by end time to keep intervals that finish earliest
    intervals.sort(key=lambda x: x[1])

    removed = 0
    prev_end = intervals[0][1]

    for i in range(1, len(intervals)):
        # If current starts before previous ends, they overlap; remove current
        if intervals[i][0] < prev_end:
            removed += 1
        else:
            # Keep current; it becomes the new anchor
            prev_end = intervals[i][1]

    return removed
```

---

### Problem 5. LeetCode 57. Insert Interval
**Archetype:** 16.1 Merge Overlapping
**Type:** Warm-Up
**Statement:** Insert a new interval into a list of sorted, non-overlapping intervals, merging if necessary.
**Why it fits:** Tests the merge template in a constrained setting (already sorted input). It breaks the problem into three phases: intervals before, overlapping intervals, and intervals after.
**The Twist:** Input is already sorted and disjoint, so you do not need to sort again. The challenge is identifying the "overlap zone" efficiently.
**Code Skeleton:**
```python
def insert(intervals, new_interval):
    result = []
    i = 0
    n = len(intervals)

    # Phase 1: add all intervals ending before new_interval starts
    while i < n and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1

    # Phase 2: merge all overlapping intervals into new_interval
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    result.append(new_interval)

    # Phase 3: add all remaining intervals
    while i < n:
        result.append(intervals[i])
        i += 1

    return result
```

---

## Core Drills

### Problem 6. LeetCode 253. Meeting Rooms II
**Archetype:** 16.2 Meeting Rooms
**Type:** Core Drill
**Statement:** Find the minimum number of conference rooms required.
**Why it fits:** This is the quantitative version of Meeting Rooms. The two-pointer technique on sorted starts and ends is a classic interval-pattern algorithm that feels different from simple merging.
**The Twist:** You do not track *which* room a meeting uses; you only care about the count of concurrent meetings. Reusing a room is abstracted away by the `start >= ends[end_ptr]` check.
**Code Skeleton:**
```python
def min_meeting_rooms(intervals):
    if not intervals:
        return 0

    starts = sorted(i[0] for i in intervals)
    ends = sorted(i[1] for i in intervals)

    rooms = 0
    end_ptr = 0

    for start in starts:
        # If a room freed up before this meeting starts, reuse it
        if start >= ends[end_ptr]:
            end_ptr += 1
        else:
            # Need a new room
            rooms += 1

    return rooms
```

---

### Problem 7. LeetCode 452. Minimum Number of Arrows to Burst Balloons
**Archetype:** 16.2 Meeting Rooms / 16.4 Remove/Select Intervals
**Type:** Core Drill
**Statement:** Given balloon intervals on the X-axis, find the minimum arrows to burst all balloons.
**Why it fits:** This is isomorphic to the interval scheduling / greedy selection problem. Sorting by end and shooting at the end of the first balloon maximizes arrow coverage.
**The Twist:** The "arrow" is a point, not an interval. You burst a balloon if the point lies within its interval. This maps exactly to finding the maximum number of non-overlapping points, but the framing is different.
**Code Skeleton:**
```python
def find_min_arrow_shots(points):
    if not points:
        return 0

    # Sort by end coordinate (greedy: shoot at the end of the earliest-finishing balloon)
    points.sort(key=lambda x: x[1])

    arrows = 1
    arrow_pos = points[0][1]

    for i in range(1, len(points)):
        # If this balloon starts after the last arrow position, we need a new arrow
        if points[i][0] > arrow_pos:
            arrows += 1
            arrow_pos = points[i][1]

    return arrows
```

---

### Problem 8. LeetCode 646. Maximum Length of Pair Chain
**Archetype:** 16.4 Remove/Select Intervals
**Type:** Core Drill
**Statement:** Given pairs `[left, right]`, form the longest chain such that each consecutive pair satisfies `a[1] < b[0]`.
**Why it fits:** A direct application of greedy interval chain selection. Sorting by end time and greedily picking compatible intervals yields the longest chain.
**The Twist:** The constraint is strict inequality (`<` not `<=`), which changes the overlap check from standard merge problems. This small sign flip is a common trap.
**Code Skeleton:**
```python
def find_longest_chain(pairs):
    # Sort by the right element to greedily pick the earliest-ending pair
    pairs.sort(key=lambda x: x[1])

    chain_length = 0
    current_end = float('-inf')

    for left, right in pairs:
        # Strict: next pair must start strictly after current ends
        if left > current_end:
            chain_length += 1
            current_end = right

    return chain_length
```

---

### Problem 9. LeetCode 759. Employee Free Time
**Archetype:** 16.3 Interval Intersection
**Type:** Core Drill
**Statement:** Given schedules of multiple employees, return their common free time.
**Why it fits:** First merges all employee intervals (Archetype 16.1), then scans the merged timeline to find gaps between consecutive intervals. It combines merge and gap detection.
**The Twist:** The input is a list of lists, so you must flatten and merge before finding free time. The free time is the inverse of the merged occupied intervals.
**Code Skeleton:**
```python
def employee_free_time(schedule):
    # Flatten all intervals across all employees
    intervals = []
    for employee in schedule:
        intervals.extend(employee)

    # Merge overlapping intervals
    intervals.sort(key=lambda x: x[0])
    merged = []
    for interval in intervals:
        if not merged or interval[0] > merged[-1][1]:
            merged.append(interval)
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])

    # Free time is the gap between consecutive merged intervals
    free_time = []
    for i in range(1, len(merged)):
        free_time.append([merged[i - 1][1], merged[i][0]])

    return free_time
```

---

### Problem 10. LeetCode 352. Data Stream as Disjoint Intervals
**Archetype:** 16.1 Merge Overlapping
**Type:** Core Drill
**Statement:** Implement a data structure that adds values and returns the current disjoint intervals at any time.
**Why it fits:** This is merge-intervals turned into a class-based stream problem. You must maintain a sorted list of disjoint intervals and efficiently merge adjacent values on each insert.
**The Twist:** Values are individual points, not intervals, but consecutive points merge into intervals. You need `bisect` to find the insertion position quickly and then check neighbors for merge eligibility.
**Code Skeleton:**
```python
import bisect

class SummaryRanges:
    def __init__(self):
        # Store intervals as [start, end] in a sorted list
        self.intervals = []

    def addNum(self, value: int) -> None:
        # Find position where value would be inserted
        i = bisect.bisect_left(self.intervals, [value])

        # Check if value is already inside an existing interval
        if i > 0 and self.intervals[i - 1][0] <= value <= self.intervals[i - 1][1]:
            return

        # Determine if we merge with left and/or right neighbors
        merge_left = i > 0 and self.intervals[i - 1][1] + 1 == value
        merge_right = i < len(self.intervals) and self.intervals[i][0] - 1 == value

        if merge_left and merge_right:
            # Bridge the gap: merge left and right into one interval
            self.intervals[i - 1][1] = self.intervals[i][1]
            self.intervals.pop(i)
        elif merge_left:
            self.intervals[i - 1][1] = max(self.intervals[i - 1][1], value)
        elif merge_right:
            self.intervals[i][0] = value
        else:
            self.intervals.insert(i, [value, value])

    def getIntervals(self):
        return self.intervals
```

---

### Problem 11. LeetCode 1094. Car Pooling
**Archetype:** 16.2 Meeting Rooms
**Type:** Core Drill
**Statement:** Determine if a car with given capacity can complete all trips, where each trip is `[num_passengers, start, end]`.
**Why it fits:** This is a sweep-line / difference-array variant of meeting rooms. Instead of counting concurrent meetings, you count concurrent passengers. Sorting events by location and sweeping accumulates load.
**The Twist:** The events are `[location, delta]` where `delta` is positive at pickup and negative at dropoff. The car does not need a new "room" at every overlap; it needs the sum of deltas to never exceed capacity.
**Code Skeleton:**
```python
def car_pooling(trips, capacity: int) -> bool:
    events = []
    for num, start, end in trips:
        events.append((start, num))   # Pickup: add passengers
        events.append((end, -num))    # Dropoff: remove passengers

    # Sort by location; if same location, process dropoffs before pickups
    events.sort(key=lambda x: (x[0], x[1]))

    current_load = 0
    for location, delta in events:
        current_load += delta
        if current_load > capacity:
            return False

    return True
```

---

### Problem 12. LeetCode 1851. Minimum Interval to Include Each Query
**Archetype:** 16.5 Advanced Interval Problems
**Type:** Core Drill
**Statement:** Given intervals and queries, for each query find the length of the smallest interval that contains it.
**Why it fits:** A classic "offline query" problem that combines sorting, a min-heap, and interval containment. You sort both intervals and queries, then sweep through time while maintaining candidate intervals in a heap.
**The Twist:** The interval must *contain* the query point (`left <= query <= right`). You must add all intervals starting before the query to the heap, then purge intervals ending before the query. The heap stores `(size, right_endpoint)`.
**Code Skeleton:**
```python
import heapq

def min_interval(intervals, queries):
    # Sort intervals by start time
    intervals.sort()
    # Sort queries by value, but keep original indices
    sorted_queries = sorted((q, i) for i, q in enumerate(queries))

    result = [-1] * len(queries)
    min_heap = []
    interval_idx = 0

    for query, original_idx in sorted_queries:
        # Add all intervals that start before or at this query
        while interval_idx < len(intervals) and intervals[interval_idx][0] <= query:
            left, right = intervals[interval_idx]
            size = right - left + 1
            heapq.heappush(min_heap, (size, right))
            interval_idx += 1

        # Remove intervals that ended before this query (cannot contain it)
        while min_heap and min_heap[0][1] < query:
            heapq.heappop(min_heap)

        # The smallest valid interval is at the top of the heap
        if min_heap:
            result[original_idx] = min_heap[0][0]

    return result
```

---

### Problem 13. LeetCode 1272. Remove Interval
**Archetype:** 16.1 Merge Overlapping / 16.4 Remove/Select Intervals
**Type:** Core Drill
**Statement:** Remove all parts of intervals that overlap with a given `toBeRemoved` interval.
**Why it fits:** This is the inverse of merge: given disjoint intervals, carve out a chunk from the middle. It tests precise boundary handling and understanding of overlap cases.
**The Twist:** There are three cases per interval: completely outside (keep as-is), completely inside (discard), or partially overlapping (split into two). You must handle the split case correctly.
**Code Skeleton:**
```python
def remove_interval(intervals, to_be_removed):
    result = []
    remove_start, remove_end = to_be_removed

    for start, end in intervals:
        # Case 1: interval is completely before or after removal zone
        if end <= remove_start or start >= remove_end:
            result.append([start, end])
        else:
            # Case 2: left part survives
            if start < remove_start:
                result.append([start, remove_start])
            # Case 3: right part survives
            if end > remove_end:
                result.append([remove_end, end])

    return result
```

---

### Problem 14. LeetCode 218. The Skyline Problem
**Archetype:** 16.5 Advanced Interval Problems
**Type:** Core Drill
**Statement:** Given buildings as `[left, right, height]`, output the skyline as a list of key points `[x, height]`.
**Why it fits:** This is the sweep-line grandmaster of interval problems. You treat building edges as events and maintain a max-heap of active heights. The skyline changes whenever the max height changes.
**The Twist:** You need a max-heap of heights, but Python only has a min-heap. You store negative heights. Additionally, you must lazily remove buildings that have ended by tracking their end coordinates.
**Code Skeleton:**
```python
import heapq

def get_skyline(buildings):
    # Create events: (x, height)
    # Use negative height for start to distinguish from end events
    events = []
    for left, right, height in buildings:
        events.append((left, -height, right))   # Start event
        events.append((right, 0, 0))             # End event

    # Sort by x; if same x, taller start comes first
    events.sort(key=lambda x: (x[0], x[1]))

    result = []
    # Max-heap of (-height, right_end)
    max_heap = [(0, float('inf'))]
    prev_max_height = 0

    for x, neg_height, right in events:
        if neg_height != 0:
            # Start of a building
            heapq.heappush(max_heap, (neg_height, right))
        else:
            # End of a building: we lazily clean up below
            pass

        # Remove buildings that have already ended
        while max_heap[0][1] <= x:
            heapq.heappop(max_heap)

        curr_max_height = -max_heap[0][0]
        if curr_max_height != prev_max_height:
            result.append([x, curr_max_height])
            prev_max_height = curr_max_height

    return result
```

---

### Problem 15. LeetCode 2406. Divide Intervals Into Minimum Number of Groups
**Archetype:** 16.2 Meeting Rooms
**Type:** Core Drill
**Statement:** Divide intervals into the minimum number of groups such that no two intervals in the same group overlap.
**Why it fits:** This is exactly isomorphic to Meeting Rooms II but with different framing. Each "group" is a room, and non-overlap within a group means no two meetings in the same room conflict.
**The Twist:** The problem is identical to 253 but uses the word "groups" instead of "rooms." Recognizing this isomorphism saves you from reinventing the algorithm. The greedy sort-by-end approach also works.
**Code Skeleton:**
```python
import heapq

def min_groups(intervals):
    if not intervals:
        return 0

    # Sort by start time
    intervals.sort()

    # Min-heap tracking the end time of the last interval in each group
    min_heap = []

    for start, end in intervals:
        # If the earliest-ending group finishes before this starts, reuse it
        if min_heap and min_heap[0] < start:
            heapq.heappop(min_heap)
        heapq.heappush(min_heap, end)

    # The heap size is the number of groups needed
    return len(min_heap)
```
