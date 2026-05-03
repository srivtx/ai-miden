# Pattern 05: Sliding Window — Drills Part 3

> 5 Near Misses + 5 Pattern Blends + 5 Interview Simulations

---

## Near Misses

### 16. LeetCode 30. Substring with Concatenation of All Words
**Archetype:** 5.3 Variable-Size Window (Minimum)
**Type:** Near Miss
**Statement:** Find all starting indices of substrings that are a concatenation of each word exactly once.
**Why it fits:** The total substring length is fixed (sum of word lengths), but words can appear in any permutation. We slide a fixed-size window and match word frequencies.
**The Twist:** Must match entire words, not characters; there are multiple valid starting offsets within a word length, so we check each offset separately.
**Code Skeleton:**
```python
def find_substring(s: str, words: list[str]) -> list[int]:
    from collections import Counter
    if not words or not s:
        return []
    word_len = len(words[0])
    total_len = word_len * len(words)
    word_count = Counter(words)
    result = []
    for i in range(word_len):
        left = i
        current = Counter()
        count = 0
        for j in range(i, len(s) - word_len + 1, word_len):
            word = s[j:j + word_len]
            if word in word_count:
                current[word] += 1
                count += 1
                while current[word] > word_count[word]:
                    left_word = s[left:left + word_len]
                    current[left_word] -= 1
                    count -= 1
                    left += word_len
                if count == len(words):
                    result.append(left)
            else:
                current.clear()
                count = 0
                left = j + word_len
    return result
```

### 17. LeetCode 862. Shortest Subarray with Sum at Least K
**Archetype:** 5.6 Window with Monotonic Queue
**Type:** Near Miss
**Statement:** Find the shortest subarray with sum >= k. The array may contain negative numbers.
**Why it fits:** With negative numbers, a simple sliding window fails because the sum is not monotonic. We use a monotonic deque on prefix sums to find the shortest valid subarray.
**The Twist:** Negative numbers break the standard two-pointer sliding window invariant; we need prefix sums and a deque to maintain candidates.
**Code Skeleton:**
```python
def shortest_subarray(nums: list[int], k: int) -> int:
    from collections import deque
    n = len(nums)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]

    dq = deque()
    min_len = float('inf')
    for i in range(n + 1):
        # Check if current prefix minus front prefix >= k
        while dq and prefix[i] - prefix[dq[0]] >= k:
            min_len = min(min_len, i - dq.popleft())
        # Maintain monotonic increasing deque
        while dq and prefix[i] <= prefix[dq[-1]]:
            dq.pop()
        dq.append(i)
    return min_len if min_len != float('inf') else -1
```

### 18. LeetCode 480. Sliding Window Median
**Archetype:** 5.6 Window with Monotonic Queue
**Type:** Near Miss
**Statement:** Find the median in every window of size k.
**Why it fits:** The median requires order statistics, which a simple monotonic queue cannot provide. We need two heaps or a sorted data structure to maintain the window.
**The Twist:** Removing arbitrary elements from a heap is O(k); using a sorted list or a balanced BST (e.g., `SortedList`) is more practical for this problem.
**Code Skeleton:**
```python
def median_sliding_window(nums: list[int], k: int) -> list[float]:
    # Simplified using sorted list (bisect). For production, use two heaps with lazy deletion.
    import bisect
    window = sorted(nums[:k])
    result = []
    def get_median():
        if k % 2 == 1:
            return float(window[k // 2])
        return (window[k // 2 - 1] + window[k // 2]) / 2.0

    result.append(get_median())
    for i in range(k, len(nums)):
        # Remove outgoing element
        bisect.insort(window, nums[i])
        idx = bisect.bisect_left(window, nums[i - k])
        window.pop(idx)
        # Note: the insort above is wrong for the slide logic; corrected below
        # Actually: remove old first, then insert new
    # Corrected version:
    window = sorted(nums[:k])
    result = [get_median()]
    for i in range(k, len(nums)):
        # Remove nums[i - k]
        idx = bisect.bisect_left(window, nums[i - k])
        window.pop(idx)
        # Insert nums[i]
        bisect.insort(window, nums[i])
        result.append(get_median())
    return result
```

