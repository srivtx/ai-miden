# Pattern 02: Two Pointers -- Drills Part 2

> **Focus:** Warm-ups and Core Drills
> **Goal:** Solidify recognition of Two Pointers archetypes with progressive difficulty.

---

## Warm-ups

### 1. 167. Two Sum II - Input Array Is Sorted
**Archetype:** 2.1 Converging Pointers
**Type:** Warm-Up
**Statement:** Given a sorted array and target, return 1-indexed indices of two numbers adding to target.
**Why it fits:** The sorted order lets us use converging pointers. If the sum is too small, we need a larger number so we move left up. If too large, we move right down.
**The Twist:** None--this is the canonical converging-pointer problem. The 1-indexed return is a minor LeetCode convention.
**Code Skeleton:**
```python
def two_sum_sorted(numbers, target):
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]
        elif s < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]
```

### 2. 26. Remove Duplicates from Sorted Array
**Archetype:** 2.2 Same-Direction Pointers
**Type:** Warm-Up
**Statement:** Remove duplicates in-place from a sorted array and return the new length.
**Why it fits:** A writer pointer tracks where the next unique element should go, while a reader scans ahead. Everything before writer is the "good" portion.
**The Twist:** None--this is the canonical reader-writer pattern. The array is sorted, so duplicates are contiguous and easy to skip.
**Code Skeleton:**
```python
def remove_duplicates(nums):
    if not nums:
        return 0
    writer = 1
    for reader in range(1, len(nums)):
        if nums[reader] != nums[reader - 1]:
            nums[writer] = nums[reader]
            writer += 1
    return writer
```

### 3. 125. Valid Palindrome
**Archetype:** 2.4 Palindrome Check
**Type:** Warm-Up
**Statement:** Given a string, determine if it is a palindrome considering only alphanumeric characters and ignoring cases.
**Why it fits:** Palindromes read the same forwards and backwards. Two pointers from opposite ends compare valid characters, skipping non-alphanumeric symbols.
**The Twist:** None--this is the canonical palindrome check. The pointer movement includes a filtering step to ignore punctuation and whitespace.
**Code Skeleton:**
```python
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

### 4. 11. Container With Most Water
**Archetype:** 2.5 Container/Area
**Type:** Warm-Up
**Statement:** Given n non-negative integers representing vertical lines, find two lines that form a container holding the most water.
**Why it fits:** The area is width * min(height[left], height[right]). Moving the taller pointer inward cannot increase area, so we always move the shorter pointer.
**The Twist:** None--this is the canonical area problem. The greedy proof relies on the fact that width only decreases, so we must try to increase height.
**Code Skeleton:**
```python
def max_area(height):
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        width = right - left
        if height[left] < height[right]:
            max_water = max(max_water, height[left] * width)
            left += 1
        else:
            max_water = max(max_water, height[right] * width)
            right -= 1
    return max_water
```

### 5. 88. Merge Sorted Array
**Archetype:** 2.6 Merge Sorted
**Type:** Warm-Up
**Statement:** Merge two sorted arrays into one sorted array. The first array has enough buffer at the end.
**Why it fits:** Both arrays are sorted. We merge from the back to avoid overwriting unprocessed elements in nums1, using three pointers.
**The Twist:** None--this is the canonical merge problem. Working backwards eliminates the need for extra space because the trailing zeros are unused buffer.
**Code Skeleton:**
```python
def merge(nums1, m, nums2, n):
    i, j, k = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i -= 1
        else:
            nums1[k] = nums2[j]
            j -= 1
        k -= 1
```

## Core Drills

### 6. 15. 3Sum
**Archetype:** 2.1 Converging Pointers
**Type:** Core Drill
**Statement:** Find all unique triplets in the array that sum to zero.
**Why it fits:** We sort the array, fix one element, and use converging pointers on the remainder to find pairs that sum to the negation of the fixed element.
**The Twist:** Duplicates in the input produce duplicate triplets. We must skip equal neighbors after fixing an element and after finding a valid pair to ensure uniqueness.
**Code Skeleton:**
```python
def three_sum(nums):
    nums.sort()
    result = []
    n = len(nums)
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s < 0:
                left += 1
            elif s > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
    return result
```

### 7. 16. 3Sum Closest
**Archetype:** 2.1 Converging Pointers
**Type:** Core Drill
**Statement:** Find the sum of three integers in the array such that the sum is closest to target.
**Why it fits:** Same structure as 3Sum: sort, fix one, two-pointer the rest. Instead of checking for equality, we track the smallest absolute difference from target.
**The Twist:** We do not break early when finding an exact match because there could be an even closer sum? Actually if diff is zero we can break. But generally we update a running best and continue exploring.
**Code Skeleton:**
```python
def three_sum_closest(nums, target):
    nums.sort()
    n = len(nums)
    closest = float('inf')
    for i in range(n - 2):
        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if abs(s - target) < abs(closest - target):
                closest = s
            if s < target:
                left += 1
            elif s > target:
                right -= 1
            else:
                return s
    return closest
