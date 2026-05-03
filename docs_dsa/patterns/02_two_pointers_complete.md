# Pattern 02: Two Pointers — Complete Archetype Map

> **Pattern Recognition:** When you see "sorted array", "pair with sum", "palindrome", "merge", "partition", "container/area" — think two pointers.
>
> **Fundamental Trade:** Two pointers replaces the O(n^2) brute force with O(n) by leveraging order. If the array is NOT sorted, either sort first (O(n log n)) or use a hash map (O(n) time, O(n) space).

---

## Archetype 2.1: Converging Pointers (Opposite Ends)

### Recognition Signal (10 seconds)
Words: **"sorted array", "pair with sum", "find two numbers", "target sum", "complement in sorted"**

The question is always: **"In a sorted array, find a pair that satisfies some condition."**

### Core Structure
```
left = 0, right = len(arr) - 1
while left < right:
    if condition_met(arr[left], arr[right]):
        return result
    elif too_small:
        left += 1
    else:  # too_big
        right -= 1
```

### The Invariant
Because the array is sorted:
- Moving left up increases the sum
- Moving right down decreases the sum
- We eliminate one element at a time, never revisiting

### Canonical Problem: Two Sum II — Sorted (LeetCode 167)
**Statement:** Array is sorted. Find two numbers that add up to target.

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
```

### Variation Family

**V1: 3Sum (LeetCode 15)**
- **Twist:** Find all unique triplets that sum to zero
- **Change:** Sort array. For each i, use two pointers on arr[i+1:] to find pairs that sum to -arr[i]
- **Key insight:** Fix one, two-sum the rest. Skip duplicates.

**V2: 3Sum Closest (LeetCode 16)**
- **Twist:** Find triplet sum closest to target
- **Change:** Track minimum difference. Update best sum when closer.
- **Key insight:** Same structure as 3Sum, but optimize for proximity instead of exact match.

**V3: 4Sum (LeetCode 18)**
- **Twist:** Find all unique quadruplets that sum to target
- **Change:** Fix two with nested loops, two-sum the rest with pointers.
- **Key insight:** N-sum generalizes: sort + (N-2) nested loops + two pointers.

**V4: Boats to Save People (LeetCode 881)**
- **Twist:** Each boat carries at most limit. Minimize number of boats.
- **Change:** Sort. Heaviest person must go. If lightest can join, pair them.
- **Key insight:** Greedy + two pointers. Always try to pair heaviest with lightest.

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

**V5: Two Sum Less Than or Equal to K**
- **Twist:** Find max pair sum <= K
- **Change:** Sort. Start from widest. If sum <= K, record it and move left up (try larger). Else move right down.
- **Key insight:** "Maximize under constraint" needs careful pointer movement tracking.

**V6: Count Pairs with Sum Less Than Target**
- **Twist:** Count all pairs (i,j) where sum < target
- **Change:** Sort. For each left, move right inward until sum < target. All pairs between left and right are valid.

```python
def count_pairs(nums, target):
    nums.sort()
    left, right = 0, len(nums) - 1
    count = 0
    while left < right:
        if nums[left] + nums[right] < target:
            count += right - left
            left += 1
        else:
            right -= 1
    return count
```

**Near Miss: Two Sum (unsorted)**
- **Looks like:** Pair with target sum
- **But:** Array is NOT sorted. Two pointers require sorting (loses original indices). Hash map is better.
- **Lesson:** Two pointers NEED sorted data. If indices matter, use hash map.

---

## Archetype 2.2: Same-Direction Pointers (Fast & Slow / Reader & Writer)

### Recognition Signal (10 seconds)
Words: **"remove duplicates", "move zeros", "in-place", "overwrite", "compress", "partition"**

The question is always: **"Iterate through array, but only keep some elements. Do it in-place."**

### Core Structure
```
writer = 0
for reader in range(n):
    if should_keep(arr[reader]):
        arr[writer] = arr[reader]
        writer += 1
return writer  # new length
```

### The Invariant
The `writer` pointer always points to where the next kept element should go. Everything before `writer` is the "good" part of the array.

### Canonical Problem: Remove Duplicates from Sorted Array (LeetCode 26)
**Statement:** Remove duplicates in-place, return new length.

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

### Variation Family

**V1: Remove Element (LeetCode 27)**
- **Twist:** Remove all instances of val in-place
- **Change:** Keep elements that != val

```python
def remove_element(nums, val):
    writer = 0
    for reader in range(len(nums)):
        if nums[reader] != val:
            nums[writer] = nums[reader]
            writer += 1
    return writer