### 19. LeetCode 395. Longest Substring with At Least K Repeating Characters
**Archetype:** 5.2 Variable-Size Window (At Most K)
**Type:** Near Miss
**Statement:** Find the longest substring where every character appears at least k times.
**Why it fits:** We cannot solve this with a simple sliding window because shrinking when one character drops below k might still leave others valid. We use divide and conquer or iterate over unique character counts.
**The Twist:** For each possible number of unique characters (1 to 26), we run a sliding window that ensures every character in the window appears at least k times.
**Code Skeleton:**
```python
def longest_substring(s: str, k: int) -> int:
    if not s or k < 1:
        return 0
    max_len = 0
    for max_unique in range(1, len(set(s)) + 1):
        freq = {}
        left = 0
        unique = 0
        count_at_least_k = 0
        for right in range(len(s)):
            if s[right] not in freq or freq[s[right]] == 0:
                unique += 1
            freq[s[right]] = freq.get(s[right], 0) + 1
            if freq[s[right]] == k:
                count_at_least_k += 1
            while unique > max_unique:
                if freq[s[left]] == k:
                    count_at_least_k -= 1
                freq[s[left]] -= 1
                if freq[s[left]] == 0:
                    unique -= 1
                left += 1
            if unique == count_at_least_k:
                max_len = max(max_len, right - left + 1)
    return max_len
```

### 20. LeetCode 1358. Number of Substrings Containing All Three Characters
**Archetype:** 5.4 Count-Based Window
**Type:** Near Miss
**Statement:** Count substrings containing at least one occurrence of 'a', 'b', and 'c'.
**Why it fits:** For each right index, we find the leftmost position where all three characters exist in the window. Every valid window ending at right contributes `leftmost + 1` substrings.
**The Twist:** We do not use the `exactly(K)` formula; instead, we track the last occurrence of each character and compute valid subarrays directly.
**Code Skeleton:**
```python
def number_of_substrings(s: str) -> int:
    last_seen = {'a': -1, 'b': -1, 'c': -1}
    count = 0
    for right, ch in enumerate(s):
        last_seen[ch] = right
        # The leftmost valid start is the minimum of last seen positions
        leftmost = min(last_seen.values())
        if leftmost != -1:
            count += leftmost + 1
    return count
```

---

## Pattern Blends

### 21. LeetCode 632. Smallest Range Covering Elements from K Lists
**Archetype:** 5.3 Variable-Size Window (Minimum)
**Type:** Pattern Blend
**Statement:** Find the smallest range that includes at least one number from each of k lists.
**Why it fits:** We maintain a window over a merged view of all lists using a min-heap. The window tracks the current min and max across all lists.
**The Twist:** Multi-list window maintained with a heap; we advance the list that contributed the current minimum to try to shrink the range.
**Code Skeleton:**
```python
def smallest_range(nums: list[list[int]]) -> list[int]:
    import heapq
    pq = []
    current_max = float('-inf')
    for i, lst in enumerate(nums):
        heapq.heappush(pq, (lst[0], i, 0))
        current_max = max(current_max, lst[0])

    best_left, best_right = -10**9, 10**9
    while pq:
        current_min, list_idx, elem_idx = heapq.heappop(pq)
        if current_max - current_min < best_right - best_left:
            best_left, best_right = current_min, current_max
        if elem_idx + 1 == len(nums[list_idx]):
            break
        next_val = nums[list_idx][elem_idx + 1]
        current_max = max(current_max, next_val)
        heapq.heappush(pq, (next_val, list_idx, elem_idx + 1))
    return [best_left, best_right]
```

### 22. LeetCode 523. Continuous Subarray Sum
**Archetype:** 5.5 Multi-Condition Window
**Type:** Pattern Blend
**Statement:** Check if the array has a subarray of size >= 2 with sum divisible by k.
**Why it fits:** Uses prefix sums and a hash map. If `prefix[j] % k == prefix[i] % k`, then the subarray (i, j] has sum divisible by k. The sliding window intuition applies but the solution is prefix-sum based.
**The Twist:** The condition is about modular arithmetic, not direct window values. We need to track the first occurrence of each mod result.
**Code Skeleton:**
```python
def check_subarray_sum(nums: list[int], k: int) -> bool:
    mod_map = {0: -1}  # mod -> earliest index
    prefix = 0
    for i, num in enumerate(nums):
        prefix += num
        mod = prefix % k
        if mod in mod_map:
            if i - mod_map[mod] >= 2:
                return True
        else:
            mod_map[mod] = i
    return False
```

