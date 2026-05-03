# Heap: Drills Part 2 — Warm-ups + Core Drills

---

### Problem 1. 1046. Last Stone Weight
**Archetype:** 8.1 Top K Elements
**Type:** Warm-Up
**Statement:** You are given an array of integers stones where stones[i] is the weight of the i-th stone. Play the game until there is at most one stone left. Return the weight of the last remaining stone (or 0).
**Why it fits:** The simplest max-heap problem. It teaches Python's `heapq` (which is a min-heap) by using negative values to simulate a max-heap, a pattern used in nearly every heap problem.
**The Twist:** None — the canonical "simulation with a max-heap" problem. Perfect for learning the negative-value trick.
**Code Skeleton:**
```python
from typing import List
import heapq

def lastStoneWeight(stones: List[int]) -> int:
    # Python only has min-heap; invert values for max-heap behavior
    max_heap = [-s for s in stones]
    heapq.heapify(max_heap)

    while len(max_heap) > 1:
        first = -heapq.heappop(max_heap)
        second = -heapq.heappop(max_heap)
        if first != second:
            heapq.heappush(max_heap, -(first - second))

    return -max_heap[0] if max_heap else 0
```

---

### Problem 2. 703. Kth Largest Element in a Stream
**Archetype:** 8.1 Top K Elements
**Type:** Warm-Up
**Statement:** Design a class to find the k-th largest element in a stream. Note that it is the k-th largest element in the sorted order, not the k-th distinct element.
**Why it fits:** The canonical min-heap problem for maintaining the top K. The heap size is capped at `k`, so the root is always the k-th largest. This establishes the "fixed-size heap" pattern.
**The Twist:** None — the standard template for streaming top-K. `heapq` maintains the smallest at index 0, which is exactly what we want for k-th largest.
**Code Skeleton:**
```python
from typing import List
import heapq

class KthLargest:
    def __init__(self, k: int, nums: List[int]):
        self.k = k
        self.min_heap = nums
        heapq.heapify(self.min_heap)
        # Ensure heap only contains k largest elements
        while len(self.min_heap) > k:
            heapq.heappop(self.min_heap)

    def add(self, val: int) -> int:
        heapq.heappush(self.min_heap, val)
        if len(self.min_heap) > self.k:
            heapq.heappop(self.min_heap)
        return self.min_heap[0]
```

---

### Problem 3. 215. Kth Largest Element in an Array
**Archetype:** 8.1 Top K Elements
**Type:** Warm-Up
**Statement:** Given an integer array nums and an integer k, return the k-th largest element in the array.
**Why it fits:** The most fundamental top-K problem. While solvable with Quickselect (O(n) average), the heap solution (O(n log k)) is more robust and generalizable to streaming scenarios. It reinforces the min-heap of size k pattern.
**The Twist:** None — the canonical problem for both heap and partitioning approaches. The heap solution is more intuitive and less error-prone in an interview.
**Code Skeleton:**
```python
from typing import List
import heapq

def findKthLargest(nums: List[int], k: int) -> int:
    min_heap = []
    for num in nums:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
    return min_heap[0]
```

---

### Problem 4. 347. Top K Frequent Elements
**Archetype:** 8.5 Frequency-Based
**Type:** Warm-Up
**Statement:** Given an integer array nums and an integer k, return the k most frequent elements.
**Why it fits:** Introduces the frequency map + heap combination. You count frequencies first, then use a heap to select the top k. It is the bridge between hashing and heap patterns.
**The Twist:** None — canonical frequency + heap. Python's `heapq.nlargest` can do this in one line, but building the heap manually is better for understanding.
**Code Skeleton:**
```python
from typing import List
import heapq
from collections import Counter

def topKFrequent(nums: List[int], k: int) -> List[int]:
    count = Counter(nums)
    # Use a min-heap of size k based on frequency
    min_heap = []
    for num, freq in count.items():
        heapq.heappush(min_heap, (freq, num))
        if len(min_heap) > k:
            heapq.heappop(min_heap)
    return [num for freq, num in min_heap]
```

---

### Problem 5. 1337. The K Weakest Rows in a Matrix
**Archetype:** 8.1 Top K Elements
**Type:** Warm-Up
**Statement:** You are given an m x n binary matrix mat of 1's (representing soldiers) and 0's (representing civilians). The soldiers are positioned in front of the civilians. A row i is weaker than a row j if the number of soldiers in row i is less than the number of soldiers in row j, or they have the same number of soldiers but i < j. Return the indices of the k weakest rows.
**Why it fits:** A straightforward top-K problem where the elements are not raw integers but tuples (soldier_count, index). It reinforces that heaps can order complex keys naturally.
**The Twist:** None — the canonical problem for custom keys in a heap. `heapq` compares tuples element-wise, which matches the problem's tie-breaking logic perfectly.
**Code Skeleton:**
```python
from typing import List
import heapq

def kWeakestRows(mat: List[List[int]], k: int) -> List[int]:
    heap = []
    for i, row in enumerate(mat):
        # Count soldiers using binary search or built-in count
        soldiers = sum(row)
        heapq.heappush(heap, (soldiers, i))
    return [heapq.heappop(heap)[1] for _ in range(k)]
```

