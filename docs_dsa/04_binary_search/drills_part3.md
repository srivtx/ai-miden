# Pattern 04: Binary Search — Drills Part 3

> 5 Near Misses + 5 Pattern Blends + 5 Interview Simulations

---

## Near Misses

### 16. LeetCode 81. Search in Rotated Sorted Array II
**Archetype:** 4.2 Search Space Reduction (Rotated)
**Type:** Near Miss
**Statement:** Find target in a rotated sorted array that may contain duplicates.
**Why it fits:** Same rotated array logic as LeetCode 33, but duplicates make it impossible to determine which half is sorted when `nums[left] == nums[mid]`.
**The Twist:** When `nums[left] == nums[mid]`, we cannot tell which half is sorted, so we increment `left` by 1 to reduce ambiguity, degrading worst-case to O(n).
**Code Skeleton:**
```python
def search_rotated_ii(nums: list[int], target: int) -> bool:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return True
        if nums[left] == nums[mid]:
            left += 1  # Cannot determine sorted half; shrink
            continue
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
    return False
```

### 17. LeetCode 154. Find Minimum in Rotated Sorted Array II
**Archetype:** 4.2 Search Space Reduction (Rotated)
**Type:** Near Miss
**Statement:** Find the minimum element in a rotated sorted array that may contain duplicates.
**Why it fits:** Same as LeetCode 153, but duplicates blur the boundary between sorted and unsorted halves.
**The Twist:** When `nums[mid] == nums[right]`, we cannot tell if mid is the minimum or if it lies to the left, so we decrement `right` by 1.
**Code Skeleton:**
```python
def find_min_ii(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        elif nums[mid] < nums[right]:
            right = mid
        else:
            right -= 1  # Cannot determine; shrink conservatively
    return nums[left]
```

### 18. LeetCode 540. Single Element in a Sorted Array
**Archetype:** 4.4 Condition-Based Search
**Type:** Near Miss
**Statement:** Every element appears exactly twice except one. Find the single element.
**Why it fits:** Before the single element, pairs occupy (even, odd) indices. After the single element, pairs occupy (odd, even). Binary search finds where this pattern changes.
**The Twist:** We force `mid` to be even before comparing with its neighbor, so we can check if the pair is in the expected position.
**Code Skeleton:**
```python
def single_non_duplicate(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if mid % 2 == 1:
            mid -= 1  # Ensure mid is even
        if nums[mid] == nums[mid + 1]:
            left = mid + 2  # Single element is to the right
        else:
            right = mid  # Single element is at or before mid
    return nums[left]
```

### 19. LeetCode 378. Kth Smallest Element in a Sorted Matrix
**Archetype:** 4.6 2D Matrix Search
**Type:** Near Miss
**Statement:** Find the kth smallest element in a matrix where each row and column is sorted.
**Why it fits:** Instead of searching by index, we binary search on the value space. We count how many elements are <= mid to determine if we need to go higher or lower.
**The Twist:** The counting function walks from bottom-left or top-right in O(n) time, making the overall complexity O(n log(max-min)).
**Code Skeleton:**
```python
def kth_smallest(matrix: list[list[int]], k: int) -> int:
    n = len(matrix)
    left, right = matrix[0][0], matrix[-1][-1]

    def count_less_equal(x: int) -> int:
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

### 20. LeetCode 1283. Find the Smallest Divisor Given a Threshold
**Archetype:** 4.5 Answer Space Search
**Type:** Near Miss
**Statement:** Find the smallest divisor such that the sum of ceiling divisions of all numbers by the divisor is <= threshold.
**Why it fits:** Larger divisors produce smaller sums, so feasibility is monotonic. We binary search on divisor space [1, max(nums)].
**The Twist:** The condition involves ceiling division for every element, and the lower bound of the search space is 1, not an array element.
**Code Skeleton:**
```python
def smallest_divisor(nums: list[int], threshold: int) -> int:
    def condition(divisor: int) -> bool:
        total = 0
        for num in nums:
            total += (num + divisor - 1) // divisor  # Ceiling division
        return total <= threshold

    left, right = 1, max(nums)
    while left < right:
        mid = left + (right - left) // 2
        if condition(mid):
            right = mid
        else:
            left = mid + 1
    return left
```

---

## Pattern Blends

### 21. LeetCode 4. Median of Two Sorted Arrays
**Archetype:** 4.7 Median of Two Sorted Arrays
**Type:** Pattern Blend
**Statement:** Find the median of two sorted arrays in O(log(min(m,n))) time.
**Why it fits:** We binary search on the partition point of the smaller array. The goal is to balance the left and right halves so that every element in the left half is <= every element in the right half.
**The Twist:** Requires handling edge cases where the partition is at the boundary (0 or n) using positive/negative infinity.
**Code Skeleton:**
```python
def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
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

