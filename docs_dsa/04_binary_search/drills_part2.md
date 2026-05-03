# Pattern 04: Binary Search — Drills Part 2

> 5 Warm-ups + 10 Core Drills

---

## Warm-Ups

### 1. LeetCode 704. Binary Search
**Archetype:** 4.1 Classic Search
**Type:** Warm-Up
**Statement:** Find the index of target in a sorted array, or -1.
**Why it fits:** This is the canonical binary search problem. The array is sorted, and we can eliminate half the search space with each comparison by comparing the middle element to the target.
**The Twist:** None — this is the template from which all other binary search problems derive.
**Code Skeleton:**
```python
def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2  # Avoid overflow
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### 2. LeetCode 35. Search Insert Position
**Archetype:** 4.1 Classic Search
**Type:** Warm-Up
**Statement:** Return the index where target would be inserted to maintain order.
**Why it fits:** Identical structure to classic search, but instead of returning -1 when the target is missing, we return the `left` pointer where the target should go.
**The Twist:** The target may not exist; the answer is the convergence point of the search boundaries.
**Code Skeleton:**
```python
def search_insert(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left  # Convergence point is the insert position
```

### 3. LeetCode 69. Sqrt(x)
**Archetype:** 4.1 Classic Search
**Type:** Warm-Up
**Statement:** Compute and return the integer square root of x.
**Why it fits:** The search space [0, x] is conceptually sorted by the predicate `mid * mid <= x`. We find the largest value satisfying the condition.
**The Twist:** There is no explicit array; the search space is a numeric range.
**Code Skeleton:**
```python
def my_sqrt(x: int) -> int:
    if x < 2:
        return x
    left, right = 1, x // 2
    while left <= right:
        mid = left + (right - left) // 2
        sq = mid * mid
        if sq == x:
            return mid
        elif sq < x:
            left = mid + 1
        else:
            right = mid - 1
    return right  # right is the largest with mid*mid <= x
```

### 4. LeetCode 278. First Bad Version
**Archetype:** 4.3 Boundary Detection
**Type:** Warm-Up
**Statement:** Find the first bad version in [1, n] using the `isBadVersion` API.
**Why it fits:** Versions are implicitly sorted: all good versions come before all bad versions. We binary search for the boundary where the predicate changes from false to true.
**The Twist:** The condition is hidden behind an API; we only know if a version is bad, not the underlying data.
**Code Skeleton:**
```python
def first_bad_version(n: int) -> int:
    left, right = 1, n
    while left < right:
        mid = left + (right - left) // 2
        if isBadVersion(mid):  # API provided by platform
            right = mid
        else:
            left = mid + 1
    return left
```

### 5. LeetCode 367. Valid Perfect Square
**Archetype:** 4.1 Classic Search
**Type:** Warm-Up
**Statement:** Return True if num is a perfect square, else False.
**Why it fits:** Binary search for an integer square root. If we find an exact match, it is a perfect square.
**The Twist:** Must verify exact equality; if the loop terminates without finding it, the number is not a perfect square.
**Code Skeleton:**
```python
def is_perfect_square(num: int) -> bool:
    if num < 2:
        return True
    left, right = 1, num // 2
    while left <= right:
        mid = left + (right - left) // 2
        sq = mid * mid
        if sq == num:
            return True
        elif sq < num:
            left = mid + 1
        else:
            right = mid - 1
    return False
```

---

## Core Drills

### 6. LeetCode 33. Search in Rotated Sorted Array
**Archetype:** 4.2 Search Space Reduction (Rotated)
**Type:** Core Drill
**Statement:** Find target in a rotated sorted array with no duplicates.
**Why it fits:** The array was sorted then rotated, so one half is always sorted. We determine which half is sorted, then check if target lies within that sorted half.
**The Twist:** Cannot assume the entire array is sorted; must compare `nums[left]` with `nums[mid]` to identify the sorted half.
**Code Skeleton:**
```python
def search_rotated(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        # Determine which half is sorted
        if nums[left] <= nums[mid]:  # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

### 7. LeetCode 153. Find Minimum in Rotated Sorted Array
**Archetype:** 4.2 Search Space Reduction (Rotated)
**Type:** Core Drill
**Statement:** Find the minimum element in a rotated sorted array with no duplicates.
**Why it fits:** Comparing `nums[mid]` with `nums[right]` tells us which half contains the minimum. If `nums[mid] > nums[right]`, the minimum is in the right half.
**The Twist:** Uses `left < right` (not `<=`) and `right = mid` (not `mid - 1`) because `nums[mid]` itself could be the minimum.
**Code Skeleton:**
```python
def find_min(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            # nums[mid] < nums[right], min is in left half including mid
            right = mid
    return nums[left]
```

### 8. LeetCode 34. Find First and Last Position of Element in Sorted Array
**Archetype:** 4.3 Boundary Detection
**Type:** Core Drill
**Statement:** Find the starting and ending position of target in a sorted array.
**Why it fits:** We need two boundaries: the leftmost occurrence and the rightmost. Each requires a slightly different binary search to avoid infinite loops.
**The Twist:** The right-boundary search must use upper mid `(right - left + 1) // 2` to prevent infinite loops when only two elements remain.
**Code Skeleton:**
```python
def search_range(nums: list[int], target: int) -> list[int]:
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
            mid = left + (right - left + 1) // 2  # Upper mid
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

### 9. LeetCode 162. Find Peak Element
**Archetype:** 4.4 Condition-Based Search
**Type:** Core Drill
**Statement:** Find a peak element (greater than its neighbors) in an array.
**Why it fits:** Although the array is not globally sorted, it has a single-peak structure locally. Comparing `nums[mid]` with `nums[mid + 1]` tells us which half contains a peak.
**The Twist:** We only need to compare with one neighbor; if `nums[mid] < nums[mid+1]`, a peak must exist to the right.
**Code Skeleton:**
```python
def find_peak_element(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[mid + 1]:
            right = mid
        else:
            left = mid + 1
    return left
```

### 10. LeetCode 74. Search a 2D Matrix
**Archetype:** 4.6 2D Matrix Search
**Type:** Core Drill
**Statement:** Search for target in a matrix where each row is sorted and the first element of each row is greater than the last of the previous row.
**Why it fits:** The matrix can be conceptually flattened into a 1D sorted array. We use index math to convert 1D mid to 2D coordinates.
**The Twist:** Index conversion: `row = mid // n`, `col = mid % n`.
**Code Skeleton:**
```python
def search_matrix(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1
    while left <= right:
        mid = left + (right - left) // 2
        row, col = mid // n, mid % n
        val = matrix[row][col]
        if val == target:
            return True
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1
    return False
```

### 11. LeetCode 875. Koko Eating Bananas
**Archetype:** 4.5 Answer Space Search
**Type:** Core Drill
**Statement:** Find the minimum eating speed K such that all bananas are eaten within H hours.
**Why it fits:** We binary search on the answer space [1, max(piles)]. The feasibility function `can_finish(k)` is monotonic: if speed k works, any speed > k also works.
**The Twist:** The condition function computes total hours using ceiling division: `(pile + k - 1) // k`.
**Code Skeleton:**
```python
def min_eating_speed(piles: list[int], h: int) -> int:
    def can_finish(k: int) -> bool:
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

### 12. LeetCode 1011. Capacity To Ship Packages Within D Days
**Archetype:** 4.5 Answer Space Search
**Type:** Core Drill
**Statement:** Find the minimum ship capacity to deliver all packages within D days.
**Why it fits:** The answer space is [max(weights), sum(weights)]. We binary search on capacity and greedily check if a given capacity allows shipping within D days.
**The Twist:** The condition function requires a greedy simulation to count days needed for a given capacity.
**Code Skeleton:**
```python
def ship_within_days(weights: list[int], days: int) -> int:
    def can_ship(capacity: int) -> bool:
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

### 13. LeetCode 852. Peak Index in a Mountain Array
**Archetype:** 4.4 Condition-Based Search
**Type:** Core Drill
**Statement:** Find the peak index in a strictly increasing then strictly decreasing array.
**Why it fits:** The array is guaranteed bitonic, so there is exactly one peak. We compare `arr[mid]` with `arr[mid + 1]` to determine which side the peak is on.
**The Twist:** The strict monotonicity guarantees exactly one peak, so the standard find-peak template applies directly without edge cases.
**Code Skeleton:**
```python
def peak_index_in_mountain_array(arr: list[int]) -> int:
    left, right = 0, len(arr) - 1
    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] < arr[mid + 1]:
            left = mid + 1
        else:
            right = mid
    return left
```

### 14. LeetCode 240. Search a 2D Matrix II
**Archetype:** 4.6 2D Matrix Search
**Type:** Core Drill
**Statement:** Search for target in a matrix where each row and each column is sorted in ascending order.
**Why it fits:** Starting from the top-right corner, we can eliminate an entire row or column with each comparison because of the 2D sorted property.
**The Twist:** Cannot flatten into 1D because rows are not guaranteed to be greater than previous rows; must use 2D elimination.
**Code Skeleton:**
```python
def search_matrix_ii(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    row, col = 0, len(matrix[0]) - 1
    while row < len(matrix) and col >= 0:
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] > target:
            col -= 1  # Eliminate current column
        else:
            row += 1  # Eliminate current row
    return False
```

### 15. LeetCode 658. Find K Closest Elements
**Archetype:** 4.3 Boundary Detection
**Type:** Core Drill
**Statement:** Find the k closest elements to x in a sorted array.
**Why it fits:** Instead of finding a single element, we binary search for the left boundary of the k-length window. We compare which side is farther from x.
**The Twist:** The comparison is `x - arr[mid] > arr[mid + k] - x` to decide whether to move left or right boundary.
**Code Skeleton:**
```python
def find_closest_elements(arr: list[int], k: int, x: int) -> list[int]:
    left, right = 0, len(arr) - k
    while left < right:
        mid = left + (right - left) // 2
        # Compare distance from x to arr[mid] vs arr[mid+k]
        if x - arr[mid] > arr[mid + k] - x:
            left = mid + 1
        else:
            right = mid
    return arr[left:left + k]
```