---

### Problem 6. 23. Merge k Sorted Lists
**Archetype:** 8.2 Merge K Sorted
**Type:** Core Drill
**Statement:** You are given an array of k linked-lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.
**Why it fits:** The canonical "Merge K Sorted" problem. It demonstrates the core pattern of using a min-heap to always extract the smallest available element across K sorted streams.
**The Twist:** None — the standard template. Each heap element is a tuple (node.val, list_index, node) to handle tie-breaking and store the actual node reference.
**Code Skeleton:**
```python
from typing import Optional, List
import heapq

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def mergeKLists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    min_heap = []
    for i, node in enumerate(lists):
        if node:
            # (value, index, node) — index breaks ties to avoid ListNode comparison
            heapq.heappush(min_heap, (node.val, i, node))

    dummy = ListNode(0)
    curr = dummy

    while min_heap:
        val, i, node = heapq.heappop(min_heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(min_heap, (node.next.val, i, node.next))
    return dummy.next
```

---

### Problem 7. 373. Find K Pairs with Smallest Sums
**Archetype:** 8.2 Merge K Sorted
**Type:** Core Drill
**Statement:** You are given two integer arrays nums1 and nums2 sorted in non-decreasing order and an integer k. Find the k pairs with the smallest sums.
**Why it fits:** Conceptually, each element in `nums1` can be paired with all elements in `nums2` to form a sorted list of pairs. You are merging `len(nums1)` sorted lists of pairs. This is a hidden "Merge K Sorted" problem.
**The Twist:** The k sorted sequences are implicit. For `nums1[i]`, the sequence is `(nums1[i]+nums2[0], i, 0), (nums1[i]+nums2[1], i, 1), ...`. You seed the heap with the first element of each sequence.
**Code Skeleton:**
```python
from typing import List
import heapq

def kSmallestPairs(nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
    if not nums1 or not nums2:
        return []
    min_heap = []
    # Seed the heap with the first pair from each nums1 element
    for i in range(min(k, len(nums1))):
        heapq.heappush(min_heap, (nums1[i] + nums2[0], i, 0))

    result = []
    while min_heap and len(result) < k:
        s, i, j = heapq.heappop(min_heap)
        result.append([nums1[i], nums2[j]])
        if j + 1 < len(nums2):
            heapq.heappush(min_heap, (nums1[i] + nums2[j + 1], i, j + 1))
    return result
```

---

### Problem 8. 253. Meeting Rooms II
**Archetype:** 8.3 Scheduling/Intervals
**Type:** Core Drill
**Statement:** Given an array of meeting time intervals consisting of start and end times, find the minimum number of conference rooms required.
**Why it fits:** The canonical interval scheduling problem solved with a min-heap. The heap tracks end times of ongoing meetings. If a new meeting starts after the earliest ending meeting, reuse that room.
**The Twist:** None — the standard template for resource allocation over intervals. Sorting by start time is a prerequisite; the heap handles the dynamic room assignment.
**Code Skeleton:**
```python
from typing import List
import heapq

def minMeetingRooms(intervals: List[List[int]]) -> int:
    if not intervals:
        return 0
    # Sort by start time
    intervals.sort(key=lambda x: x[0])
    # Min-heap stores end times of meetings
    end_times = [intervals[0][1]]

    for start, end in intervals[1:]:
        if start >= end_times[0]:
            # Reuse the room that frees up the earliest
            heapq.heappop(end_times)
        heapq.heappush(end_times, end)

    return len(end_times)
```

---

