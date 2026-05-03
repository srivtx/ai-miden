# Pattern 05: Sliding Window — Drills Part 2

> 5 Warm-ups + 10 Core Drills

---

## Warm-Ups

### 1. LeetCode 643. Maximum Average Subarray I
**Archetype:** 5.1 Fixed-Size Window
**Type:** Warm-Up
**Statement:** Find the contiguous subarray of length k with the maximum average.
**Why it fits:** The window size is fixed at k. We compute the initial window sum, then slide it across the array updating the sum in O(1) per step.
**The Twist:** Only the sum matters; the average is computed once at the end by dividing the max sum by k.
**Code Skeleton:**
```python
def find_max_average(nums: list[int], k: int) -> float:
    if not nums or k > len(nums):
        return 0.0
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum / k
```

### 2. LeetCode 219. Contains Duplicate II
**Archetype:** 5.1 Fixed-Size Window
**Type:** Warm-Up
**Statement:** Check if there are two distinct indices i and j such that nums[i] == nums[j] and abs(i - j) <= k.
**Why it fits:** We maintain a sliding window (hash set) of the last k elements. If we see a duplicate within the window, return True.
**The Twist:** Uses a hash set instead of sum/count; the window is maintained by adding the new element and removing the element that falls out.
**Code Skeleton:**
```python
def contains_nearby_duplicate(nums: list[int], k: int) -> bool:
    seen = set()
    for i, num in enumerate(nums):
        if num in seen:
            return True
        seen.add(num)
        if len(seen) > k:
            seen.remove(nums[i - k])
    return False
```

### 3. LeetCode 3. Longest Substring Without Repeating Characters
**Archetype:** 5.2 Variable-Size Window (At Most K)
**Type:** Warm-Up
**Statement:** Find the length of the longest substring without repeating characters.
**Why it fits:** We expand the window by moving `right`, and shrink from `left` whenever a duplicate is found inside the window. The max valid window size is tracked.
**The Twist:** K is implicit (all distinct). A hash map tracks the last seen index of each character to jump the left pointer efficiently.
**Code Skeleton:**
```python
def length_of_longest_substring(s: str) -> int:
    char_index = {}
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            left = char_index[ch] + 1
        char_index[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

### 4. LeetCode 424. Longest Repeating Character Replacement
**Archetype:** 5.2 Variable-Size Window (At Most K)
**Type:** Warm-Up
**Statement:** Find the longest substring containing the same letter after replacing at most k characters.
**Why it fits:** The window is valid if `window_length - max_freq <= k`. We expand the window and only shrink if it becomes invalid.
**The Twist:** We do not strictly shrink when invalid; `max_freq` may be stale from a previous window, but the formula still yields the correct max length.
**Code Skeleton:**
```python
def character_replacement(s: str, k: int) -> int:
    freq = {}
    left = 0
    max_freq = 0
    max_len = 0
    for right in range(len(s)):
        freq[s[right]] = freq.get(s[right], 0) + 1
        max_freq = max(max_freq, freq[s[right]])
        # Window is invalid if replacements needed > k
        while (right - left + 1) - max_freq > k:
            freq[s[left]] -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