```

**V2: Move Zeroes (LeetCode 283)**
- **Twist:** Move all zeros to end, maintain relative order of non-zero elements
- **Change:** Same as remove element, but fill rest with zeros

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

**V3: Sort Colors / Dutch National Flag (LeetCode 75)**
- **Twist:** Array of 0s, 1s, 2s. Sort in-place in one pass.
- **Change:** THREE pointers. Low boundary for 0s, high boundary for 2s, current scanner.

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

**V4: Remove Duplicates II (LeetCode 80)**
- **Twist:** Allow at most 2 duplicates
- **Change:** Check if current element is same as element two positions behind writer

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

**V5: Replace Elements with Greatest Element on Right Side (LeetCode 1299)**
- **Twist:** Replace each element with max element to its right
- **Change:** Traverse from right to left. Track max so far.

```python
def replace_elements(arr):
    max_right = -1
    for i in range(len(arr) - 1, -1, -1):
        arr[i], max_right = max_right, max(max_right, arr[i])
    return arr
```

**Near Miss: Merge Sorted Array (LeetCode 88)**
- **Looks like:** In-place array manipulation
- **But:** Two arrays, merge into first. Go from back to front to avoid overwriting.
- **Lesson:** Same-direction pointers can go forward OR backward depending on what needs protection.

---

## Archetype 2.3: Partitioning (Rearrangement)

### Recognition Signal (10 seconds)
Words: **"partition", "rearrange", "odds before evens", "negatives before positives", "stable partition"**

The question is always: **"Rearrange array so that elements satisfying some condition come first/last."**

### Core Structure
```
Same as Dutch National Flag or quicksort partition:
- Boundary pointer tracks where the partition should be
- Scanner finds elements that belong on the other side
- Swap them
```

### Canonical Problem: Partition List (LeetCode 86 - Linked List, but same idea)
For arrays: **Odd Even Linked List / Array Partition**

**Array version:** Move all negative numbers before positive numbers.

```python
def partition_negatives(nums):
    writer = 0
    for reader in range(len(nums)):
        if nums[reader] < 0:
            nums[writer], nums[reader] = nums[reader], nums[writer]
            writer += 1
    return nums
