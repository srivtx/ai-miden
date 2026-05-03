# Pattern 16: Intervals — Practice Problems

## Merge

### 56. Merge Intervals
**Statement:** Merge all overlapping intervals.
**Code:**
```python
def merge(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    result = [intervals[0]]
    for current in intervals[1:]:
        last = result[-1]
        if current[0] <= last[1]:
            last[1] = max(last[1], current[1])
        else:
            result.append(current)
    return result
```

### 57. Insert Interval
**Statement:** Insert new interval into sorted non-overlapping intervals.
**Intuition:** Add to list, then merge. Or find position, merge affected intervals.

---

## Meeting Rooms

### 252. Meeting Rooms
**Statement:** Can attend all meetings?
**Intuition:** Sort by start. Check if any start < previous end.

### 253. Meeting Rooms II
**Statement:** Min conference rooms needed.
**Code:**
```python
def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    starts = sorted(i[0] for i in intervals)
    ends = sorted(i[1] for i in intervals)
    rooms = end_ptr = 0
    for start in starts:
        if start >= ends[end_ptr]:
            end_ptr += 1
        else:
            rooms += 1
    return rooms
```

---

## Intersection

### 986. Interval List Intersections
**Statement:** Intersection of two lists of intervals.
**Intuition:** Two pointers. If intervals overlap, add intersection. Move pointer with smaller end.
**Code:**
```python
def interval_intersection(first, second):
    i = j = 0
    result = []
    while i < len(first) and j < len(second):
        start = max(first[i][0], second[j][0])
        end = min(first[i][1], second[j][1])
        if start <= end:
            result.append([start, end])
        if first[i][1] < second[j][1]:
            i += 1
        else:
            j += 1
    return result
```

### 759. Employee Free Time
**Statement:** Find common free time.
**Intuition:** Merge all intervals. Gaps between merged intervals are free time.

---

## Remove / Select

### 435. Non-overlapping Intervals
**Statement:** Min to remove for no overlaps.
**Intuition:** Sort by end. Greedy. (Also in Greedy pattern)

### 646. Maximum Length of Pair Chain
**Statement:** Max chain where end < next start.
**Intuition:** Sort by end. Greedy chain.

---

## Mixed Drill Set

1. 56 — Merge intervals
2. 253 — Meeting rooms II
3. 986 — Interval intersection
4. 57 — Insert interval
5. 435 — Non-overlapping
6. 252 — Meeting rooms
7. 759 — Employee free time
8. 646 — Max pair chain