### 22. LeetCode 1095. Find in Mountain Array
**Archetype:** 4.4 Condition-Based Search
**Type:** Pattern Blend
**Statement:** Find the index of target in a mountain array with limited API calls.
**Why it fits:** First find the peak using condition-based binary search, then perform two separate binary searches on the increasing and decreasing slopes.
**The Twist:** The array access is limited by an API, and the two post-peak searches require opposite comparison logic (ascending vs descending).
**Code Skeleton:**
```python
def find_in_mountain_array(target: int, mountain_arr: 'MountainArray') -> int:
    # Step 1: Find peak
    left, right = 0, mountain_arr.length() - 1
    while left < right:
        mid = left + (right - left) // 2
        if mountain_arr.get(mid) < mountain_arr.get(mid + 1):
            left = mid + 1
        else:
            right = mid
    peak = left

    # Step 2: Search left (ascending)
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

    # Step 3: Search right (descending)
    left, right = peak, mountain_arr.length() - 1
    while left <= right:
        mid = left + (right - left) // 2
        val = mountain_arr.get(mid)
        if val == target:
            return mid
        elif val < target:
            right = mid - 1  # Descending: smaller values are to the right
        else:
            left = mid + 1
    return -1
```

### 23. LeetCode 410. Split Array Largest Sum
**Archetype:** 4.5 Answer Space Search
**Type:** Pattern Blend
**Statement:** Split the array into m subarrays to minimize the largest subarray sum.
**Why it fits:** Binary search on the answer (largest sum). The condition checks if we can split into m or fewer subarrays where each sum <= mid.
**The Twist:** The condition uses a greedy approach to count subarrays, blending binary search with greedy algorithm design.
**Code Skeleton:**
```python
def split_array(nums: list[int], m: int) -> int:
    def can_split(max_sum: int) -> bool:
        count = 1
        current = 0
        for num in nums:
            if current + num > max_sum:
                count += 1
                current = 0
            current += num
        return count <= m

    left, right = max(nums), sum(nums)
    while left < right:
        mid = left + (right - left) // 2
        if can_split(mid):
            right = mid
        else:
            left = mid + 1
    return left
```

### 24. LeetCode 315. Count of Smaller Numbers After Self
**Archetype:** 4.3 Boundary Detection
**Type:** Pattern Blend
**Statement:** For each element, count how many smaller elements are to its right.
**Why it fits:** Process elements from right to left, maintaining a sorted list. For each element, binary search to find its insertion position (how many elements are smaller).
**The Twist:** Requires a dynamic sorted structure. In practice, merge sort or a Fenwick tree is more efficient than list insertion.
**Code Skeleton:**
```python
def count_smaller(nums: list[int]) -> list[int]:
    # Simplified: using bisect on a sorted list (O(n^2) worst case; use BIT for O(n log n))
    import bisect
    sorted_list = []
    result = []
    for num in reversed(nums):
        idx = bisect.bisect_left(sorted_list, num)
        result.append(idx)
        bisect.insort(sorted_list, num)
    return result[::-1]
```

### 25. LeetCode 300. Longest Increasing Subsequence
**Archetype:** 4.4 Condition-Based Search
**Type:** Pattern Blend
**Statement:** Find the length of the longest strictly increasing subsequence.
**Why it fits:** Uses patience sorting with a `tails` array. For each number, binary search finds the first tail >= num to replace, maintaining the smallest possible tail for each length.
**The Twist:** This is not a direct binary search on an input array; it is binary search on a self-maintained monotonic array (`tails`).
**Code Skeleton:**
```python
def length_of_lis(nums: list[int]) -> int:
    import bisect
    tails = []
    for num in nums:
        idx = bisect.bisect_left(tails, num)
        if idx == len(tails):
            tails.append(num)
        else:
            tails[idx] = num
    return len(tails)
```

---

## Interview Simulations

### 26. LeetCode 1482. Minimum Number of Days to Make m Bouquets
**Archetype:** 4.5 Answer Space Search
**Type:** Interview Sim
**Statement:** Given bloom days for each flower, find the minimum day to make m bouquets of k adjacent bloomed flowers.
**Why it fits:** As days increase, more flowers bloom (monotonic). Binary search on day space, with a greedy check to count how many bouquets can be made by day `d`.
**The Twist:** The condition function must track consecutive bloomed flowers to form bouquets; non-consecutive flowers break the streak.
**Code Skeleton:**
```python
def min_days(bloom_day: list[int], m: int, k: int) -> int:
    if m * k > len(bloom_day):
        return -1

    def can_make(day: int) -> bool:
        bouquets = 0
        flowers = 0
        for bloom in bloom_day:
            if bloom <= day:
                flowers += 1
                if flowers == k:
                    bouquets += 1
                    flowers = 0
            else:
                flowers = 0
        return bouquets >= m

    left, right = min(bloom_day), max(bloom_day)
    while left < right:
        mid = left + (right - left) // 2
        if can_make(mid):
            right = mid
        else:
            left = mid + 1
    return left
```

