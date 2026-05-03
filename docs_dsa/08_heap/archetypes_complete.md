# Pattern 08: Heap — Complete Archetype Map

> **Pattern Recognition:** When you see "top K", "smallest/largest K", "merge sorted", "median", "frequency", "schedule" — think heap.
>
> **Fundamental Insight:** A heap gives O(log n) insertion and O(log n) extraction of the min/max element. Use it when you need to repeatedly access the smallest or largest element, or maintain a running ordered collection of elements.

---

## Archetype 8.1: Top K Elements

### Recognition Signal (10 seconds)
Words: **"top K", "K largest", "K smallest", "K most frequent", "K closest"**

The question: **"Find the K largest/smallest/frequent elements from a collection."**

### Core Structure
```python
import heapq

def top_k(nums, k):
    # Min heap for K largest
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)  # Remove smallest
    return heap  # Contains K largest

# For K smallest, use max heap (negate values)
def k_smallest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, -num)
        if len(heap) > k:
            heapq.heappop(heap)
    return [-x for x in heap]
```

### The Invariant
For "K largest", maintain a min-heap of size K. The heap root is the Kth largest element. If a new element is larger than the root, it belongs in the top K. For "K smallest", maintain a max-heap (negated min-heap in Python) of size K.

### Canonical Problem: Kth Largest Element in an Array (LeetCode 215)
**Statement:** Find the kth largest element in an unsorted array.

```python
import heapq

def find_kth_largest(nums, k):
    min_heap = []
    for num in nums:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
    return min_heap[0]
```

### Variation Family

**V1: Top K Frequent Elements (LeetCode 347)**
- **Twist:** Find k most frequent elements
- **Change:** Count frequencies, then heap of (frequency, element). Or bucket sort by frequency

```python
import heapq
from collections import Counter

def top_k_frequent(nums, k):
    count = Counter(nums)
    # Heap of (frequency, element), keep k largest frequencies
    return heapq.nlargest(k, count.keys(), key=count.get)
```

**V2: Find K Closest Elements (LeetCode 658)**
- **Twist:** Find k closest elements to x in sorted array
- **Change:** Heap of (distance, value), or binary search + two pointers

```python
import heapq

def find_closest_elements(arr, k, x):
    # Max heap based on distance
    heap = []
    for num in arr:
        dist = abs(num - x)
        heapq.heappush(heap, (-dist, -num))
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted([-x[1] for x in heap])
```

**V3: Kth Largest Element in a Stream (LeetCode 703)**
- **Twist:** Design class to find kth largest as new elements arrive
- **Change:** Maintain min-heap of size k. Add new element, pop if exceeds k

```python
import heapq

class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = nums
        heapq.heapify(self.heap)
        while len(self.heap) > k:
            heapq.heappop(self.heap)
    
    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]
```

**V4: Sort Characters By Frequency (LeetCode 451)**
- **Twist:** Sort string by character frequency descending
- **Change:** Count frequencies, use max heap (negate) or bucket sort

**Near Miss: Quickselect for Kth Largest**
- **Looks like:** Top K
- **But:** Average O(n) using partitioning instead of heap
- **Lesson:** Heap is O(n log k), quickselect is O(n) average but O(n^2) worst case

---

## Archetype 8.2: Merge K Sorted

### Recognition Signal (10 seconds)
Words: **"merge k sorted", "combine sorted lists", "smallest range", "k sorted arrays"**

The question: **"Combine multiple sorted sequences into one sorted sequence."**

### Core Structure
```python
import heapq

def merge_k_sorted(lists):
    heap = []
    # Push first element of each list: (value, list_index, element_index)
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

### The Invariant
The heap always contains the smallest unprocessed element from each list. The minimum of these is the next element in the merged result. After extracting, we push the next element from that same list.

### Canonical Problem: Merge k Sorted Lists (LeetCode 23)
**Statement:** Merge k sorted linked lists and return one sorted list.

```python
import heapq

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    
    def __lt__(self, other):
        return self.val < other.val

