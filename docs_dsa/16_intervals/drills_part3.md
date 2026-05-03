# Pattern 16: Intervals — Drills Part 3

> **Focus:** Near Misses (5) + Pattern Blends (5) + Interview Simulation (5)
>
> **Goal:** Train pattern recognition under disguise, cross-pattern synthesis, and full interview-ready problem solving.

---

## Near Misses

### Problem 1. LeetCode 731. My Calendar II
**Archetype:** 16.5 Advanced Interval Problems
**Type:** Near Miss
**Statement:** Implement a calendar that books intervals and detects double-bookings (no triple bookings allowed).
**Why it fits:** This looks like a standard interval booking problem, but the twist is that *one* overlap is allowed (double-booking), while a second overlap (triple-booking) must be rejected. It tests precise overlap counting rather than simple merge logic.
**The Twist:** You must maintain two lists: successfully booked intervals and "overlaps" (regions already double-booked). A new booking is valid only if it does not intersect any overlap interval.
**Code Skeleton:**
```python
class MyCalendarTwo:
    def __init__(self):
        self.bookings = []      # All successfully booked intervals
        self.overlaps = []      # Regions that are double-booked

    def book(self, start: int, end: int) -> bool:
        # Check if this new booking would create a triple booking
        for o_start, o_end in self.overlaps:
            if max(start, o_start) < min(end, o_end):
                # Overlaps with a double-booked region -> triple booking
                return False

        # Record all new double-booked regions created by this booking
        for b_start, b_end in self.bookings:
            if max(start, b_start) < min(end, b_end):
                self.overlaps.append((max(start, b_start), min(end, b_end)))

        self.bookings.append((start, end))
        return True
```

---

### Problem 2. LeetCode 732. My Calendar III
**Archetype:** 16.5 Advanced Interval Problems
**Type:** Near Miss
**Statement:** Implement a calendar that returns the maximum number of concurrent bookings (k-booking) after each `book` call.
**Why it fits:** This is a streaming version of Meeting Rooms II. Instead of computing once over a static array, you process events online and track the maximum concurrency seen so far.
**The Twist:** The input is online (streaming), so you cannot sort all events upfront. A sweep-line with a sorted dictionary (or two heaps) is required to maintain active intervals dynamically.
**Code Skeleton:**
```python
class MyCalendarThree:
    def __init__(self):
        # Difference array using a sorted map: point -> delta
        self.timeline = {}

    def book(self, start: int, end: int) -> int:
        self.timeline[start] = self.timeline.get(start, 0) + 1
        self.timeline[end] = self.timeline.get(end, 0) - 1

        max_k = 0
        active = 0
        for x in sorted(self.timeline.keys()):
            active += self.timeline[x]
            max_k = max(max_k, active)

        return max_k
```

---

### Problem 3. LeetCode 1229. Meeting Scheduler
**Archetype:** 16.3 Interval Intersection
**Type:** Near Miss
**Statement:** Given availability slots of two people and a meeting duration, find the earliest time slot that works for both.
**Why it fits:** This is interval intersection with an extra constraint: the intersection must be at least `duration` long. It uses the same two-pointer approach but adds a length check before returning.
**The Twist:** You do not return the entire intersection; you return a sub-interval of exact length `duration` starting at the intersection's beginning. If the intersection is too short, you skip it entirely.
**Code Skeleton:**
```python
def min_available_duration(slots1, slots2, duration: int):
    slots1.sort()
    slots2.sort()
    i = j = 0

    while i < len(slots1) and j < len(slots2):
        start = max(slots1[i][0], slots2[j][0])
        end = min(slots1[i][1], slots2[j][1])

        if end - start >= duration:
            # Earliest valid slot found
            return [start, start + duration]

        # Advance the pointer with the earlier-ending slot
        if slots1[i][1] < slots2[j][1]:
            i += 1
        else:
            j += 1

    return []
```

---

