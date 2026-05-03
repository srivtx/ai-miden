# Pattern 02: Two Pointers -- Drills Part 3

> **Focus:** Near Misses + Pattern Blends + Interview Simulation
> **Goal:** Build pattern-switching judgment and simulate real interview ambiguity.

---

## Near Misses (Looks like Pattern 02, but isn't)

### 16. 1. Two Sum
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given an array of integers and a target, return indices of two numbers that add up to target.
**Why it fits:** The problem asks for a pair summing to a target, which strongly suggests converging pointers on a sorted array. The array is small and could easily be sorted.
**The Twist:** Sorting would destroy the original indices, which must be returned. A hash map provides O(n) time without sorting, making it the correct tool despite the "pair sum" signal.
**Code Skeleton:**
```python
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []
```

### 17. 217. Contains Duplicate
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given an integer array, return true if any value appears at least twice.
**Why it fits:** Sorting the array would bring duplicates adjacent, allowing a same-direction scan to detect them. The "sorted array" signal is implicit because duplicates are easier to find in order.
**The Twist:** Sorting is O(n log n). A hash set achieves O(n) average time and is simpler. The problem gives no sorted guarantee, so hashing dominates.
**Code Skeleton:**
```python
def contains_duplicate(nums):
    seen = set()
    for n in nums:
        if n in seen:
            return True
        seen.add(n)
    return False
```

### 18. 53. Maximum Subarray
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Find the contiguous subarray with the largest sum and return its sum.
**Why it fits:** The problem asks about a contiguous subarray, which suggests a sliding window that expands and contracts based on running sums. Two pointers seem applicable.
**The Twist:** The presence of negative numbers breaks the monotonicity required for a simple sliding window. Kadane's dynamic programming tracks the maximum ending at each position without explicit pointers.
**Code Skeleton:**
```python
def max_sub_array(nums):
    current_max = global_max = nums[0]
    for n in nums[1:]:
        current_max = max(n, current_max + n)
        global_max = max(global_max, current_max)
    return global_max
```

### 19. 84. Largest Rectangle in Histogram
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given an array of bar heights, find the largest rectangle in the histogram.
**Why it fits:** The "container/area" archetype is triggered: we want width * height between two bars. Two pointers from the ends could attempt to maximize such an area.
**The Twist:** The optimal rectangle may be bounded by bars that are not at the array ends. A monotonic stack tracking indices of increasing heights is required to efficiently find the nearest smaller bar for each position.
**Code Skeleton:**
```python
def largest_rectangle_area(heights):
    stack = []
    max_area = 0
    heights.append(0)  # sentinel to flush stack
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area
```

### 20. 23. Merge k Sorted Lists
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Merge k sorted linked lists into one sorted linked list.
**Why it fits:** Merging sorted sequences is the canonical two-pointer pattern. We could iteratively merge lists two at a time using the standard merge technique.
**The Twist:** Pairwise merging with two pointers is O(k^2 * n). A min-heap achieves O(nk log k) by always extracting the smallest head among all lists. The merge pattern is correct but the data structure must scale.
**Code Skeleton:**
```python
import heapq

# Definition for singly-linked list node (assumed provided by LeetCode).
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

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

## Pattern Blends (Pattern 02 + Another Pattern)

### 21. 360. Sort Transformed Array
**Archetype:** 2.1 + Math
**Type:** Pattern Blend
**Statement:** Given a sorted array and a quadratic function f(x)=ax^2+bx+c, apply the function to each element and return the resulting array sorted.
**Why it fits:** The input is sorted, and we need to produce sorted output. Converging pointers can compare f(left) and f(right) because a parabola is monotonic on either side of its vertex.
**The Twist:** Depending on the sign of a, the larger value comes from either the ends (a>0, parabola opens upward) or the middle (a<0). We fill the result array from back to front or front to back accordingly.
**Code Skeleton:**
```python
def sort_transformed_array(nums, a, b, c):
    def f(x):
        return a * x * x + b * x + c

    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    index = n - 1 if a > 0 else 0

    while left <= right:
        l_val, r_val = f(nums[left]), f(nums[right])
        if a > 0:
            if l_val > r_val:
                result[index] = l_val
                left += 1
            else:
                result[index] = r_val
                right -= 1
            index -= 1
        else:
            if l_val < r_val:
                result[index] = l_val
                left += 1
            else:
                result[index] = r_val
                right -= 1
            index += 1
    return result