def merge_k_lists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    
    dummy = ListNode(0)
    curr = dummy
    
    while heap:
        val, i, node = heapq.heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    
    return dummy.next
```

### Variation Family

**V1: Find Smallest Range Covering Elements from K Lists (LeetCode 632)**
- **Twist:** Smallest range with at least one element from each of k lists
- **Change:** Track min and max as we merge. Update smallest range when we have one from each list

```python
import heapq

def smallest_range(lists):
    heap = []
    curr_max = float('-inf')
    
    for i, lst in enumerate(lists):
        heapq.heappush(heap, (lst[0], i, 0))
        curr_max = max(curr_max, lst[0])
    
    best_range = [-float('inf'), float('inf')]
    
    while len(heap) == len(lists):
        curr_min, i, j = heapq.heappop(heap)
        
        if curr_max - curr_min < best_range[1] - best_range[0]:
            best_range = [curr_min, curr_max]
        
        if j + 1 < len(lists[i]):
            next_val = lists[i][j + 1]
            heapq.heappush(heap, (next_val, i, j + 1))
            curr_max = max(curr_max, next_val)
    
    return best_range
```

**V2: The Skyline Problem (LeetCode 218)**
- **Twist:** Draw skyline from building outlines
- **Change:** Sweep line. Events: building start (add height), building end (remove height). Max heap of active heights

**V3: Ugly Number II (LeetCode 264)**
- **Twist:** Find nth ugly number (factors only 2, 3, 5)
- **Change:** Min-heap starting with 1. Pop smallest, push *2, *3, *5. Use set to avoid duplicates

```python
import heapq

def nth_ugly_number(n):
    heap = [1]
    seen = {1}
    factors = [2, 3, 5]
    
    for _ in range(n - 1):
        curr = heapq.heappop(heap)
        for f in factors:
            nxt = curr * f
            if nxt not in seen:
                seen.add(nxt)
                heapq.heappush(heap, nxt)
    
    return heap[0]
```

**Near Miss: Merge Two Sorted Lists**
- **Looks like:** Merge K sorted
- **But:** Only two lists. Two pointers are simpler and O(1) space
- **Lesson:** K >= 3 is where heap shines; K = 2 often has a simpler solution

---

## Archetype 8.3: Scheduling / Interval Problems

### Recognition Signal (10 seconds)
Words: **"meeting rooms", "intervals", "schedule", "minimum rooms", "overlap"**

The question: **"Determine optimal scheduling or resource allocation using ordering."**

### Core Structure
```python
import heapq

def scheduling(intervals):
    # Sort by start time
    intervals.sort(key=lambda x: x[0])
    
    # Min heap of end times (rooms occupied)
    heap = []
    
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heappop(heap)  # Room freed up
        heapq.heappush(heap, end)
    
    return len(heap)  # Minimum rooms needed
```

### The Invariant
The heap stores end times of ongoing meetings. If the earliest ending meeting finishes before the current meeting starts, we reuse that room (pop and push new end time). Otherwise, we need a new room.

### Canonical Problem: Meeting Rooms II (LeetCode 253)
**Statement:** Given intervals, find minimum number of conference rooms required.

```python
import heapq

def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    
    intervals.sort(key=lambda x: x[0])
    rooms = []
    heapq.heappush(rooms, intervals[0][1])
    
    for start, end in intervals[1:]:
        if rooms[0] <= start:
            heapq.heappop(rooms)
        heapq.heappush(rooms, end)
    
    return len(rooms)
```

### Variation Family

**V1: Employee Free Time (LeetCode 759)**
- **Twist:** Find common free time across all employees' schedules
- **Change:** Merge all intervals, find gaps between consecutive intervals

```python
import heapq

