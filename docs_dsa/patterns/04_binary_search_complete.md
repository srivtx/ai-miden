# Pattern 04: Binary Search — Complete Archetype Map

> **Pattern Recognition:** When you see "sorted", "O(log n)", "find minimum/maximum where condition changes", "search space" — think binary search.
>
> **Fundamental Insight:** If a sequence is sorted (or has a single peak/valley), you can eliminate half the search space with each comparison. This turns O(n) into O(log n).

---

## Archetype 4.1: Classic Search (Find Target)

### Recognition Signal (10 seconds)
Words: **"sorted array", "find", "search", "index of", "contains", "locate"**

The question is always: **"Find the position of target in a sorted array."**

### Core Structure
```
left, right = 0, len(arr) - 1
while left <= right:
    mid = left + (right - left) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
return -1
```

**Critical detail:** `left <= right` (not `<`) to check the last element. `mid = left + (right - left) // 2` prevents overflow.

### The Invariant
After each iteration, if target exists, it is in [left, right]. We halve the search space each time.

### Canonical Problem: Binary Search (LeetCode 704)
**Statement:** Find index of target in sorted array, or -1.

```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### Variation Family

**V1: Search Insert Position (LeetCode 35)**
- **Twist:** Return index where target would be inserted to maintain order
- **Change:** Return `left` when loop ends (not -1)

```python
def search_insert(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left
```

**V2: Sqrt(x) (LeetCode 69)**
- **Twist:** Compute integer square root
- **Change:** Search space is [0, x]. Find largest num where num*num <= x.

```python
def my_sqrt(x):
    left, right = 0, x
    while left <= right:
        mid = left + (right - left) // 2
        if mid * mid == x:
            return mid
        elif mid * mid < x:
            left = mid + 1
        else:
            right = mid - 1
    return right  # right is the largest with mid*mid <= x
```

**V3: Guess Number Higher or Lower (LeetCode 374)**
- **Twist:** API says if guess is too high or low
- **Change:** Same binary search, but use API instead of direct comparison.

**V4: Count Negative Numbers in Sorted Matrix (LeetCode 1351)**
- **Twist:** Row-wise and column-wise sorted matrix
- **Change:** For each row, binary search first negative. Or start from top-right and move.

**Near Miss: Search in Rotated Sorted Array**
- **Looks like:** Find target in sorted array
- **But:** Array is rotated. Need to determine which half is sorted.
- **Lesson:** Classic search assumes fully sorted. Rotated needs extra logic.

---

## Archetype 4.2: Search Space Reduction (Rotated Arrays)

### Recognition Signal (10 seconds)
Words: **"rotated", "pivot", "shifted", "sorted then rotated", "find minimum"**

The question is always: **"The array was sorted and then rotated at some unknown pivot. Find something."**

### Core Structure
```
Determine which half is sorted:
- If arr[left] <= arr[mid]: left half is sorted
- Else: right half is sorted

Decide which half to search based on target's position relative to sorted half.
```

### Canonical Problem: Find Minimum in Rotated Sorted Array (LeetCode 153)
**Statement:** Find minimum element in rotated sorted array (no duplicates).

```python
def find_min(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            # Minimum must be in right half
            left = mid + 1
        else:
            # nums[mid] < nums[right], minimum in left half including mid
            right = mid
    return nums[left]
```

**Why `left < right` (not `<=`):** We want to converge to a single element. When left == right, that's the minimum.

**Why `right = mid` (not `mid - 1`):** Because `nums[mid]` could BE the minimum.

### Variation Family

**V1: Find Minimum in Rotated Sorted Array II (LeetCode 154)**
- **Twist:** Array may contain duplicates
- **Change:** When `nums[mid] == nums[right]`, we can't tell which half. Shrink right by 1.

```python
def find_min_ii(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        elif nums[mid] < nums[right]:
            right = mid
        else:
            right -= 1
    return nums[left]
```

**V2: Search in Rotated Sorted Array (LeetCode 33)**
- **Twist:** Find target in rotated sorted array
- **Change:** Determine which half is sorted, then check if target is in that half.

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        
        # Determine which half is sorted
        if nums[left] <= nums[mid]:  # Left half sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # Right half sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

**V3: Search in Rotated Sorted Array II (LeetCode 81)**
- **Twist:** With duplicates
- **Change:** Same as II above. Handle `nums[left] == nums[mid]` by incrementing left.

**Near Miss: Find Peak Element (LeetCode 162)**
- **Looks like:** Search in unusual array
- **But:** Not rotated. Just has a single peak. Compare neighbors.
- **Lesson:** Single peak/valley can also be solved with binary search.

---

## Archetype 4.3: Boundary Detection (First/Last Occurrence)

### Recognition Signal (10 seconds)
Words: **"first occurrence", "last occurrence", "leftmost", "rightmost", "starting position", "ending position", "range"**

The question is always: **"Find the boundary where the condition changes from false to true (or vice versa)."**

### Core Structure
```
For leftmost (first true):
    while left < right:
        mid = left + (right - left) // 2
        if condition(mid):
            right = mid
        else:
            left = mid + 1
    return left

For rightmost (last true):
    while left < right:
        mid = left + (right - left + 1) // 2  # Upper mid to avoid infinite loop
        if condition(mid):
            left = mid
        else:
            right = mid - 1
    return left
```

**Critical difference:** Leftmost uses lower mid `(right - left) // 2`. Rightmost uses upper mid `(right - left + 1) // 2`. This prevents infinite loops.

### Canonical Problem: Find First and Last Position of Element (LeetCode 34)
**Statement:** Find starting and ending position of target in sorted array.

```python
def search_range(nums, target):
    def find_first():
        left, right = 0, len(nums) - 1
        while left < right:
            mid = left + (right - left) // 2
            if nums[mid] >= target:
                right = mid
            else:
                left = mid + 1
        return left if nums and nums[left] == target else -1
    
    def find_last():
        left, right = 0, len(nums) - 1
        while left < right:
            mid = left + (right - left + 1) // 2
            if nums[mid] <= target:
                left = mid
            else:
                right = mid - 1
        return left if nums and nums[left] == target else -1
    
    first = find_first()
    if first == -1:
        return [-1, -1]
    return [first, find_last()]
```

### Variation Family

**V1: First Bad Version (LeetCode 278)**
- **Twist:** Find first bad version in [1, n]
- **Change:** Binary search on version space. `isBadVersion(mid)` is the condition.

**V2: Find Smallest Letter Greater Than Target (LeetCode 744)**
- **Twist:** Find smallest letter strictly greater than target
- **Change:** Condition: `letters[mid] > target`. Wrap around if not found.

**V3: Find K Closest Elements (LeetCode 658)**
- **Twist:** Find k closest elements to x in sorted array
- **Change:** Binary search for the left boundary of the window. Compare distances.

```python
def find_closest_elements(arr, k, x):
    left, right = 0, len(arr) - k
    while left < right:
        mid = left + (right - left) // 2
        if x - arr[mid] > arr[mid + k] - x:
            left = mid + 1
        else:
            right = mid
    return arr[left:left + k]
```

**V4: Find First and Last Position (already covered)**
- **Key insight:** Two binary searches: one for left boundary, one for right boundary.

**Near Miss: Search Insert Position**
- **Looks like:** Boundary detection
- **But:** Just returns left pointer when loop ends. No separate search needed.
- **Lesson:** Single boundary can often be found by returning the convergence point.

---

## Archetype 4.4: Condition-Based Search (Peak, Valley, Transition)

### Recognition Signal (10 seconds)
Words: **"peak element", "mountain array", "find in mountain", "single peak", "bitonic"**

The question is always: **"Find the point where the trend changes."**

### Core Structure
```
Compare mid with neighbor(s):
- If arr[mid] > arr[mid+1]: peak is at or before mid
- If arr[mid] < arr[mid+1]: peak is after mid
```

### Canonical Problem: Find Peak Element (LeetCode 162)
**Statement:** Find peak element (greater than neighbors). Array may have multiple peaks.

```python
def find_peak_element(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[mid + 1]:
            right = mid
        else:
            left = mid + 1
    return left
```

**Why this works:** If `nums[mid] > nums[mid+1]`, there must be a peak in [left, mid] (could be mid itself). If `nums[mid] < nums[mid+1]`, there must be a peak in [mid+1, right].

### Variation Family

**V1: Peak Index in Mountain Array (LeetCode 852)**
- **Twist:** Strictly increasing then strictly decreasing. Find peak.
- **Change:** Same as find peak. The structure guarantees exactly one peak.

**V2: Find in Mountain Array (LeetCode 1095)**
- **Twist:** Find target in mountain array. Array access via API.
- **Change:** First find peak. Then binary search left (increasing) and right (decreasing).

```python
def find_in_mountain_array(target, mountain_arr):
    # Find peak
    left, right = 0, mountain_arr.length() - 1
    while left < right:
        mid = left + (right - left) // 2
        if mountain_arr.get(mid) < mountain_arr.get(mid + 1):
            left = mid + 1
        else:
            right = mid
    peak = left
    
    # Search left (ascending)
    left, right = 0, peak
    while left <= right:
        mid = left + (right - left) // 2
        val = mountain_arr.get(mid)
        if val == target:
            return mid
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1
    
    # Search right (descending)
    left, right = peak, mountain_arr.length() - 1
    while left <= right:
        mid = left + (right - left) // 2
        val = mountain_arr.get(mid)
        if val == target:
            return mid
        elif val < target:
            right = mid - 1
        else:
            left = mid + 1
    
    return -1
```

**V3: Single Element in Sorted Array (LeetCode 540)**
- **Twist:** Every element appears twice except one. Find it.
- **Change:** Before single element, pairs are at (even, odd). After, at (odd, even).

```python
def single_non_duplicate(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if mid % 2 == 1:
            mid -= 1
        if nums[mid] == nums[mid + 1]:
            left = mid + 2
        else:
            right = mid
    return nums[left]
```

**Near Miss: Search a 2D Matrix (LeetCode 74)**
- **Looks like:** Search with conditions
- **But:** Treat 2D matrix as 1D array. Standard binary search with index math.
- **Lesson:** Multi-dimensional search can often be flattened.

---

## Archetype 4.5: Answer Space Search (Minimize/Maximize)

### Recognition Signal (10 seconds)
Words: **"minimum speed", "maximum", "Koko eating bananas", "ship packages", "aggressive cows", "allocate", "minimize the maximum"**

The question is always: **"Find the minimum/maximum value X such that some condition is satisfied."**

### Core Structure
```
Define condition(x): returns True if x is feasible

left, right = min_possible, max_possible
while left < right:
    mid = left + (right - left) // 2
    if condition(mid):
        right = mid  # Can try smaller
    else:
        left = mid + 1  # Need larger
return left
```

**Key insight:** The answer space is "sorted" by feasibility. All values >= answer are feasible, all < answer are not.

### Canonical Problem: Koko Eating Bananas (LeetCode 875)
**Statement:** Find minimum eating speed K such that all bananas are eaten within H hours.

```python
def min_eating_speed(piles, h):
    def can_finish(k):
        hours = 0
        for pile in piles:
            hours += (pile + k - 1) // k  # Ceiling division
        return hours <= h
    
    left, right = 1, max(piles)
    while left < right:
        mid = left + (right - left) // 2
        if can_finish(mid):
            right = mid
        else:
            left = mid + 1
    return left
```

### Variation Family

**V1: Capacity To Ship Packages Within D Days (LeetCode 1011)**
- **Twist:** Find minimum ship capacity to deliver all packages within D days
- **Change:** Condition: can ship with capacity C within D days?

```python
def ship_within_days(weights, days):
    def can_ship(capacity):
        days_needed = 1
        current = 0
        for w in weights:
            if current + w > capacity:
                days_needed += 1
                current = 0
            current += w
        return days_needed <= days
    
    left, right = max(weights), sum(weights)
    while left < right:
        mid = left + (right - left) // 2
        if can_ship(mid):
            right = mid
        else:
            left = mid + 1
    return left
```

**V2: Split Array Largest Sum (LeetCode 410)**
- **Twist:** Split array into m subarrays to minimize largest sum
- **Change:** Same as ship packages. Condition: can split into m subarrays where each sum <= mid?

**V3: Minimum Limit of Balls in a Bag (LeetCode 1760)**
- **Twist:** Operations: split a bag into two with floor/ceil. Minimize max bag size after at most maxOperations.
- **Change:** Condition: can we ensure all bags <= mid with maxOperations?

**V4: Magnetic Force Between Two Balls (LeetCode 1552)**
- **Twist:** Place m balls in baskets to maximize minimum magnetic force
- **Change:** Condition: can we place m balls with at least mid distance apart?
- **Key insight:** Sort positions first. Then greedy placement + binary search on distance.

**V5: Find the Smallest Divisor Given a Threshold (LeetCode 1283)**
- **Twist:** Find smallest divisor such that sum of ceiling divisions <= threshold
- **Change:** Binary search on divisor space [1, max(nums)].

**Near Miss: Minimum Time to Complete Trips**
- **Looks like:** Minimize maximum
- **But:** Time = trips * time_per_trip. Binary search on time. Condition: can complete all trips within time?

---

## Archetype 4.6: 2D Matrix Search

### Recognition Signal (10 seconds)
Words: **"search 2D matrix", "sorted matrix", "matrix", "rows and columns sorted"**

The question is always: **"Find target in a matrix where rows and/or columns are sorted."**

### Core Structure
```
Option 1: Treat as 1D array (row-major order)
Option 2: Start from top-right (or bottom-left) and eliminate row/column
```

### Canonical Problem: Search a 2D Matrix (LeetCode 74)
**Statement:** Matrix: each row sorted, first element of each row > last element of previous row.

```python
def search_matrix(matrix, target):
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        row, col = mid // n, mid % n
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] < target:
            left = mid + 1
        else:
            right = mid - 1
    return False
```

### Variation Family

**V1: Search a 2D Matrix II (LeetCode 240)**
- **Twist:** Each row sorted left-to-right, each column sorted top-to-bottom
- **Change:** Start from top-right. If target < current, go left. If target > current, go down.

```python
def search_matrix_ii(matrix, target):
    if not matrix or not matrix[0]:
        return False
    row, col = 0, len(matrix[0]) - 1
    while row < len(matrix) and col >= 0:
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] > target:
            col -= 1
        else:
            row += 1
    return False
```

**V2: Kth Smallest Element in Sorted Matrix (LeetCode 378)**
- **Twist:** Find kth smallest in matrix where rows/columns sorted
- **Change:** Binary search on value space. Count elements <= mid.

```python
def kth_smallest(matrix, k):
    n = len(matrix)
    left, right = matrix[0][0], matrix[-1][-1]
    
    def count_less_equal(x):
        count = 0
        row, col = n - 1, 0
        while row >= 0 and col < n:
            if matrix[row][col] <= x:
                count += row + 1
                col += 1
            else:
                row -= 1
        return count
    
    while left < right:
        mid = left + (right - left) // 2
        if count_less_equal(mid) < k:
            left = mid + 1
        else:
            right = mid
    return left
```

**Near Miss: Median of Two Sorted Arrays**
- **Looks like:** Search in sorted structures
- **But:** Binary search on partition point, not element value.
- **Lesson:** This is the hardest binary search problem. Requires finding correct partition.

---

## Archetype 4.7: Advanced — Median of Two Sorted Arrays

### Recognition Signal (10 seconds)
Words: **"median of two sorted arrays", "O(log(min(m,n)))"**

This is the classic "hard" binary search problem.

### Canonical Problem: Median of Two Sorted Arrays (LeetCode 4)
**Statement:** Find median of two sorted arrays in O(log(m+n)).

```python
def find_median_sorted_arrays(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    
    m, n = len(nums1), len(nums2)
    left, right = 0, m
    
    while left <= right:
        partition_x = (left + right) // 2
        partition_y = (m + n + 1) // 2 - partition_x
        
        max_left_x = float('-inf') if partition_x == 0 else nums1[partition_x - 1]
        min_right_x = float('inf') if partition_x == m else nums1[partition_x]
        
        max_left_y = float('-inf') if partition_y == 0 else nums2[partition_y - 1]
        min_right_y = float('inf') if partition_y == n else nums2[partition_y]
        
        if max_left_x <= min_right_y and max_left_y <= min_right_x:
            if (m + n) % 2 == 0:
                return (max(max_left_x, max_left_y) + min(min_right_x, min_right_y)) / 2
            else:
                return max(max_left_x, max_left_y)
        elif max_left_x > min_right_y:
            right = partition_x - 1
        else:
            left = partition_x + 1
```

**Key insight:** Partition both arrays such that left half has (m+n+1)//2 elements. All elements in left half <= all in right half.

---

## Pattern 04 Mastery Checklist

Before moving to Pattern 05, confirm you can:

- [ ] **Classic:** Write binary search without looking it up. Know `left <= right` vs `left < right`.
- [ ] **Rotated:** Handle rotated sorted array. Determine which half is sorted.
- [ ] **Boundary:** Find first and last occurrence. Know upper vs lower mid.
- [ ] **Peak:** Find peak element. Compare with neighbor.
- [ ] **Answer Space:** Set up binary search on answer space. Write condition function.
- [ ] **2D Matrix:** Search in sorted 2D matrix (both flatten and top-right approaches).
- [ ] **Median:** Understand partition-based binary search for two arrays.

---

*Next: Pattern 05 — Sliding Window*