```

### 8. 881. Boats to Save People
**Archetype:** 2.1 Converging Pointers
**Type:** Core Drill
**Statement:** Given people weights and a boat limit, return the minimum number of boats to carry everyone. Each boat carries at most two people.
**Why it fits:** Sorting lets us pair the lightest available person with the heaviest. If their combined weight exceeds the limit, the heaviest must go alone.
**The Twist:** The greedy pairing is proven optimal by exchange argument. The converging pointers naturally implement the greedy strategy without explicit scheduling logic.
**Code Skeleton:**
```python
def num_rescue_boats(people, limit):
    people.sort()
    left, right = 0, len(people) - 1
    boats = 0
    while left <= right:
        if people[left] + people[right] <= limit:
            left += 1
        right -= 1
        boats += 1
    return boats
```

### 9. 27. Remove Element
**Archetype:** 2.2 Same-Direction Pointers
**Type:** Core Drill
**Statement:** Given an array and a value, remove all instances of that value in-place and return the new length.
**Why it fits:** The writer pointer only advances when the reader sees a value that should be kept. This compresses the array by overwriting unwanted elements.
**The Twist:** Unlike Remove Duplicates, we are filtering by a fixed target value rather than comparing adjacent elements. The rest of the array after the writer is irrelevant.
**Code Skeleton:**
```python
def remove_element(nums, val):
    writer = 0
    for reader in range(len(nums)):
        if nums[reader] != val:
            nums[writer] = nums[reader]
            writer += 1
    return writer
```

### 10. 283. Move Zeroes
**Archetype:** 2.2 Same-Direction Pointers
**Type:** Core Drill
**Statement:** Given an array, move all 0s to the end while maintaining the relative order of non-zero elements.
**Why it fits:** We use a writer to place non-zero elements at the front, then fill the remainder with zeros. This preserves the original order of non-zero elements.
**The Twist:** We cannot simply swap zeros to the end because that would scramble order. The two-pass approach (write non-zeros, then fill zeros) guarantees stability.
**Code Skeleton:**
```python
def move_zeroes(nums):
    writer = 0
    for reader in range(len(nums)):
        if nums[reader] != 0:
            nums[writer] = nums[reader]
            writer += 1
    for i in range(writer, len(nums)):
        nums[i] = 0
```

### 11. 80. Remove Duplicates from Sorted Array II
**Archetype:** 2.2 Same-Direction Pointers
**Type:** Core Drill
**Statement:** Remove duplicates in-place such that each element appears at most twice, and return the new length.
**Why it fits:** The writer tracks the insertion position. We allow an element if it is not equal to the element two positions before the writer, ensuring at most two copies.
**The Twist:** The condition generalizes the classic "remove all duplicates" problem. We compare nums[reader] against nums[writer - 2] rather than nums[reader - 1].
**Code Skeleton:**
```python
def remove_duplicates_ii(nums):
    if len(nums) <= 2:
        return len(nums)
    writer = 2
    for reader in range(2, len(nums)):
        if nums[reader] != nums[writer - 2]:
            nums[writer] = nums[reader]
            writer += 1
    return writer
```

### 12. 75. Sort Colors
**Archetype:** 2.3 Partitioning
**Type:** Core Drill
**Statement:** Given an array with objects colored red, white, or blue, sort them in-place by color (0, 1, 2).
**Why it fits:** We partition the array into three sections: zeros on the left, ones in the middle, and twos on the right. Three pointers track the boundaries.
**The Twist:** This is the Dutch National Flag problem. A single mid pointer explores unknown territory while low and high delimit the known good regions.
**Code Skeleton:**
```python
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
```

### 13. 42. Trapping Rain Water
**Archetype:** 2.5 Container/Area
**Type:** Core Drill
**Statement:** Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.
**Why it fits:** Water trapped at any index is determined by the minimum of the highest bar to its left and right, minus its own height. Two pointers track max heights from both ends.
**The Twist:** We do not precompute prefix/suffix arrays. Instead, we move the pointer at the smaller max height because the water level is bounded by that smaller max.
**Code Skeleton:**
```python
def trap(height):
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1
    return water
```

### 14. 680. Valid Palindrome II
**Archetype:** 2.4 Palindrome Check
**Type:** Core Drill
**Statement:** Given a string, determine if it can be a palindrome after deleting at most one character.
**Why it fits:** We use two pointers from the ends. When a mismatch is found, we have two choices: skip left or skip right. We test both branches.
**The Twist:** The "at most one deletion" adds a recursive/branching decision. We do not backtrack with a stack; instead we greedily check the two possible substrings.
**Code Skeleton:**
```python
def valid_palindrome(s):
    def check(left, right):
        while left < right:
            if s[left] != s[right]:
                return False
            left += 1
            right -= 1
        return True

    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return check(left + 1, right) or check(left, right - 1)
        left += 1
        right -= 1
    return True
```

### 15. 209. Minimum Size Subarray Sum
**Archetype:** 2.7 Sliding Window Variant
**Type:** Core Drill
**Statement:** Given an array of positive integers and target, find the minimal length of a contiguous subarray whose sum is greater than or equal to target.
**Why it fits:** Because all numbers are positive, when the window sum exceeds target, shrinking from the left only decreases the sum. This monotonicity lets us slide a variable-size window.
**The Twist:** The window is not fixed-size. We expand until the sum is sufficient, then contract from the left to find the minimum valid window, tracking the smallest length seen.
**Code Skeleton:**
```python
def min_sub_array_len(target, nums):
    left = 0
    current_sum = 0
    min_len = float('inf')
    for right in range(len(nums)):
        current_sum += nums[right]
        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= nums[left]
            left += 1
    return 0 if min_len == float('inf') else min_len
```