def employee_free_time(schedule):
    # schedule[i] = list of [start, end] for employee i
    heap = []
    for i, employee in enumerate(schedule):
        if employee:
            heapq.heappush(heap, (employee[0][0], i, 0))
    
    result = []
    prev_end = None
    
    while heap:
        start, emp_idx, interval_idx = heapq.heappop(heap)
        
        if prev_end is not None and start > prev_end:
            result.append([prev_end, start])
        
        prev_end = max(prev_end, schedule[emp_idx][interval_idx][1]) if prev_end is not None else schedule[emp_idx][interval_idx][1]
        
        if interval_idx + 1 < len(schedule[emp_idx]):
            nxt_start = schedule[emp_idx][interval_idx + 1][0]
            heapq.heappush(heap, (nxt_start, emp_idx, interval_idx + 1))
    
    return result
```

**V2: Minimum Interval to Include Each Query (LeetCode 1851)**
- **Twist:** For each query, find smallest interval containing it
- **Change:** Sort queries and intervals by start. Use min-heap of (size, end). Remove intervals that ended before query

```python
import heapq

def min_interval(intervals, queries):
    intervals.sort()
    sorted_queries = sorted((q, i) for i, q in enumerate(queries))
    result = [-1] * len(queries)
    heap = []
    idx = 0
    
    for query, original_idx in sorted_queries:
        while idx < len(intervals) and intervals[idx][0] <= query:
            start, end = intervals[idx]
            heapq.heappush(heap, (end - start + 1, end))
            idx += 1
        
        while heap and heap[0][1] < query:
            heapq.heappop(heap)
        
        if heap:
            result[original_idx] = heap[0][0]
    
    return result
```

**V3: Maximum CPU Load (LeetCode premium, similar to 253)**
- **Twist:** Jobs have start, end, and load. Find maximum overlapping load
- **Change:** Heap stores (end_time, load). Track current load as we add/remove jobs

**Near Miss: Non-overlapping Intervals**
- **Looks like:** Scheduling
- **But:** Greedy: sort by end time, count removals. No heap needed
- **Lesson:** Not all interval problems need heaps; check if greedy suffices

---

## Archetype 8.4: Median Finder (Two Heaps)

### Recognition Signal (10 seconds)
Words: **"median", "running median", "find median", "data stream", "sliding window median"**

The question: **"Find the median of a dynamically changing dataset."**

### Core Structure
```python
import heapq

