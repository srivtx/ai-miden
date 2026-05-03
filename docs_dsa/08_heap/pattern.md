# Pattern 08: Heap / Priority Queue

> **Pattern Recognition:** When you see "K largest/smallest", "merge K sorted", "median", "scheduling", "top K" — think heap.
>
> **Fundamental Insight:** A heap gives you O(1) access to the min/max element and O(log n) insertion/deletion. It is a partial order, not a total order. Perfect for "I only care about the extreme" problems.

---

## Archetype 8.1: Top K Elements

### Recognition Signal
Words: **"K largest", "K smallest", "Kth largest", "Kth smallest", "top K"**

### Template: Kth Largest
```python
import heapq

def find_kth_largest(nums, k):
    # Min heap of size k
    heap = nums[:k]
    heapq.heapify(heap)
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)
    return heap[0]
```

### Problems
- Kth Largest Element in an Array (LeetCode 215)
- Kth Smallest Element in a Sorted Matrix (LeetCode 378)
- Find K Pairs with Smallest Sums (LeetCode 373)
- Top K Frequent Elements (LeetCode 347) — bucket sort alternative
- K Closest Points to Origin (LeetCode 973)

---

## Archetype 8.2: Merge K Sorted

### Recognition Signal
Words: **"merge K sorted", "K lists", "combine sorted"**

### Template
```python
import heapq

def merge_k_lists(lists):
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))
    
    result = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        if elem_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))
    return result
```

### Problems
- Merge k Sorted Lists (LeetCode 23)
- Merge k Sorted Arrays
- Smallest Range Covering Elements from K Lists (LeetCode 632)
- Find K Pairs with Smallest Sums (LeetCode 373)

---

## Archetype 8.3: Scheduling / Interval Problems

### Recognition Signal
Words: **"meeting rooms", "schedule", "minimum rooms", "task scheduler", "reorganize"**

### Problems
- Meeting Rooms II (LeetCode 253)
- Task Scheduler (LeetCode 621)
- Reorganize String (LeetCode 767)
- Car Pooling (LeetCode 1094)
- Employee Free Time (LeetCode 759)

**Meeting Rooms II:**
- Sort by start time. Min heap of end times. If next meeting starts after earliest end, reuse room.

```python
def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])
    heap = []
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)
        else:
            heapq.heappush(heap, end)
    return len(heap)
```

---

## Archetype 8.4: Median Finder

### Recognition Signal
Words: **"median", "running median", "sliding window median", "find median from data stream"**

### Template: Two Heaps
```python
class MedianFinder:
    def __init__(self):
        self.small = []  # max heap (negated)
        self.large = []  # min heap
    
    def add_num(self, num):
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.small) < len(self.large):
            heapq.heappush(self.small, -heapq.heappop(self.large))
    
    def find_median(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
```

### Problems
- Find Median from Data Stream (LeetCode 295)
- Sliding Window Median (LeetCode 480)
- IPO (LeetCode 502) — max profit with k projects

---

## Archetype 8.5: Frequency-Based

### Recognition Signal
Words: **"frequent", "reorganize", "rearrange", "string", "tasks"**

### Problems
- Top K Frequent Elements (LeetCode 347)
- Top K Frequent Words (LeetCode 692)
- Sort Characters by Frequency (LeetCode 451)
- Reorganize String (LeetCode 767)
- Rearrange String k Distance Apart (LeetCode 358)

---

## Mastery Checklist
- [ ] Kth largest with min heap of size k
- [ ] Merge K sorted with heap
- [ ] Two heaps for running median
- [ ] Meeting rooms with end-time heap
- [ ] Task scheduler with frequency max heap
- [ ] Top K frequent with heap vs bucket sort tradeoff

---

## Python Heap Tips

```python
import heapq

# Min heap (default)
heap = []
heapq.heappush(heap, 3)
heapq.heappop(heap)

# Max heap (negate values)
heapq.heappush(max_heap, -val)
-max_heap[0]

# Heapify in place
heapq.heapify(list)

# Heap replace (pop then push, more efficient)
heapq.heapreplace(heap, new_val)

# Pushpop (push then pop)
heapq.heappushpop(heap, new_val)

# N largest / smallest
heapq.nlargest(n, iterable)
heapq.nsmallest(n, iterable)
```

---

## Common Traps

**Trap:** Using heap when bucket sort is faster.
- Top K frequent: bucket sort is O(n) vs heap O(n log k)
- Rule: if K is small, heap. If frequency range is bounded, bucket.

**Trap:** Forgetting to handle empty heap.
- Fix: Always check `if heap:` before `heap[0]`.

**Trap:** Heap with tuples — comparison uses first element.
- Fix: Use `(priority, counter, value)` to break ties.

**Near Miss:** Priority Queue in BFS (Dijkstra)
- Looks like heap
- But for shortest path, not top K
- Pattern blend: Graph + heap