### 5. LeetCode 1004. Max Consecutive Ones III
**Archetype:** 5.2 Variable-Size Window (At Most K)
**Type:** Warm-Up
**Statement:** Find the longest subarray of 1s after flipping at most k 0s.
**Why it fits:** The window is valid if the count of 0s inside it is <= k. We expand and shrink to maintain this invariant.
**The Twist:** The array contains only 0s and 1s, so the condition is simply counting zeros in the current window.
**Code Skeleton:**
```python
def longest_ones(nums: list[int], k: int) -> int:
    left = 0
    zero_count = 0
    max_len = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zero_count += 1
        while zero_count > k:
            if nums[left] == 0:
                zero_count -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

---

## Core Drills

### 6. LeetCode 76. Minimum Window Substring
**Archetype:** 5.3 Variable-Size Window (Minimum)
**Type:** Core Drill
**Statement:** Find the minimum window substring containing all characters of t.
**Why it fits:** Expand until the window contains all required characters, then shrink from the left as much as possible while still valid. Track the minimum valid window.
**The Twist:** Uses a "missing" counter to avoid scanning the entire frequency map on each iteration, reducing complexity.
**Code Skeleton:**
```python
def min_window(s: str, t: str) -> str:
    from collections import Counter
    need = Counter(t)
    missing = len(t)
    left = start = 0
    min_len = float('inf')
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if right - left + 1 < min_len:
                min_len = right - left + 1
                start = left
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return s[start:start + min_len] if min_len != float('inf') else ""
```

### 7. LeetCode 904. Fruit Into Baskets
**Archetype:** 5.2 Variable-Size Window (At Most K)
**Type:** Core Drill
**Statement:** Find the longest subarray with at most 2 distinct integers (fruit types).
**Why it fits:** Classic at-most-K sliding window with k=2. The hash map tracks the count of each fruit type in the window.
**The Twist:** The problem is framed as collecting fruit into baskets, but it maps directly to the longest subarray with at most 2 distinct elements.
**Code Skeleton:**
```python
def total_fruit(fruits: list[int]) -> int:
    basket = {}
    left = 0
    max_len = 0
    for right in range(len(fruits)):
        basket[fruits[right]] = basket.get(fruits[right], 0) + 1
        while len(basket) > 2:
            basket[fruits[left]] -= 1
            if basket[fruits[left]] == 0:
                del basket[fruits[left]]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

### 8. LeetCode 209. Minimum Size Subarray Sum
**Archetype:** 5.3 Variable-Size Window (Minimum)
**Type:** Core Drill
**Statement:** Find the minimal length subarray with sum >= target.
**Why it fits:** All positive numbers guarantee that as the window expands, the sum increases monotonically. We expand to satisfy the condition, then shrink to find the minimum.
**The Twist:** If no valid subarray exists, return 0 instead of the default infinity.
**Code Skeleton:**
```python
def min_sub_array_len(target: int, nums: list[int]) -> int:
    left = 0
    current_sum = 0
    min_len = float('inf')
    for right in range(len(nums)):
        current_sum += nums[right]
        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= nums[left]
            left += 1
    return min_len if min_len != float('inf') else 0
```

### 9. LeetCode 239. Sliding Window Maximum
**Archetype:** 5.6 Window with Monotonic Queue
**Type:** Core Drill
**Statement:** Find the maximum in every window of size k.
**Why it fits:** A monotonic deque maintains indices of elements in decreasing order. The front of the deque is always the max of the current window.
**The Twist:** The deque stores indices, not values, so we can efficiently remove elements that have left the window.
**Code Skeleton:**
```python
def max_sliding_window(nums: list[int], k: int) -> list[int]:
    from collections import deque
    dq = deque()
    result = []
    for i, num in enumerate(nums):
        # Remove elements smaller than current from back
        while dq and nums[dq[-1]] < num:
            dq.pop()
        dq.append(i)
        # Remove front if out of window
        if dq[0] <= i - k:
            dq.popleft()
        # Start appending results after first window is full
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

### 10. LeetCode 992. Subarrays with K Different Integers
**Archetype:** 5.4 Count-Based Window
**Type:** Core Drill
**Statement:** Count subarrays with exactly K distinct integers.
**Why it fits:** Uses the inclusion-exclusion principle: `exactly(K) = at_most(K) - at_most(K-1)`. We need a helper that counts subarrays with at most K distinct integers.
**The Twist:** Requires writing and calling a helper function; the main insight is the transformation from exactly to at-most.
**Code Skeleton:**
```python
def subarrays_with_k_distinct(nums: list[int], k: int) -> int:
    def at_most(k_distinct: int) -> int:
        freq = {}
        left = 0
        count = 0
        for right in range(len(nums)):
            freq[nums[right]] = freq.get(nums[right], 0) + 1
            while len(freq) > k_distinct:
                freq[nums[left]] -= 1
                if freq[nums[left]] == 0:
                    del freq[nums[left]]
                left += 1
            count += right - left + 1  # All subarrays ending at right are valid
        return count

    return at_most(k) - at_most(k - 1)