### Problem 9. 1851. Minimum Interval to Include Each Query
**Archetype:** 8.3 Scheduling/Intervals
**Type:** Core Drill
**Statement:** You are given a 2D integer array intervals, where intervals[i] = [left_i, right_i] describes the i-th interval. You are also given an integer array queries. Return an array containing the answers to the queries.
**Why it fits:** A hard interval problem that combines sorting with a min-heap. For each query (sorted), you add all intervals that have started and remove those that have ended, then query the smallest interval size.
**The Twist:** Queries are processed offline (sorted) to leverage monotonicity. The heap stores (size, right_endpoint), allowing you to lazily discard intervals that no longer contain the current query.
**Code Skeleton:**
```python
from typing import List
import heapq

def minInterval(intervals: List[List[int]], queries: List[int]) -> List[int]:
    intervals.sort()
    # Sort queries but keep original indices
    sorted_queries = sorted((q, i) for i, q in enumerate(queries))
    result = [-1] * len(queries)
    min_heap = []
    idx = 0

    for q, original_i in sorted_queries:
        # Add all intervals that start before or at q
        while idx < len(intervals) and intervals[idx][0] <= q:
            l, r = intervals[idx]
            heapq.heappush(min_heap, (r - l + 1, r))
            idx += 1
        # Remove intervals that end before q
        while min_heap and min_heap[0][1] < q:
            heapq.heappop(min_heap)
        if min_heap:
            result[original_i] = min_heap[0][0]
    return result
```

---

### Problem 10. 295. Find Median from Data Stream
**Archetype:** 8.4 Median Finder
**Type:** Core Drill
**Statement:** The median is the middle value in an ordered integer list. If the size of the list is even, there is no middle value, and the median is the mean of the two middle values. Implement the MedianFinder class.
**Why it fits:** The definitive median-finder problem. It requires maintaining two heaps: a max-heap for the lower half and a min-heap for the upper half. The balance invariant is the key.
**The Twist:** None — the canonical dual-heap structure. Rebalancing after every insertion ensures the tops of the heaps are always the middle elements.
**Code Skeleton:**
```python
import heapq

class MedianFinder:
    def __init__(self):
        # max_heap for the lower half (inverted values)
        self.small = []
        # min_heap for the larger half
        self.large = []

    def addNum(self, num: int) -> None:
        # Push to max_heap (small), then move max to min_heap (large)
        heapq.heappush(self.small, -num)
        val = -heapq.heappop(self.small)
        heapq.heappush(self.large, val)
        # Balance sizes: small can have at most one more element than large
        if len(self.small) < len(self.large):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)

    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2.0
```

---

### Problem 11. 480. Sliding Window Median
**Archetype:** 8.4 Median Finder
**Type:** Core Drill
**Statement:** The median is the middle value in an ordered integer list. You are given an integer array nums and an integer k. There is a sliding window of size k. Return the median array for each window.
**Why it fits:** It combines the dual-heap median finder with a sliding window, requiring efficient removal of arbitrary elements. Lazy deletion using a hashmap is the standard approach.
**The Twist:** Heaps do not support efficient removal of arbitrary elements. You must use a "delayed deletion" dictionary and only discard from the heap tops when they are stale.
**Code Skeleton:**
```python
from typing import List
import heapq
from collections import defaultdict

class DualHeap:
    def __init__(self, k):
        self.small = []  # max heap (inverted)
        self.large = []  # min heap
        self.delayed = defaultdict(int)
        self.k = k
        self.small_size = 0
        self.large_size = 0

    def prune(self, heap):
        while heap:
            num = -heap[0] if heap is self.small else heap[0]
            if self.delayed[num]:
                heapq.heappop(heap)
                self.delayed[num] -= 1
            else:
                break

    def make_balance(self):
        if self.small_size > self.large_size + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
            self.small_size -= 1
            self.large_size += 1
            self.prune(self.small)
        elif self.small_size < self.large_size:
            heapq.heappush(self.small, -heapq.heappop(self.large))
            self.small_size += 1
            self.large_size -= 1
            self.prune(self.large)

    def insert(self, num):
        if not self.small or num <= -self.small[0]:
            heapq.heappush(self.small, -num)
            self.small_size += 1
        else:
            heapq.heappush(self.large, num)
            self.large_size += 1
        self.make_balance()

    def erase(self, num):
        self.delayed[num] += 1
        if num <= -self.small[0]:
            self.small_size -= 1
            if num == -self.small[0]:
                self.prune(self.small)
        else:
            self.large_size -= 1
            if self.large and num == self.large[0]:
                self.prune(self.large)
        self.make_balance()

    def get_median(self):
        if self.k % 2 == 1:
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2.0

def medianSlidingWindow(nums: List[int], k: int) -> List[float]:
    dh = DualHeap(k)
    for i in range(k):
        dh.insert(nums[i])
    result = [dh.get_median()]
    for i in range(k, len(nums)):
        dh.insert(nums[i])
        dh.erase(nums[i - k])
        result.append(dh.get_median())
    return result
```

---

