# Pattern 16: Intervals

> **Pattern Recognition:** When you see "overlapping", "merge", "insert", "meeting rooms", "schedule", "intervals" — think interval problems.
>
> **Fundamental Insight:** Interval problems usually involve sorting by start time (or end time), then scanning while maintaining some state about the current interval(s).

---

## Archetype 16.1: Merge Overlapping

### Recognition Signal
Words: **"merge intervals", "overlapping", "combine"**

### Template
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

### Problems
- Merge Intervals (LeetCode 56)
- Insert Interval (LeetCode 57)

---

## Archetype 16.2: Meeting Rooms

### Recognition Signal
Words: **"meeting rooms", "minimum rooms", "conference rooms"**

### Problems
- Meeting Rooms (LeetCode 252) — can attend all?
- Meeting Rooms II (LeetCode 253) — min rooms needed
- Minimum Number of Arrows to Burst Balloons (LeetCode 452)

**Meeting Rooms II:**
```python
def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    starts = sorted(i[0] for i in intervals)
    ends = sorted(i[1] for i in intervals)
    rooms = 0
    end_ptr = 0
    for start in starts:
        if start >= ends[end_ptr]:
            end_ptr += 1
        else:
            rooms += 1
    return rooms
```

---

## Archetype 16.3: Interval Intersection

### Recognition Signal
Words: **"intersection", "common", "overlap between two lists"**

### Problems
- Interval List Intersections (LeetCode 986)
- Employee Free Time (LeetCode 759)

---

## Archetype 16.4: Remove / Select Intervals

### Recognition Signal
Words: **"remove", "erase", "select", "maximum non-overlapping"**

### Problems
- Non-overlapping Intervals (LeetCode 435)
- Maximum Length of Pair Chain (LeetCode 646)

---

## Mastery Checklist
- [ ] Merge overlapping: sort by start, iterate
- [ ] Meeting rooms: two pointers on starts and ends
- [ ] Interval intersection: two pointers
- [ ] Remove overlaps: sort by end, greedy

---

## Common Traps

**Trap:** Not sorting first.
- Fix: Almost all interval problems require sorting.

**Trap:** Using <= vs < for overlap check.
- Overlap: `[1, 3]` and `[3, 5]` — do they overlap? Depends on problem. Usually `[a, b]` and `[b, c]` do NOT overlap for "merge" but DO for "meeting rooms" if one ends when other starts.

**Trap:** Forgetting to merge end times.
- Fix: `last[1] = max(last[1], current[1])`

**Near Miss: Calendar Scheduling**
- Multiple people's calendars
- Find common free time
- Pattern blend: Intervals + merge + difference