```

### Variation Family

**V1: Sort Array by Parity (LeetCode 905)**
- **Twist:** Even integers followed by odd integers
- **Change:** Two pointers from ends. Swap when left is odd and right is even.

```python
def sort_array_by_parity(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        while left < right and nums[left] % 2 == 0:
            left += 1
        while left < right and nums[right] % 2 == 1:
            right -= 1
        nums[left], nums[right] = nums[right], nums[left]
        left += 1
        right -= 1
    return nums
```

**V2: Sort Array by Parity II (LeetCode 922)**
- **Twist:** Even indices have even numbers, odd indices have odd numbers
- **Change:** Two pointers: even_idx finds wrong evens, odd_idx finds wrong odds. Swap.

**V3: Interleaving Positive and Negative (LeetCode 2149)**
- **Twist:** Rearrange so positives and negatives alternate, starting with positive
- **Change:** Separate into positive and negative arrays, then interleave.
- **Key insight:** Sometimes two pointers on separate arrays, then merge.

**Near Miss: Quicksort Partition**
- **Looks like:** Partitioning
- **But:** In-place sorting algorithm, not just rearrangement
- **Lesson:** The Lomuto/Hoare partition schemes are the foundation of all partitioning problems.

---

## Archetype 2.4: Palindrome Checking

### Recognition Signal (10 seconds)
Words: **"palindrome", "reverse", "same forwards and backwards", "valid palindrome"**

The question is always: **"Does this string read the same forwards and backwards?"**

### Core Structure
```
left, right = 0, len(s) - 1
while left < right:
    if s[left] != s[right]:
        return False
    left += 1
    right -= 1
return True
```

### Canonical Problem: Valid Palindrome (LeetCode 125)
**Statement:** Check if string is palindrome, considering only alphanumeric and ignoring cases.

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

### Variation Family

**V1: Valid Palindrome II (LeetCode 680)**
- **Twist:** Can delete at most one character
- **Change:** When mismatch found, try skipping left OR skipping right, check if either becomes palindrome.

```python
def valid_palindrome_ii(s):
    def check_palindrome(left, right):
        while left < right:
            if s[left] != s[right]:
                return False
            left += 1
            right -= 1
        return True
    
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return check_palindrome(left + 1, right) or check_palindrome(left, right - 1)
        left += 1
        right -= 1
    return True
```

**V2: Longest Palindromic Substring (LeetCode 5)**
- **Twist:** Find longest palindromic substring
- **Change:** Expand around center. For each position, expand as long as palindrome.
- **Key insight:** Palindromes have centers. Odd length has one center, even has two.

```python
def longest_palindrome(s):
    def expand(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left + 1:right]
    
    result = ""
    for i in range(len(s)):
        # Odd length
        odd = expand(i, i)
        # Even length
        even = expand(i, i + 1)
        if len(odd) > len(result):
            result = odd
        if len(even) > len(result):
            result = even
    return result
```

**V3: Palindromic Substrings (LeetCode 647)**
- **Twist:** Count all palindromic substrings
- **Change:** Same expand-around-center, but count instead of track max.

**V4: Longest Palindrome (LeetCode 409)**
- **Twist:** Build longest palindrome from given characters
- **Change:** Count frequencies. For each char, add largest even count. Add one if any odd count exists (for center).
- **Pattern blend:** Two pointers + frequency counting.

**Near Miss: Reverse String (LeetCode 344)**
- **Looks like:** Palindrome-related
- **But:** Just reverse in-place. Two pointers swap until meet.
- **Lesson:** Palindrome checking is "compare", reverse is "swap".

---

## Archetype 2.5: Container / Area Problems

### Recognition Signal (10 seconds)
Words: **"container", "most water", "trap rain", "area", "height", "width"**

The question is always: **"Find two lines that form the container with maximum area/volume."**

### Core Structure
```
left, right = 0, n-1
max_area = 0
while left < right:
    area = min(height[left], height[right]) * (right - left)
    max_area = max(max_area, area)
    # Move the pointer at the shorter line
    if height[left] < height[right]:
        left += 1
    else:
        right -= 1
```

### The Invariant
Why move the shorter line? Because:
- Area = min(h[left], h[right]) * width
- If you move the taller line, width decreases AND min height stays the same or decreases
- If you move the shorter line, you MIGHT find a taller line that compensates for lost width

### Canonical Problem: Container With Most Water (LeetCode 11)
**Statement:** Find two lines that together with x-axis form a container that holds most water.

```python
def max_area(height):
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        width = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, width * h)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water
```

### Variation Family

**V1: Trapping Rain Water (LeetCode 42)**
- **Twist:** How much water can be trapped after raining?
- **Change:** Water at position i = min(max_left, max_right) - height[i]. Two pointers track max from each side.

```python
def trap(height):
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water
```

**V2: Max Area of Island (LeetCode 695)**
- **Twist:** Find max area of connected 1s in grid
- **Change:** DFS/BFS, not two pointers. But the "area" concept is similar.
- **Pattern blend:** Graph traversal for area calculation.

**V3: Largest Rectangle in Histogram (LeetCode 84)**
- **Twist:** Find largest rectangle in histogram
- **Change:** Stack-based, not two pointers. But "area bounded by heights" is conceptually related.
- **Pattern blend:** This is actually a stack problem (monotonic stack).

**Near Miss: Maximal Square (LeetCode 221)**
- **Looks like:** Area calculation
- **But:** Dynamic programming. dp[i][j] = largest square ending at (i,j).
- **Lesson:** Area problems can be two pointers (1D) OR DP (2D).

---

## Archetype 2.6: Merge Sorted Structures

### Recognition Signal (10 seconds)
Words: **"merge", "sorted", "combine", "union", "intersection", "two sorted arrays/lists"**

The question is always: **"Combine two sorted sequences into one sorted sequence."**

### Core Structure
```
i, j = 0, 0
result = []
while i < len(a) and j < len(b):
    if a[i] <= b[j]:
        result.append(a[i])
        i += 1
    else:
        result.append(b[j])
        j += 1
# Add remaining elements
```

### Canonical Problem: Merge Sorted Array (LeetCode 88)
**Statement:** Merge two sorted arrays into first array (which has enough space).

```python
def merge(nums1, m, nums2, n):
    # Start from back to avoid overwriting
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

### Variation Family

**V1: Intersection of Two Arrays II (LeetCode 350)**
- **Twist:** Find intersection with duplicates (if 2 appears twice in both, output two 2s)
- **Change:** If sorted, two pointers. If not, hash map.

```python
def intersect(nums1, nums2):
    nums1.sort()
    nums2.sort()
    i, j = 0, 0
    result = []
    while i < len(nums1) and j < len(nums2):
        if nums1[i] < nums2[j]:
            i += 1
        elif nums1[i] > nums2[j]:
            j += 1
        else:
            result.append(nums1[i])
            i += 1
            j += 1
    return result
```