### Problem 4. LeetCode 163. Missing Ranges
**Archetype:** 16.1 Merge Overlapping
**Type:** Near Miss
**Statement:** Given a sorted unique array of integers and a range `[lower, upper]`, return the missing ranges.
**Why it fits:** The problem is about identifying gaps in a sorted sequence, which is the inverse of merging. You scan the array and report the intervals *not* covered by the array elements within the global bounds.
**The Twist:** There are no explicit intervals in the input; you generate them from consecutive elements. Edge cases include missing ranges at the boundaries (`lower` to first element, last element to `upper`).
**Code Skeleton:**
```python
def find_missing_ranges(nums, lower: int, upper: int):
    def format_range(start, end):
        if start == end:
            return str(start)
        return f"{start}->{end}"

    result = []
    prev = lower - 1

    for i in range(len(nums) + 1):
        # Use upper+1 as the virtual last element
        curr = nums[i] if i < len(nums) else upper + 1

        if curr - prev >= 2:
            # There is a gap between prev+1 and curr-1
            result.append(format_range(prev + 1, curr - 1))

        prev = curr

    return result
```

---

### Problem 5. LeetCode 715. Range Module
**Archetype:** 16.5 Advanced Interval Problems
**Type:** Near Miss
**Statement:** Design a data structure to add, remove, and query ranges efficiently.
**Why it fits:** This is interval manipulation as a full API. Adding ranges requires merging; removing ranges requires splitting; querying requires checking containment. It tests deep understanding of interval boundaries.
**The Twist:** Unlike simple merge, you must persist disjoint intervals and support destructive operations (remove). Every operation can split or merge existing intervals, so boundary arithmetic must be exact.
**Code Skeleton:**
```python
class RangeModule:
    def __init__(self):
        # Maintain a sorted list of disjoint [start, end) intervals
        self.ranges = []

    def addRange(self, left: int, right: int) -> None:
        new_ranges = []
        i = 0

        # Add intervals strictly before the new range
        while i < len(self.ranges) and self.ranges[i][1] < left:
            new_ranges.append(self.ranges[i])
            i += 1

        # Merge all overlapping intervals with [left, right)
        while i < len(self.ranges) and self.ranges[i][0] <= right:
            left = min(left, self.ranges[i][0])
            right = max(right, self.ranges[i][1])
            i += 1
        new_ranges.append([left, right])

        # Add intervals strictly after
        while i < len(self.ranges):
            new_ranges.append(self.ranges[i])
            i += 1

        self.ranges = new_ranges

    def queryRange(self, left: int, right: int) -> bool:
        # Binary search for candidate interval
        lo, hi = 0, len(self.ranges)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.ranges[mid][1] <= left:
                lo = mid + 1
            else:
                hi = mid

        # Check if the found interval fully contains [left, right)
        if lo < len(self.ranges):
            start, end = self.ranges[lo]
            return start <= left and right <= end
        return False

    def removeRange(self, left: int, right: int) -> None:
        new_ranges = []
        for start, end in self.ranges:
            if end <= left or start >= right:
                # No overlap
                new_ranges.append([start, end])
            else:
                # Left part survives
                if start < left:
                    new_ranges.append([start, left])
                # Right part survives
                if end > right:
                    new_ranges.append([right, end])
        self.ranges = new_ranges
```

---

## Pattern Blends

### Problem 6. LeetCode 1235. Maximum Profit in Job Scheduling
**Archetype:** 16.5 Advanced Interval Problems / 13.1 1D DP
**Type:** Pattern Blend
**Statement:** Given jobs `[start, end, profit]`, find the maximum profit subset of non-overlapping jobs.
**Why it fits:** After sorting by end time, each job either stands alone or chains onto the latest compatible job. This reduces to weighted interval scheduling, a classic DP-on-intervals blend.
**The Twist:** Greedy by end time is insufficient because profits differ. You need DP plus binary search to find the last non-conflicting job in O(log n) per state, yielding O(n log n) total.
**Code Skeleton:**
```python
import bisect

def job_scheduling(start_time, end_time, profit):
    jobs = sorted(zip(end_time, start_time, profit))
    n = len(jobs)

    # dp[i] = max profit using first i jobs (0-indexed, dp[0] is profit of first job)
    dp_end = [0]    # End times corresponding to dp states
    dp_profit = [0] # Max profit up to each end time

    for end, start, p in jobs:
        # Find rightmost job that ends <= start
        i = bisect.bisect_right(dp_end, start) - 1
        curr_profit = dp_profit[i] + p

        if curr_profit > dp_profit[-1]:
            dp_end.append(end)
            dp_profit.append(curr_profit)

    return dp_profit[-1]
```

