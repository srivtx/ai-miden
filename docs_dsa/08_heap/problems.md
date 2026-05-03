# Pattern 08: Heap — Practice Problems

## Top K Elements

### 215. Kth Largest Element in an Array
**Statement:** Find kth largest.
**Code (Min Heap):**
```python
import heapq

def find_kth_largest(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)
    return heap[0]
```

**Alternative (QuickSelect):** Average O(n), worst O(n^2).

### 378. Kth Smallest Element in a Sorted Matrix
**Statement:** Kth smallest in row/col sorted matrix.
**Intuition:** Min heap of (value, row, col). Pop smallest, push next in row.

### 373. Find K Pairs with Smallest Sums
**Statement:** K pairs with smallest sums from two sorted arrays.
**Intuition:** Heap of (sum, i, j). Push (nums1[i]+nums2[j+1]) and (nums1[i+1]+nums2[j]).

### 973. K Closest Points to Origin
**Statement:** K closest points to (0,0).
**Intuition:** Max heap of size k on distance squared. Or sort.

### 347. Top K Frequent Elements
**Statement:** K most frequent elements.
**Intuition:** Count frequencies. Heap of size k on frequency. Or bucket sort.
**Code:**
```python
def top_k_frequent(nums, k):
    from collections import Counter
    count = Counter(nums)
    return heapq.nlargest(k, count.keys(), key=count.get)
```

---

## Merge K Sorted

### 23. Merge k Sorted Lists
**Statement:** Merge k sorted linked lists.
**Intuition:** Min heap of (node.val, list_index, node).
**Code:**
```python
def merge_k_lists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    
    dummy = ListNode(0)
    current = dummy
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

### 632. Smallest Range Covering Elements from K Lists
**Statement:** Smallest range with one element from each list.
**Intuition:** Heap of (value, list_idx, elem_idx). Track max. Move pointer of min.

---

## Scheduling

### 253. Meeting Rooms II
**Statement:** Minimum meeting rooms required.
**Intuition:** Sort by start. Min heap of end times. Reuse room if start >= min end.
**Code:**
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

### 621. Task Scheduler
**Statement:** Minimum intervals to complete all tasks with cooling n.
**Intuition:** Max heap for task frequencies. Execute most frequent, put in cooldown queue.

### 767. Reorganize String
**Statement:** Rearrange so no two adjacent are same.
**Intuition:** Max heap on frequency. Pop two most frequent, append, push back if remaining.

### 1094. Car Pooling
**Statement:** Can car accommodate all trips?
**Intuition:** Sort by start. Heap of (end, passengers). Remove trips that ended.

### 759. Employee Free Time
**Statement:** Find common free time intervals.
**Intuition:** Merge all intervals, find gaps.

---

## Median & Two Heaps

### 295. Find Median from Data Stream
**Statement:** Running median.
**Intuition:** Small (max heap) and large (min heap). Balance sizes.
**Code:**
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

### 480. Sliding Window Median
**Statement:** Median in every window of size k.
**Intuition:** Two heaps + lazy deletion hash map. Balance and clean tops.

### 502. IPO
**Statement:** Maximize initial capital with k projects.
**Intuition:** Sort by minimum capital. Use max heap for available projects by profit.

---

## Frequency-Based

### 692. Top K Frequent Words
**Statement:** Top k frequent words, sorted by frequency then lexicographical.
**Intuition:** Heap of (-frequency, word). Or sort.

### 451. Sort Characters by Frequency
**Statement:** Sort by decreasing frequency.
**Intuition:** Count, then build string by frequency.

### 358. Rearrange String k Distance Apart
**Statement:** Same characters at least k apart.
**Intuition:** Max heap + wait queue. Track next available time.

---

## Near Misses & Advanced

**Near Miss: Dijkstra's Algorithm**
- Uses heap for shortest path
- Not "top K" but "minimum distance"
- Pattern blend: Graph + heap

**Near Miss: Prim's / Kruskal's MST**
- Prim's uses heap for minimum edge
- Advanced graphs pattern

**Near Miss: Huffman Coding**
- Greedy + heap
- Build tree by combining least frequent

---

## Mixed Drill Set

1. 215 — Kth largest
2. 23 — Merge k sorted
3. 253 — Meeting rooms
4. 295 — Running median
5. 347 — Top K frequent
6. 621 — Task scheduler
7. 378 — Kth smallest matrix
8. 973 — K closest points
9. 373 — K pairs smallest sums
10. 480 — Sliding window median