**V2: Intersection of Three Sorted Arrays (LeetCode 1213)**
- **Twist:** Find common elements in three sorted arrays
- **Change:** Three pointers. Advance the pointer pointing to smallest value.

**V3: Union of Two Sorted Arrays**
- **Twist:** All unique elements from both arrays
- **Change:** Similar to merge, but skip duplicates.

**V4: Median of Two Sorted Arrays (LeetCode 4)**
- **Twist:** Find median of two sorted arrays in O(log(m+n))
- **Change:** Binary search on partition point, not two pointers.
- **Pattern blend:** This is actually a binary search problem disguised as merge.

**Near Miss: Merge k Sorted Lists (LeetCode 23)**
- **Looks like:** Merge sorted
- **But:** K lists, not 2. Use heap for O(n log k) time.
- **Lesson:** Merge 2 = two pointers. Merge K = heap.

---

## Archetype 2.7: Sliding Window Variant (Fixed/Variable Size with Two Pointers)

### Recognition Signal (10 seconds)
Words: **"subarray", "substring", "consecutive", "window", "at most K", "longest/shortest contiguous"**

The question is always: **"Find a contiguous subarray/substring satisfying some condition."**

**Note:** This is closely related to Pattern 05 (Sliding Window). The difference: two pointers emphasizes the two-boundary nature, while sliding window emphasizes the window contents.

### Core Structure
```
left = 0
for right in range(n):
    # Add nums[right] to window
    while window_invalid():
        # Remove nums[left] from window
        left += 1
    # Update answer
```

### Canonical Problem: Minimum Size Subarray Sum (LeetCode 209)
**Statement:** Find minimum length subarray with sum >= target.

```python
def min_sub_array_len(target, nums):
    left, total = 0, 0
    min_len = float('inf')
    for right in range(len(nums)):
        total += nums[right]
        while total >= target:
            min_len = min(min_len, right - left + 1)
            total -= nums[left]
            left += 1
    return min_len if min_len != float('inf') else 0
```

### Variation Family

**V1: Longest Substring Without Repeating Characters (LeetCode 3)**
- **Twist:** Longest substring with all unique characters
- **Change:** Hash set tracks window contents. When duplicate found, shrink from left.

```python
def length_of_longest_substring(s):
    char_set = set()
    left = 0
    max_len = 0
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)
    return max_len
```

**V2: Fruit Into Baskets (LeetCode 904)**
- **Twist:** Longest subarray with at most 2 distinct elements
- **Change:** Hash map counts frequency in window. Shrink when more than 2 distinct.

**V3: Max Consecutive Ones III (LeetCode 1004)**
- **Twist:** Longest subarray of 1s if you can flip at most K 0s
- **Change:** Count zeros in window. Shrink when zeros > K.

```python
def longest_ones(nums, k):
    left = 0
    max_len = 0
    zeros = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

**V4: Subarrays with K Different Integers (LeetCode 992)**
- **Twist:** Count subarrays with exactly K distinct integers
- **Change:** at_most(K) - at_most(K-1). "Exactly K" = "at most K" - "at most K-1"
- **Key insight:** This is a common trick. Exactly = AtMost(K) - AtMost(K-1)

**Near Miss: Subarray Sum Equals K (LeetCode 560)**
- **Looks like:** Subarray problem
- **But:** Uses prefix sums + hash map, not two pointers. Negative numbers break the two-pointer approach.
- **Lesson:** Two pointers only work when all numbers are positive (or the condition is monotonic).

---

## Pattern 02 Mastery Checklist

Before moving to Pattern 03, confirm you can:

- [ ] **Converging:** See "sorted pair sum" and write two-pointer solution in 30 seconds
- [ ] **Same-Direction:** See "remove duplicates in-place" and write reader-writer in 30 seconds
- [ ] **Partitioning:** See "sort by parity" and write two-pointer swap in 45 seconds
- [ ] **Palindrome:** See "valid palindrome" and write converging check in 30 seconds
- [ ] **Container:** Explain WHY we move the shorter line in container problem
- [ ] **Merge:** See "merge sorted" and know whether to go front-to-back or back-to-front
- [ ] **Window:** See "longest substring without repeats" and write sliding window in 45 seconds
- [ ] **Distinguish:** Know when to use two pointers vs hash map vs sliding window vs prefix sums

---

*Next: Pattern 03 — Stack*