---

### Problem 7. LeetCode 1751. Maximum Number of Events That Can Be Attended II
**Archetype:** 16.5 Advanced Interval Problems / 14.1 2D DP
**Type:** Pattern Blend
**Statement:** Given events `[start, end, value]`, attend at most `k` non-overlapping events to maximize value.
**Why it fits:** This is the multi-attendance version of job scheduling. The DP state becomes `dp[i][k]` = max value using first `i` events with at most `k` attendances, blending interval sorting with 2D DP.
**The Twist:** The binary search now looks for the next compatible event, and the DP recurrence chooses to either skip the current event or attend it (consuming one of the `k` slots and jumping to the next compatible event).
**Code Skeleton:**
```python
import bisect
from functools import lru_cache

def max_value(events, k: int):
    events.sort()  # Sort by start time
    n = len(events)
    starts = [e[0] for e in events]

    @lru_cache(maxsize=None)
    def dfs(idx, attendances_left):
        if idx >= n or attendances_left == 0:
            return 0

        # Option 1: skip current event
        skip = dfs(idx + 1, attendances_left)

        # Option 2: attend current event
        end, value = events[idx][1], events[idx][2]
        # Find next event that starts after 'end'
        next_idx = bisect.bisect_right(starts, end)
        attend = value + dfs(next_idx, attendances_left - 1)

        return max(skip, attend)

    return dfs(0, k)
```

---

### Problem 8. LeetCode 2402. Meeting Rooms III
**Archetype:** 16.2 Meeting Rooms / 08.1 Heap
**Type:** Pattern Blend
**Statement:** Given `n` rooms and meetings `[start, end]`, find the room that hosts the most meetings.
**Why it fits:** This blends interval scheduling with a min-heap to track when each room becomes free. It is a simulation problem where the interval pattern (meeting times) drives heap operations.
**The Twist:** If multiple rooms are free, always assign the lowest-numbered room. If no room is free, delay the meeting until the earliest room frees up. This delay mechanic changes the actual end times of meetings.
**Code Skeleton:**
```python
import heapq

def most_booked(n: int, meetings):
    # Min-heap of (available_time, room_index)
    rooms = [(0, i) for i in range(n)]
    heapq.heapify(rooms)
    count = [0] * n

    for start, end in sorted(meetings):
        # Free up all rooms that are available by 'start'
        # But we only need the earliest available room
        # If the earliest room is not ready, delay the meeting
        avail_time, room_idx = heapq.heappop(rooms)

        duration = end - start
        if avail_time <= start:
            # Meeting starts on time
            new_end = end
        else:
            # Meeting is delayed
            new_end = avail_time + duration

        count[room_idx] += 1
        heapq.heappush(rooms, (new_end, room_idx))

    # Return room with max count (smallest index on tie)
    return count.index(max(count))
```

---

### Problem 9. LeetCode 2054. Two Best Non-Overlapping Events
**Archetype:** 16.5 Advanced Interval Problems / 02.1 Two Pointers
**Type:** Pattern Blend
**Statement:** Given events `[start, end, value]`, pick at most two non-overlapping events to maximize total value.
**Why it fits:** After sorting by start time, for each event you want the best preceding non-overlapping event. This combines interval sorting with a prefix-maximum scan using two pointers or binary search.
**The Twist:** The "two events" constraint means you can either pick one event or two. You precompute the best value of any event ending before each event starts, which turns the problem into a linear scan with binary search.
**Code Skeleton:**
```python
import bisect

def max_two_events(events):
    # Sort by end time
    events.sort(key=lambda x: x[1])
    n = len(events)

    ends = [e[1] for e in events]
    # prefix_max[i] = max value of any single event among first i events
    prefix_max = [0] * n
    prefix_max[0] = events[0][2]
    for i in range(1, n):
        prefix_max[i] = max(prefix_max[i - 1], events[i][2])

    max_total = 0
    for i in range(n):
        start, end, value = events[i]
        # Best event that ends strictly before this event starts
        j = bisect.bisect_left(ends, start) - 1
        if j >= 0:
            max_total = max(max_total, value + prefix_max[j])
        else:
            max_total = max(max_total, value)

    return max_total
```