```

### 11. LeetCode 1248. Count Number of Nice Subarrays
**Archetype:** 5.4 Count-Based Window
**Type:** Core Drill
**Statement:** Count subarrays with exactly k odd numbers.
**Why it fits:** Transform the array into binary (odd=1, even=0), then count subarrays with sum exactly k using the same `at_most(k) - at_most(k-1)` technique.
**The Twist:** The array transformation is implicit; we count odd numbers directly in the frequency map.
**Code Skeleton:**
```python
def number_of_subarrays(nums: list[int], k: int) -> int:
    def at_most_k_odds(limit: int) -> int:
        left = 0
        odds = 0
        count = 0
        for right in range(len(nums)):
            if nums[right] % 2 == 1:
                odds += 1
            while odds > limit:
                if nums[left] % 2 == 1:
                    odds -= 1
                left += 1
            count += right - left + 1
        return count

    return at_most_k_odds(k) - at_most_k_odds(k - 1)
```

### 12. LeetCode 930. Binary Subarrays With Sum
**Archetype:** 5.4 Count-Based Window
**Type:** Core Drill
**Statement:** Count non-empty subarrays with sum goal (array of 0s and 1s).
**Why it fits:** With all non-negative numbers, we can use the sliding window to count subarrays with sum <= goal, then apply inclusion-exclusion.
**The Twist:** Because the array contains only 0s and 1s, the sliding window works perfectly. For arbitrary positive numbers, prefix sums might be needed.
**Code Skeleton:**
```python
def num_subarrays_with_sum(nums: list[int], goal: int) -> int:
    def at_most(target: int) -> int:
        if target < 0:
            return 0
        left = 0
        current_sum = 0
        count = 0
        for right in range(len(nums)):
            current_sum += nums[right]
            while current_sum > target:
                current_sum -= nums[left]
                left += 1
            count += right - left + 1
        return count

    return at_most(goal) - at_most(goal - 1)
```

### 13. LeetCode 567. Permutation in String
**Archetype:** 5.1 Fixed-Size Window
**Type:** Core Drill
**Statement:** Check if s2 contains a permutation of s1.
**Why it fits:** A permutation of s1 has the same length and exact character frequencies. We slide a fixed window of len(s1) over s2 and compare frequency arrays.
**The Twist:** Must match exact frequencies of all 26 letters, not just the set of characters present.
**Code Skeleton:**
```python
def check_inclusion(s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False
    from collections import Counter
    need = Counter(s1)
    window = Counter(s2[:len(s1)])
    if need == window:
        return True
    for i in range(len(s1), len(s2)):
        window[s2[i]] += 1
        window[s2[i - len(s1)]] -= 1
        if window[s2[i - len(s1)]] == 0:
            del window[s2[i - len(s1)]]
        if need == window:
            return True
    return False
```

### 14. LeetCode 1423. Maximum Points You Can Obtain from Cards
**Archetype:** 5.5 Multi-Condition Window
**Type:** Core Drill
**Statement:** Pick k cards from the beginning or end to maximize the sum.
**Why it fits:** Instead of picking from ends, we find the minimum subarray of size n-k in the middle. The cards not picked form a fixed-size window.
**The Twist:** The window represents the cards you do NOT pick; minimizing this window maximizes the picked cards.
**Code Skeleton:**
```python
def max_score(card_points: list[int], k: int) -> int:
    n = len(card_points)
    window_size = n - k
    if window_size == 0:
        return sum(card_points)
    window_sum = sum(card_points[:window_size])
    min_window = window_sum
    for i in range(window_size, n):
        window_sum += card_points[i] - card_points[i - window_size]
        min_window = min(min_window, window_sum)
    return sum(card_points) - min_window
```

### 15. LeetCode 1652. Defuse the Bomb
**Archetype:** 5.1 Fixed-Size Window
**Type:** Core Drill
**Statement:** Replace each element with the sum of the next k elements in a circular array.
**Why it fits:** Circular fixed-size window. We can handle wrapping by using a doubled array or modulo arithmetic.
**The Twist:** k can be negative, meaning we sum the previous |k| elements instead of the next k.
**Code Skeleton:**
```python
def decrypt(code: list[int], k: int) -> list[int]:
    n = len(code)
    if k == 0:
        return [0] * n
    result = []
    extended = code * 2  # Handle circularity
    for i in range(n):
        if k > 0:
            result.append(sum(extended[i + 1:i + 1 + k]))
        else:
            result.append(sum(extended[i + n + k:i + n]))
    return result
```