### 27. LeetCode 719. Find K-th Smallest Pair Distance
**Archetype:** 4.3 Boundary Detection
**Type:** Interview Sim
**Statement:** Given a sorted array, find the kth smallest distance among all pairs (i, j) where i < j.
**Why it fits:** Binary search on the distance value. For a given distance `d`, count how many pairs have distance <= d using a two-pointer approach.
**The Twist:** The counting function is O(n) with two pointers because the array is sorted, but we are binary searching on distance, not array indices.
**Code Skeleton:**
```python
def smallest_distance_pair(nums: list[int], k: int) -> int:
    nums.sort()

    def count_pairs(max_dist: int) -> int:
        count = 0
        left = 0
        for right in range(len(nums)):
            while nums[right] - nums[left] > max_dist:
                left += 1
            count += right - left
        return count

    left, right = 0, nums[-1] - nums[0]
    while left < right:
        mid = left + (right - left) // 2
        if count_pairs(mid) < k:
            left = mid + 1
        else:
            right = mid
    return left
```

### 28. LeetCode 778. Swim in Rising Water
**Archetype:** 4.5 Answer Space Search
**Type:** Interview Sim
**Statement:** In an n x n grid, find the minimum time to reach the bottom-right square from the top-left, where time is the maximum elevation encountered.
**Why it fits:** Binary search on elevation/time. For a given time `t`, check if a path exists where all cells on the path have elevation <= t using BFS or DFS.
**The Twist:** The condition function is a graph traversal (BFS/DFS), blending binary search with graph algorithms.
**Code Skeleton:**
```python
def swim_in_water(grid: list[list[int]]) -> int:
    n = len(grid)

    def can_swim(t: int) -> bool:
        if grid[0][0] > t:
            return False
        visited = [[False] * n for _ in range(n)]
        stack = [(0, 0)]
        visited[0][0] = True
        while stack:
            r, c = stack.pop()
            if r == n - 1 and c == n - 1:
                return True
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc] and grid[nr][nc] <= t:
                    visited[nr][nc] = True
                    stack.append((nr, nc))
        return False

    left, right = grid[0][0], n * n - 1
    while left < right:
        mid = left + (right - left) // 2
        if can_swim(mid):
            right = mid
        else:
            left = mid + 1
    return left
```

### 29. LeetCode 1231. Divide Chocolate
**Archetype:** 4.5 Answer Space Search
**Type:** Interview Sim
**Statement:** Maximize the minimum total sweetness of a piece when splitting the chocolate into k+1 chunks.
**Why it fits:** Binary search on sweetness. Check if we can make at least k+1 pieces where each piece has total sweetness >= mid. We want to maximize this minimum.
**The Twist:** The binary search returns the largest minimum sweetness that is achievable, which is a "maximize the minimum" pattern.
**Code Skeleton:**
```python
def maximize_sweetness(sweetness: list[int], k: int) -> int:
    def can_split(min_sweet: int) -> bool:
        pieces = 0
        current = 0
        for sweet in sweetness:
            current += sweet
            if current >= min_sweet:
                pieces += 1
                current = 0
        return pieces >= k + 1

    left, right = min(sweetness), sum(sweetness) // (k + 1)
    while left < right:
        mid = left + (right - left + 1) // 2  # Upper mid for max-min
        if can_split(mid):
            left = mid
        else:
            right = mid - 1
    return left
```

### 30. LeetCode 1060. Missing Element in Sorted Array
**Archetype:** 4.3 Boundary Detection
**Type:** Interview Sim
**Statement:** Find the kth missing number in a sorted array of unique elements.
**Why it fits:** At index `i`, the count of missing numbers before `arr[i]` is `arr[i] - arr[0] - i`. We binary search for the index where this count crosses k.
**The Twist:** The answer is not at an array index directly; it is computed by adding the remaining missing count to the array element at the found boundary.
**Code Skeleton:**
```python
def missing_element(nums: list[int], k: int) -> int:
    n = len(nums)

    def missing_count(idx: int) -> int:
        return nums[idx] - nums[0] - idx

    left, right = 0, n - 1
    while left < right:
        mid = left + (right - left) // 2
        if missing_count(mid) < k:
            left = mid + 1
        else:
            right = mid

    # If left is 0 and missing_count(0) >= k, answer is before array
    if missing_count(left) < k:
        return nums[left] + (k - missing_count(left))
    return nums[left - 1] + (k - missing_count(left - 1)) if left > 0 else nums[0] - k
```