### 23. LeetCode 525. Contiguous Array
**Archetype:** 5.5 Multi-Condition Window
**Type:** Pattern Blend
**Statement:** Find the longest subarray with equal number of 0s and 1s.
**Why it fits:** Transform 0 to -1, then the problem becomes finding the longest subarray with sum 0. Use prefix sum hash map to find matching sums.
**The Twist:** The problem is framed as a sliding window, but the array transformation and prefix sum hash map are the actual solution.
**Code Skeleton:**
```python
def find_max_length(nums: list[int]) -> int:
    index_map = {0: -1}  # prefix_sum -> earliest index
    prefix = 0
    max_len = 0
    for i, num in enumerate(nums):
        prefix += 1 if num == 1 else -1
        if prefix in index_map:
            max_len = max(max_len, i - index_map[prefix])
        else:
            index_map[prefix] = i
    return max_len
```

### 24. LeetCode 1838. Frequency of the Most Frequent Element
**Archetype:** 5.1 Fixed-Size Window
**Type:** Pattern Blend
**Statement:** Maximize the frequency of the most frequent element after at most k increments.
**Why it fits:** After sorting, we use a sliding window to find the largest window where the total cost to make all elements equal to the rightmost element is <= k.
**The Twist:** Sorting is required first; the window tracks the cost (sum of differences) rather than a simple count.
**Code Skeleton:**
```python
def max_frequency(nums: list[int], k: int) -> int:
    nums.sort()
    left = 0
    current_sum = 0
    max_freq = 0
    for right in range(len(nums)):
        current_sum += nums[right]
        # Cost to make all elements in window equal to nums[right]
        while nums[right] * (right - left + 1) - current_sum > k:
            current_sum -= nums[left]
            left += 1
        max_freq = max(max_freq, right - left + 1)
    return max_freq
```

### 25. LeetCode 1151. Minimum Swaps to Group All 1's Together
**Archetype:** 5.1 Fixed-Size Window
**Type:** Pattern Blend
**Statement:** Find the minimum number of swaps to group all 1s together in the array.
**Why it fits:** Count total 1s to determine window size, then slide a fixed window of that size to find the window with the most 1s (minimum 0s to swap).
**The Twist:** The window size is derived from the data (count of 1s), not given as an input parameter.
**Code Skeleton:**
```python
def min_swaps(data: list[int]) -> int:
    ones = sum(data)
    if ones <= 1:
        return 0
    window_ones = sum(data[:ones])
    max_ones = window_ones
    for i in range(ones, len(data)):
        window_ones += data[i] - data[i - ones]
        max_ones = max(max_ones, window_ones)
    return ones - max_ones
```

---

## Interview Simulations

### 26. LeetCode 2962. Count Subarrays Where Max Element Appears at Least K Times
**Archetype:** 5.4 Count-Based Window
**Type:** Interview Sim
**Statement:** Count subarrays where the maximum element of the array appears at least k times.
**Why it fits:** Track the positions of the maximum element. For each right pointer, find the leftmost position where the count of max elements in the window is at least k.
**The Twist:** Only subarrays where the global maximum element appears k times count; the window is bounded by the kth most recent occurrence of the max.
**Code Skeleton:**
```python
def count_subarrays(nums: list[int], k: int) -> int:
    max_val = max(nums)
    count = 0
    left = 0
    max_count = 0
    for right in range(len(nums)):
        if nums[right] == max_val:
            max_count += 1
        while max_count >= k:
            # All subarrays starting from left to right and ending at right or beyond are valid
            count += len(nums) - right
            if nums[left] == max_val:
                max_count -= 1
            left += 1
    return count
```