### Problem 12. 692. Top K Frequent Words
**Archetype:** 8.5 Frequency-Based
**Type:** Core Drill
**Statement:** Given an array of strings words and an integer k, return the k most frequent strings.
**Why it fits:** Extends the frequency + heap pattern to strings with tie-breaking (lexicographical order). It demonstrates how to use tuples as heap keys where the primary sort is frequency (inverted) and secondary is the string itself.
**The Twist:** The ordering is high frequency first, then lexicographical for ties. A max-heap of size k with negative frequencies achieves this cleanly because Python compares tuples element-wise.
**Code Skeleton:**
```python
from typing import List
import heapq
from collections import Counter

def topKFrequent(words: List[str], k: int) -> List[str]:
    count = Counter(words)
    # Use negative frequency for max-heap behavior; word provides lexicographical tie-break
    min_heap = []
    for word, freq in count.items():
        heapq.heappush(min_heap, (-freq, word))
    # Since we want the k largest, we can just pop k times (or use nlargest)
    return [heapq.heappop(min_heap)[1] for _ in range(k)]
```

---

### Problem 13. 451. Sort Characters By Frequency
**Archetype:** 8.5 Frequency-Based
**Type:** Core Drill
**Statement:** Given a string s, sort it in decreasing order based on the frequency of the characters.
**Why it fits:** A direct application of the frequency-heap pattern. You count characters, push them onto a max-heap by frequency, and then reconstruct the string. It is a simpler variant of top-K frequent elements where k equals the number of unique elements.
**The Twist:** None — a straightforward frequency sort. It can also be solved with bucket sort, but the heap solution is more generalizable.
**Code Skeleton:**
```python
from typing import List
import heapq
from collections import Counter

def frequencySort(s: str) -> str:
    count = Counter(s)
    max_heap = [(-freq, char) for char, freq in count.items()]
    heapq.heapify(max_heap)
    result = []
    while max_heap:
        freq, char = heapq.heappop(max_heap)
        result.append(char * (-freq))
    return "".join(result)
```

---

### Problem 14. 218. The Skyline Problem
**Archetype:** 8.3 Scheduling/Intervals
**Type:** Core Drill
**Statement:** A city's skyline is the outer contour of the silhouette formed by all the buildings when viewed from a distance. Given the locations and heights of all the buildings, return the skyline formed by these buildings collectively.
**Why it fits:** The hardest pure heap problem. It treats building start/end events as interval boundaries and uses a max-heap to track the current tallest building. When the tallest changes, a key point is recorded.
**The Twist:** You must handle "enter" and "leave" events sorted by x-coordinate. Lazy deletion is required because a max-heap cannot efficiently remove arbitrary heights. A max-heap of active heights drives the contour.
**Code Skeleton:**
```python
from typing import List
import heapq

def getSkyline(buildings: List[List[int]]) -> List[List[int]]:
    # Create events: (x, height)
    # For start, use negative height to distinguish from end
    events = []
    for l, r, h in buildings:
        events.append((l, -h, r))
        events.append((r, 0, 0))
    events.sort()

    result = [[0, 0]]
    # max_heap of (-height, right_end)
    max_heap = [(0, float('inf'))]

    for x, h, r in events:
        # Remove buildings that have already ended
        while max_heap[0][1] <= x:
            heapq.heappop(max_heap)
        if h != 0:
            heapq.heappush(max_heap, (h, r))
        curr_max = -max_heap[0][0]
        if curr_max != result[-1][1]:
            result.append([x, curr_max])

    return result[1:]
```

---

### Problem 15. 632. Smallest Range Covering Elements from K Lists
**Archetype:** 8.2 Merge K Sorted
**Type:** Core Drill
**Statement:** You have k lists of sorted integers. Find the smallest range that includes at least one number from each of the k lists.
**Why it fits:** An advanced merge-K problem. You track one pointer per list in a min-heap. The current range is `[min_element, max_element_seen_so_far]`. Advancing the list that contributed the minimum shrinks the range.
**The Twist:** The range is defined by the global min and max among the k pointers. You only ever advance the minimum pointer because advancing any other pointer would only increase the range.
**Code Skeleton:**
```python
from typing import List
import heapq

def smallestRange(nums: List[List[int]]) -> List[int]:
    min_heap = []
    curr_max = float('-inf')
    # Initialize: push first element of each list
    for i in range(len(nums)):
        heapq.heappush(min_heap, (nums[i][0], i, 0))
        curr_max = max(curr_max, nums[i][0])

    result = [float('-inf'), float('inf')]

    while min_heap:
        curr_min, list_idx, elem_idx = heapq.heappop(min_heap)
        # Update best range if smaller
        if curr_max - curr_min < result[1] - result[0]:
            result = [curr_min, curr_max]
        # If this list is exhausted, we can't cover all k lists anymore
        if elem_idx + 1 == len(nums[list_idx]):
            break
        next_val = nums[list_idx][elem_idx + 1]
        heapq.heappush(min_heap, (next_val, list_idx, elem_idx + 1))
        curr_max = max(curr_max, next_val)

    return result
```

---
