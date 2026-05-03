# Pattern 05: Sliding Window

> **Pattern Recognition:** When you see "subarray", "substring", "consecutive", "window", "at most K", "longest/shortest contiguous" — think sliding window.
>
> **Fundamental Insight:** If a problem asks about a contiguous subarray/substring, and the brute force is O(n^2) or O(n^3), there is usually an O(n) or O(n log n) window solution.

---

## Archetype 5.1: Fixed-Size Window

### Recognition Signal
Words: **"size K", "window of size", "subarray of length K", "every consecutive K"**

The question: **"Find something about every window of exactly size K."**

### Template
```python
def fixed_window(nums, k):
    window_sum = sum(nums[:k])
    result = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        result = max(result, window_sum)
    return result
```

### Problems
- Maximum Average Subarray I (LeetCode 643)
- Contains Duplicate II (LeetCode 219) — set window
- Defuse the Bomb (LeetCode 1652)

---

## Archetype 5.2: Variable-Size Window (At Most K)

### Recognition Signal
Words: **"longest substring with at most K distinct", "longest subarray with at most K odds"**

The question: **"Expand window while valid, shrink when invalid. Track max valid."**

### Template
```python
def variable_window(s, k):
    left = 0
    freq = {}
    max_len = 0
    for right in range(len(s)):
        freq[s[right]] = freq.get(s[right], 0) + 1
        while len(freq) > k:
            freq[s[left]] -= 1
            if freq[s[left]] == 0:
                del freq[s[left]]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

### Problems
- Longest Substring Without Repeating Characters (LeetCode 3)
- Fruit Into Baskets (LeetCode 904)
- Max Consecutive Ones III (LeetCode 1004)
- Longest Repeating Character Replacement (LeetCode 424)

---

## Archetype 5.3: Variable-Size Window (At Least K / Minimum Window)

### Recognition Signal
Words: **"minimum window", "smallest substring containing", "cover all characters"**

The question: **"Find the smallest window that satisfies a condition."**

### Template
```python
def min_window(s, t):
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

### Problems
- Minimum Window Substring (LeetCode 76)
- Substring with Concatenation of All Words (LeetCode 30)
- Smallest Range Covering Elements from K Lists (LeetCode 632)

---

## Archetype 5.4: Count-Based Window

### Recognition Signal
Words: **"count subarrays with exactly K", "number of nice subarrays", "binary subarrays with sum"**

The question: **"Count how many subarrays satisfy a condition."**

### Key Insight
`exactly(K) = at_most(K) - at_most(K-1)`

### Problems
- Subarrays with K Different Integers (LeetCode 992)
- Count Number of Nice Subarrays (LeetCode 1248)
- Binary Subarrays With Sum (LeetCode 930)

---

## Archetype 5.5: Multi-Condition Window

### Recognition Signal
Words: **"subarrays with sum divisible by K", "longest subarray with equal 0s and 1s"**

The question: **"Window condition involves transformed data or multiple properties."**

### Problems
- Continuous Subarray Sum (LeetCode 523) — prefix mod K
- Contiguous Array (LeetCode 525) — treat 0 as -1
- Maximum Points You Can Obtain from Cards (LeetCode 1423) — pick from ends

---

## Archetype 5.6: Window with Monotonic Queue

### Recognition Signal
Words: **"sliding window maximum", "max in every window of size K"**

The question: **"Find max/min in every fixed window efficiently."**

### Template (Monotonic Deque)
```python
def sliding_window_max(nums, k):
    from collections import deque
    dq = deque()
    result = []
    for i, num in enumerate(nums):
        while dq and nums[dq[-1]] < num:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

### Problems
- Sliding Window Maximum (LeetCode 239)
- Sliding Window Median (LeetCode 480) — two heaps
- Shortest Subarray with Sum at Least K (LeetCode 862) — monotonic deque

---

## Mastery Checklist
- [ ] Fixed-size window sum update
- [ ] Variable window: expand while valid, shrink when invalid
- [ ] Minimum window with "missing" counter
- [ ] Exactly K = at_most(K) - at_most(K-1)
- [ ] Monotonic deque for window max
- [ ] Distinguish: sliding window vs two pointers vs prefix sums