---

### Problem 10. LeetCode 2008. Maximum Earnings From Taxi
**Archetype:** 16.5 Advanced Interval Problems / 13.1 1D DP
**Type:** Pattern Blend
**Statement:** Given `n` points and rides `[start, end, tip]`, where earnings = `end - start + tip`, find max earnings visiting non-overlapping rides.
**Why it fits:** This is structurally identical to weighted interval scheduling (job scheduling) but framed as a taxi route. The DP plus binary search template applies directly once you see the interval structure.
**The Twist:** The tip makes earnings non-obvious. Also, you can choose not to take any ride at a point and just drive forward. The DP state represents max earnings up to each point, not just up to each ride.
**Code Skeleton:**
```python
import bisect

def max_taxi_earnings(n: int, rides):
    # Sort rides by end point
    rides.sort(key=lambda x: x[1])
    m = len(rides)

    ends = [r[1] for r in rides]
    # dp[i] = max earnings using first i rides
    dp = [0] * (m + 1)

    for i in range(1, m + 1):
        start, end, tip = rides[i - 1]
        profit = end - start + tip

        # Find last ride that ends <= start
        j = bisect.bisect_right(ends, start)
        dp[i] = max(dp[i - 1], dp[j] + profit)

    return dp[m]
```

---

## Interview Simulation

### Problem 11. LeetCode 729. My Calendar I
**Archetype:** 16.5 Advanced Interval Problems
**Type:** Interview Sim
**Statement:** Implement a calendar that books intervals if they do not overlap with existing bookings.
**Why it fits:** This is a classic design interview problem. It tests whether you can maintain a sorted list of disjoint intervals and efficiently check for overlaps on each insert.
**The Twist:** The input is online, so you must use `bisect` or a balanced BST to find the insertion position and neighbor-check in O(log n) time. Brute-force O(n) scan is acceptable but suboptimal.
**Code Skeleton:**
```python
import bisect

class MyCalendar:
    def __init__(self):
        # Store bookings as [start, end] sorted by start
        self.bookings = []

    def book(self, start: int, end: int) -> bool:
        # Find insertion point
        i = bisect.bisect_left(self.bookings, [start, end])

        # Check overlap with next interval
        if i < len(self.bookings) and self.bookings[i][0] < end:
            return False

        # Check overlap with previous interval
        if i > 0 and self.bookings[i - 1][1] > start:
            return False

        self.bookings.insert(i, [start, end])
        return True
```

---

### Problem 12. LeetCode 391. Perfect Rectangle
**Archetype:** 16.5 Advanced Interval Problems / 17.4 Coordinate Geometry
**Type:** Interview Sim
**Statement:** Given multiple rectangles, determine if they exactly cover a rectangular region with no overlap and no gap.
**Why it fits:** This is a 2D interval problem. The area of the bounding box must equal the sum of individual areas, and the internal corners must cancel out (appear an even number of times) while the four outer corners appear exactly once.
**The Twist:** Checking only area equality is insufficient (overlaps can preserve total area). You must also verify corner uniqueness using a hash set: internal corners are added/removed twice; only the four extreme corners should remain.
**Code Skeleton:**
```python
def is_rectangle_cover(rectangles) -> bool:
    area = 0
    corner_set = set()

    for x1, y1, x2, y2 in rectangles:
        # Calculate total area
        area += (x2 - x1) * (y2 - y1)

        # Toggle corners in the set
        corners = [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]
        for c in corners:
            if c in corner_set:
                corner_set.remove(c)
            else:
                corner_set.add(c)

    if len(corner_set) != 4:
        return False

    # Extract bounding box corners
    x_coords = [c[0] for c in corner_set]
    y_coords = [c[1] for c in corner_set]
    x1, x2 = min(x_coords), max(x_coords)
    y1, y2 = min(y_coords), max(y_coords)

    # Check if total area matches bounding box area
    return area == (x2 - x1) * (y2 - y1)
```

---