```

### 22. 31. Next Permutation
**Archetype:** 2.2 + Math
**Type:** Pattern Blend
**Statement:** Given an array of integers, rearrange it into the lexicographically next greater permutation. If not possible, sort ascending.
**Why it fits:** We scan from the right (same-direction) to find the first decreasing element. This identifies the pivot. Then we swap it with the smallest larger element to its right and reverse the suffix.
**The Twist:** The algorithm combines a same-direction scan with a suffix reversal. The two-pointer reverse at the end is a sub-pattern, but the core logic is mathematical: finding the pivot and successor.
**Code Skeleton:**
```python
def next_permutation(nums):
    n = len(nums)
    i = n - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i >= 0:
        j = n - 1
        while j >= 0 and nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    left, right = i + 1, n - 1
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left += 1
        right -= 1
```

### 23. 5. Longest Palindromic Substring
**Archetype:** 2.4 + Expand
**Type:** Pattern Blend
**Statement:** Given a string, return the longest palindromic substring.
**Why it fits:** Palindromes are symmetric around a center. For each possible center, we expand two pointers outward while characters match. The longest valid expansion is our answer.
**The Twist:** Unlike the standard palindrome check (one center), we must try 2n-1 centers because palindromes can have odd or even length. The two pointers here expand rather than converge.
**Code Skeleton:**
```python
def longest_palindrome(s):
    if not s:
        return ""
    start, end = 0, 0

    def expand(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1

    for i in range(len(s)):
        len1 = expand(i, i)
        len2 = expand(i, i + 1)
        max_len = max(len1, len2)
        if max_len > end - start:
            start = i - (max_len - 1) // 2
            end = i + max_len // 2
    return s[start:end + 1]
```

### 24. 424. Longest Repeating Character Replacement
**Archetype:** 2.7 + Hash Map
**Type:** Pattern Blend
**Statement:** Given a string and integer k, find the length of the longest substring containing the same letter after at most k replacements.
**Why it fits:** We maintain a sliding window and a frequency map of characters inside it. The window is valid if its length minus the max frequency is <= k (replacements needed).
**The Twist:** The sliding window only expands or shifts right; it never contracts. This works because we only care about the maximum length ever achieved. The hash map tracks frequencies to compute the "cost" of the window.
**Code Skeleton:**
```python
from collections import defaultdict

def character_replacement(s, k):
    freq = defaultdict(int)
    left = 0
    max_freq = 0
    max_len = 0
    for right in range(len(s)):
        freq[s[right]] += 1
        max_freq = max(max_freq, freq[s[right]])
        while (right - left + 1) - max_freq > k:
            freq[s[left]] -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

### 25. 76. Minimum Window Substring
**Archetype:** 2.7 + Hash Map
**Type:** Pattern Blend
**Statement:** Given strings s and t, return the minimum window substring of s such that every character in t is included.
**Why it fits:** A sliding window over s expands until it covers all characters of t, then contracts from the left to find the minimum valid window. A hash map tracks required character counts.
**The Twist:** The window must satisfy a multi-character constraint, not just a single condition. We track "formed" characters to know when the window is valid, then greedily shrink.
**Code Skeleton:**
```python
from collections import Counter, defaultdict

def min_window(s, t):
    if not t or not s:
        return ""
    target = Counter(t)
    required = len(target)
    formed = 0
    window_counts = defaultdict(int)
    left = 0
    ans = float('inf'), None, None
    for right in range(len(s)):
        char = s[right]
        window_counts[char] += 1
        if char in target and window_counts[char] == target[char]:
            formed += 1
        while left <= right and formed == required:
            char = s[left]
            if right - left + 1 < ans[0]:
                ans = (right - left + 1, left, right)
            window_counts[char] -= 1
            if char in target and window_counts[char] < target[char]:
                formed -= 1
            left += 1
    return "" if ans[0] == float('inf') else s[ans[1]:ans[2] + 1]
```

## Interview Simulation (No archetype label given)

### 26. 1574. Shortest Subarray to Remove to Make Array Sorted
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given an integer array, remove one contiguous subarray so that the remaining elements are non-decreasing. Return the shortest such subarray length.
**Why it fits:** We can find the longest non-decreasing prefix and suffix. The answer involves either removing the middle, extending the prefix into the suffix, or extending the suffix into the prefix.
**The Twist:** A naive O(n^2) scan of all removals is too slow. Two pointers on the prefix and suffix allow us to find the best merge point in O(n) time.
**Code Skeleton:**
```python
def find_length_of_shortest_subarray(arr):
    n = len(arr)
    right = n - 1
    while right > 0 and arr[right - 1] <= arr[right]:
        right -= 1
    if right == 0:
        return 0
    result = right
    left = 0
    while left < right and (left == 0 or arr[left - 1] <= arr[left]):
        while right < n and arr[left] > arr[right]:
            right += 1
        result = min(result, right - left - 1)
        left += 1
    return result
```

### 27. 581. Shortest Unsorted Continuous Subarray
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given an integer array, find the shortest continuous subarray that if sorted, the whole array becomes sorted.
**Why it fits:** We can identify where the array stops being sorted from the left and right. Any element out of order must be included in the subarray.
**The Twist:** We track running min and max from the right and left respectively. The subarray boundaries are determined by where elements deviate from the eventual sorted order.
**Code Skeleton:**
```python
def find_unsorted_subarray(nums):
    n = len(nums)
    left, right = 0, n - 1
    
    while left < n - 1 and nums[left] <= nums[left + 1]:
        left += 1
    if left == n - 1:
        return 0
    while right > 0 and nums[right] >= nums[right - 1]:
        right -= 1
    
    sub_min = min(nums[left:right + 1])
    sub_max = max(nums[left:right + 1])
    
    while left >= 0 and nums[left] > sub_min:
        left -= 1
    while right < n and nums[right] < sub_max:
        right += 1
    
    return right - left - 1
```

### 28. 948. Bag of Tokens
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given tokens and initial power, play to maximize score. Face-up costs power, face-up gives score, face-down costs score and gives power.
**Why it fits:** To maximize score, we want to buy cheap tokens with power and sell expensive tokens for power. Sorting lets us use the cheapest and most expensive tokens.
**The Twist:** The greedy strategy uses two pointers. We buy with the left (cheapest) when we can, and sell with the right (most expensive) when we cannot buy but have score. Track max score.
**Code Skeleton:**
```python
def bag_of_tokens_score(tokens, power):
    tokens.sort()
    left, right = 0, len(tokens) - 1
    score = 0
    max_score = 0
    while left <= right:
        if power >= tokens[left]:
            power -= tokens[left]
            score += 1
            left += 1
            max_score = max(max_score, score)
        elif score > 0:
            power += tokens[right]
            score -= 1
            right -= 1
        else:
            break
    return max_score
```

### 29. 611. Valid Triangle Number
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given an array of non-negative integers, return the number of triplets that can form triangles.
**Why it fits:** For three sides to form a triangle, the sum of any two sides must exceed the third. Sorting lets us fix the largest side and use two pointers to count valid pairs.
**The Twist:** Instead of checking all triplets (O(n^3)), we fix the largest side and shrink the window: if nums[left] + nums[right] > nums[i], all pairs between left and right are valid.
**Code Skeleton:**
```python
def triangle_number(nums):
    nums.sort()
    count = 0
    n = len(nums)
    for i in range(n - 1, 1, -1):
        left, right = 0, i - 1
        while left < right:
            if nums[left] + nums[right] > nums[i]:
                count += right - left
                right -= 1
            else:
                left += 1
    return count
```

### 30. 189. Rotate Array
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Rotate the array to the right by k steps in-place.
**Why it fits:** The rotation can be viewed as moving a suffix to the prefix. A buffer array would be O(n) space, but we need O(1) extra space.
**The Twist:** Three reverses achieve the rotation in-place. The two-pointer reverse is used twice: once on the whole array, then on each partition. This is a pointer-based in-place transformation.
**Code Skeleton:**
```python
def rotate(nums, k):
    n = len(nums)
    k %= n
    if k == 0:
        return

    def reverse(left, right):
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1

    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)
```