class MedianFinder:
    def __init__(self):
        # Max heap for lower half (negated values)
        self.small = []
        # Min heap for upper half
        self.large = []
    
    def add_num(self, num):
        # Add to small (max heap)
        heapq.heappush(self.small, -num)
        
        # Ensure every element in small <= every element in large
        if (self.small and self.large and
            (-self.small[0]) > self.large[0]):
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        
        # Balance sizes: small can have at most 1 more element
        if len(self.small) > len(self.large) + 1:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        elif len(self.large) > len(self.small):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)
    
    def find_median(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
```

### The Invariant
The `small` max-heap contains the smaller half of numbers, `large` min-heap contains the larger half. All elements in `small` are <= all elements in `large`. The heaps differ in size by at most 1. This ensures the median is either the top of the larger heap or the average of both tops.

### Canonical Problem: Find Median from Data Stream (LeetCode 295)
**Statement:** Design data structure that supports adding integers and finding median.

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.small = []  # Max heap (negated)
        self.large = []  # Min heap
    
    def add_num(self, num):
        heapq.heappush(self.small, -num)
        
        # Balance: max of small should be <= min of large
        if (self.small and self.large and
            (-self.small[0]) > self.large[0]):
            heapq.heappush(self.large, -heapq.heappop(self.small))
        
        # Size balance
        if len(self.small) > len(self.large) + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        elif len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))
    
    def find_median(self):
        if len(self.small) > len(self.large):
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2.0
```

### Variation Family

**V1: Sliding Window Median (LeetCode 480)**
- **Twist:** Find median in every window of size k
- **Change:** Two heaps with lazy deletion using hash map. Balance heaps after each slide
- **Key insight:** Heaps don't support arbitrary deletion, so mark deleted elements and clean up tops

```python
import heapq
from collections import defaultdict

def median_sliding_window(nums, k):
    small = []  # Max heap (negated)
    large = []  # Min heap
    delayed = defaultdict(int)
    
    def prune(heap):
        while heap:
            num = -heap[0] if heap is small else heap[0]
            if delayed[num]:
                heapq.heappop(heap)
                delayed[num] -= 1
            else:
                break
    
    def make_balance():
        if len(small) > len(large) + 1:
            heapq.heappush(large, -heapq.heappop(small))
            prune(small)
        elif len(small) < len(large):
            heapq.heappush(small, -heapq.heappop(large))
            prune(large)
    
    def insert(num):
        if not small or num <= -small[0]:
            heapq.heappush(small, -num)
        else:
            heapq.heappush(large, num)
        make_balance()
    
    def erase(num):
        delayed[num] += 1
        if num <= -small[0]:
            if num == -small[0]:
                prune(small)
        else:
            if large and num == large[0]:
                prune(large)
        make_balance()
    
    def get_median():
        if k % 2 == 1:
            return float(-small[0])
        return (-small[0] + large[0]) / 2.0
    
    for i in range(k):
        insert(nums[i])
    result = [get_median()]
    
    for i in range(k, len(nums)):
        insert(nums[i])
        erase(nums[i - k])
        result.append(get_median())
    
    return result
```

**V2: IPO (LeetCode 502)**
- **Twist:** Maximize capital by picking at most k projects
- **Change:** Sort by capital requirement. Use min-heap for available capital, max-heap (negate) for profits of affordable projects

```python
import heapq

def find_maximized_capital(k, w, profits, capital):
    projects = sorted(zip(capital, profits))
    available = []
    idx = 0
    
    for _ in range(k):
        while idx < len(projects) and projects[idx][0] <= w:
            heapq.heappush(available, -projects[idx][1])
            idx += 1
        if available:
            w += -heapq.heappop(available)
        else:
            break
    return w
```

**Near Miss: Sorting to Find Median**
- **Looks like:** Median finder
- **But:** If all data is known upfront and static, sorting is O(n log n) and simpler
- **Lesson:** Two heaps shine when data arrives dynamically or incrementally

---

## Archetype 8.5: Frequency-Based

### Recognition Signal (10 seconds)
Words: **"frequency", "most frequent", "least frequent", " reorganize string", "task scheduler"**

The question: **"Use element frequencies to determine ordering or feasibility."**

### Core Structure
```python
from collections import Counter
import heapq

def frequency_based(nums):
    count = Counter(nums)
    # Max heap of (-frequency, element)
    heap = [(-freq, num) for num, freq in count.items()]
    heapq.heapify(heap)
    
    while heap:
        freq, num = heapq.heappop(heap)
        # Use the most frequent element
```

### The Invariant
The most frequent element is the most constrained resource. Greedy algorithms that use the most frequent element first often yield optimal or valid solutions for rearrangement and scheduling problems.

### Canonical Problem: Task Scheduler (LeetCode 621)
**Statement:** Given tasks and cooling time n, find least number of units of time to finish all tasks.

```python
import heapq
from collections import Counter, deque

def least_interval(tasks, n):
    count = Counter(tasks)
    max_heap = [-cnt for cnt in count.values()]
    heapq.heapify(max_heap)
    
    time = 0
    queue = deque()  # (count, available_time)
    
    while max_heap or queue:
        time += 1
        
        if max_heap:
            cnt = 1 + heapq.heappop(max_heap)  # Execute most frequent task
            if cnt < 0:
                queue.append((cnt, time + n))
        
        if queue and queue[0][1] == time:
            heapq.heappush(max_heap, queue.popleft()[0])
    
    return time
```

### Variation Family

**V1: Reorganize String (LeetCode 767)**
- **Twist:** Rearrange string so no two adjacent characters are same
- **Change:** Greedy: always place most frequent remaining character, ensuring it's not the same as last placed

```python
import heapq
from collections import Counter

def reorganize_string(s):
    count = Counter(s)
    max_heap = [(-cnt, char) for char, cnt in count.items()]
    heapq.heapify(max_heap)
    
    result = []
    prev_count, prev_char = 0, ''
    
    while max_heap:
        count, char = heapq.heappop(max_heap)
        result.append(char)
        
        if prev_count < 0:
            heapq.heappush(max_heap, (prev_count, prev_char))
        
        prev_count, prev_char = count + 1, char
    
    result = ''.join(result)
    return result if len(result) == len(s) else ""
```

**V2: Rearrange String k Distance Apart (LeetCode 358)**
- **Twist:** Same characters must be at least k distance apart
- **Change:** Use queue to track when a character becomes available again

**V3: Reduce Array Size to The Half (LeetCode 1338)**
- **Twist:** Remove elements so at least half of array is removed. Minimize distinct elements removed
- **Change:** Count frequencies, greedily remove most frequent first

```python
import heapq
from collections import Counter

def min_set_size(arr):
    count = Counter(arr)
    frequencies = [-c for c in count.values()]
    heapq.heapify(frequencies)
    
    removed = 0
    sets = 0
    target = len(arr) // 2
    
    while removed < target:
        removed += -heapq.heappop(frequencies)
        sets += 1
    
    return sets
```

**V4: Seat Reservation Manager (LeetCode 1845)**
- **Twist:** Manage seat reservations and unreservations
- **Change:** Min-heap of available seats. Reserve pops smallest, unreserve pushes back

```python
import heapq

class SeatManager:
    def __init__(self, n):
        self.available = list(range(1, n + 1))
        heapq.heapify(self.available)
    
    def reserve(self):
        return heapq.heappop(self.available)
    
    def unreserve(self, seat_number):
        heapq.heappush(self.available, seat_number)
```

**Near Miss: Top K Frequent Words**
- **Looks like:** Frequency-based
- **But:** Requires tie-breaking by lexicographical order
- **Lesson:** Heap tuple ordering: `(-freq, word)` gives correct ordering in Python since tuples compare element by element

---

## Pattern 08 Mastery Checklist

Before moving to Pattern 09, confirm you can:

- [ ] Use min-heap to find K largest elements
- [ ] Use max-heap (negation) to find K smallest elements
- [ ] Merge K sorted lists/arrays with heap in O(N log k)
- [ ] Find Kth largest in stream with fixed-size heap
- [ ] Design median finder with two heaps
- [ ] Implement sliding window median with lazy deletion
- [ ] Solve meeting rooms II with end-time heap
- [ ] Use max-heap for greedy frequency-based scheduling
- [ ] Reorganize string using greedy + heap
- [ ] Distinguish: when to use heap vs sorting vs quickselect
- [ ] Handle Python's min-heap only limitation with negation

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Using sort instead of heap for streaming data | O(n log n) per insertion instead of O(log n) | Use heap when data arrives dynamically |
| Forgetting Python only has min-heap | Wrong ordering for max-heap problems | Negate values: `heapq.heappush(heap, -val)` |
| Not balancing two heaps | Median is wrong | After each insertion, ensure size diff <= 1 |
| Heap with tuples: wrong element comparison | Heap orders by first element, unexpected behavior | Structure tuple as `(primary_key, secondary_key, data)` |
| Merge K sorted with full sort | O(N log N) instead of O(N log k) | Only keep k elements in heap, one from each list |
| Not handling empty heap | Runtime error | Always check `if heap:` before heappop |
| Confusing heapify vs heappush | heapify is O(n), n heappushes is O(n log n) | Build heap with `heapq.heapify(data)` when all data known |
| Sliding window median: not pruning | Stale data at heap tops | Implement lazy deletion with hash map |

---

## Pattern Blends (What Comes Next)

Heap does not live in isolation. It blends with:

- **Greedy:** Always pick most/least frequent, largest profit, earliest ending
- **Two Heaps:** Median finder, sliding window median
- **Hash Map:** Count frequencies, then heap for ordering
- **Linked List:** Merge k sorted linked lists
- **Intervals:** Meeting rooms, employee free time
- **BFS/Priority Queue:** Dijkstra's algorithm, uniform cost search

---

*Next: Pattern 09 — Backtracking*

(End of file)