### Problem 13. LeetCode 850. Rectangle Area II
**Archetype:** 16.5 Advanced Interval Problems / 17.4 Coordinate Geometry
**Type:** Interview Sim
**Statement:** Find the total area covered by a list of rectangles in the plane, counting overlaps only once.
**Why it fits:** This is the sweep-line algorithm applied to 2D intervals. You sweep a vertical line across the x-axis and maintain the total covered length on the y-axis using interval merging.
**The Twist:** Coordinate compression is essential because coordinates can be as large as 10^9. You collect all unique y-coordinates, sort them, and maintain an active set of y-intervals as you sweep across x-events.
**Code Skeleton:**
```python
def rectangle_area(rectangles) -> int:
    MOD = 10**9 + 7
    events = []
    y_coords = set()

    for x1, y1, x2, y2 in rectangles:
        events.append((x1, 1, y1, y2))   # Enter event
        events.append((x2, -1, y1, y2))  # Exit event
        y_coords.update([y1, y2])

    events.sort()
    y_sorted = sorted(y_coords)
    y_index = {v: i for i, v in enumerate(y_sorted)}

    # Segment tree or difference array for active y-intervals
    count = [0] * (len(y_sorted) - 1)
    active_length = 0
    prev_x = 0
    area = 0

    for x, typ, y1, y2 in events:
        dx = x - prev_x
        area += dx * active_length

        # Update active y-intervals
        l = y_index[y1]
        r = y_index[y2]
        for i in range(l, r):
            count[i] += typ
            # Recalculate active_length would require a segment tree for efficiency
            # Below is a simplified linear scan; use a segment tree for production
            if typ == 1 and count[i] == 1:
                active_length += y_sorted[i + 1] - y_sorted[i]
            elif typ == -1 and count[i] == 0:
                active_length -= y_sorted[i + 1] - y_sorted[i]

        prev_x = x

    return area % MOD
```

---

### Problem 14. LeetCode 699. Falling Squares
**Archetype:** 16.5 Advanced Interval Problems
**Type:** Interview Sim
**Statement:** Given axis-aligned squares falling bottom-down, return the maximum height of the current stack after each drop.
**Why it fits:** Each square lands on top of the highest stack in its x-interval. This is an interval query-and-update problem: for each new square, find the max height in its x-range, then set the new height for that range.
**The Twist:** Brute-force O(n^2) works for moderate input, but the expected solution uses a segment tree with lazy propagation or coordinate compression to handle range max queries and range updates efficiently.
**Code Skeleton:**
```python
def falling_squares(positions):
    # Brute-force O(n^2) approach for clarity
    n = len(positions)
    heights = [0] * n  # heights[i] = final height of the i-th square
    result = []
    max_height = 0

    for i, (left, size) in enumerate(positions):
        right = left + size
        base_height = 0

        # Find the max height of all squares this new square overlaps
        for j in range(i):
            j_left, j_size = positions[j]
            j_right = j_left + j_size
            if not (right <= j_left or left >= j_right):
                # Overlaps with square j
                base_height = max(base_height, heights[j])

        heights[i] = base_height + size
        max_height = max(max_height, heights[i])
        result.append(max_height)

    return result
```

---

### Problem 15. LeetCode 2251. Number of Flowers in Full Bloom
**Archetype:** 16.3 Interval Intersection
**Type:** Interview Sim
**Statement:** Given flower bloom times `[start, end]` and people arriving at specific times, return how many flowers are in full bloom when each person arrives.
**Why it fits:** For each person, you need to count how many intervals contain their arrival time. This is a batch-query version of interval containment, solvable with binary search on sorted start and end times.
**The Twist:** Instead of iterating all intervals per query, you sort all starts and ends separately. For a query time `t`, the answer is: count of starts <= t minus count of ends < t. This reduces to two binary searches per query.
**Code Skeleton:**
```python
import bisect

def full_bloom_flowers(flowers, people):
    starts = sorted(s for s, e in flowers)
    ends = sorted(e for s, e in flowers)

    result = []
    for t in people:
        # Flowers that have started blooming by time t
        started = bisect.bisect_right(starts, t)
        # Flowers that have already died before time t
        died = bisect.bisect_left(ends, t)

        # Flowers in full bloom = started - died
        result.append(started - died)

    return result
```