### 27. LeetCode 2444. Count Subarrays With Fixed Bounds
**Archetype:** 5.5 Multi-Condition Window
**Type:** Interview Sim
**Statement:** Count subarrays where the minimum is minK and the maximum is maxK.
**Why it fits:** Track the last positions of minK, maxK, and any invalid element (outside [minK, maxK]). A valid subarray ending at right must start after the last invalid element and include both minK and maxK.
**The Twist:** Must have both bounds exactly; invalid elements reset the window. The valid start is the max of last invalid, last minK, and last maxK.
**Code Skeleton:**
```python
def count_subarrays_fixed_bounds(nums: list[int], minK: int, maxK: int) -> int:
    last_invalid = -1
    last_min = -1
    last_max = -1
    count = 0
    for i, num in enumerate(nums):
        if num < minK or num > maxK:
            last_invalid = i
        if num == minK:
            last_min = i
        if num == maxK:
            last_max = i
        # Valid start must be after last_invalid and must include both bounds
        valid_start = min(last_min, last_max)
        if valid_start > last_invalid:
            count += valid_start - last_invalid
    return count
```

### 28. LeetCode 2134. Minimum Swaps to Group All 1's Together II
**Archetype:** 5.1 Fixed-Size Window
**Type:** Interview Sim
**Statement:** Find the minimum swaps to group all 1s together in a circular array.
**Why it fits:** Circular array means the first and last elements are adjacent. We double the array or use modulo to simulate circular fixed windows.
**The Twist:** Circular adjacency allows the window to wrap around; we handle this by extending the array or using modulo indexing.
**Code Skeleton:**
```python
def min_swaps_circular(nums: list[int]) -> int:
    n = len(nums)
    ones = sum(nums)
    if ones == 0 or ones == n:
        return 0
    # Use circular window by extending array
    extended = nums + nums
    window_ones = sum(extended[:ones])
    max_ones = window_ones
    for i in range(ones, 2 * n):
        window_ones += extended[i] - extended[i - ones]
        max_ones = max(max_ones, window_ones)
    return ones - max_ones
```

### 29. LeetCode 2779. Maximum Beauty of an Array
**Archetype:** 5.1 Fixed-Size Window
**Type:** Interview Sim
**Statement:** Maximize the length of a subsequence where the difference between any two elements is at most 2*k after incrementing elements by at most k.
**Why it fits:** After sorting, the problem reduces to finding the longest subarray where `nums[right] - nums[left] <= 2*k`. This is a fixed-threshold sliding window.
**The Twist:** The operation allows incrementing each element by at most k, which after sorting translates to a simple difference constraint on the sorted array.
**Code Skeleton:**
```python
def maximum_beauty(nums: list[int], k: int) -> int:
    nums.sort()
    left = 0
    max_len = 0
    for right in range(len(nums)):
        while nums[right] - nums[left] > 2 * k:
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

### 30. LeetCode 2271. Maximum White Tiles Covered by a Carpet
**Archetype:** 5.1 Fixed-Size Window
**Type:** Interview Sim
**Statement:** Find the maximum number of white tiles covered by a carpet of length carpetLen.
**Why it fits:** Sort intervals by start, then use a sliding window over intervals. The carpet can fully cover intervals in the window and partially cover at most one interval at the edge.
**The Twist:** The carpet may partially cover an interval at the window boundary; we must compute the partial coverage explicitly.
**Code Skeleton:**
```python
def maximum_white_tiles(tiles: list[list[int]], carpetLen: int) -> int:
    tiles.sort()
    n = len(tiles)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + (tiles[i][1] - tiles[i][0] + 1)

    max_cover = 0
    left = 0
    for right in range(n):
        carpet_end = tiles[right][0] + carpetLen - 1
        # Move left so that tiles[left] is within or just before carpet
        while left <= right and tiles[left][1] < carpet_end - carpetLen + 1:
            left += 1
        # Actually: find the leftmost tile still relevant
        # Binary search or while loop for left boundary
        while left <= right and tiles[left][1] < tiles[right][0]:
            left += 1

        # Simplified: for each right, binary search leftmost tile with end >= carpet_end - carpetLen + 1
        # Corrected sliding window approach:
        left = 0
        for right in range(n):
            carpet_start = tiles[right][1] - carpetLen + 1
            while tiles[left][1] < carpet_start:
                left += 1
            full_cover = prefix[right] - prefix[left]
            # Partial cover from tiles[left]
            partial_start = max(tiles[left][0], tiles[right][1] - carpetLen + 1)
            partial = tiles[right][1] - partial_start + 1
            max_cover = max(max_cover, full_cover + partial)
    return max_cover
```
