# Pattern 05: Sliding Window — Complete Archetype Map

> **Pattern Recognition:** When you see "subarray", "substring", "consecutive", "window", "at most K", "longest/shortest contiguous" — think sliding window.
>
> **Fundamental Insight:** If a problem asks about a contiguous subarray/substring, and the brute force is O(n^2) or O(n^3), there is usually an O(n) or O(n log n) window solution.

---

## Archetype 5.1: Fixed-Size Window

### Recognition Signal (10 seconds)
Words: **"size K", "window of size", "subarray of length K", "every consecutive K"**

The question: **"Find something about every window of exactly size K."**

### Core Structure
```python
def fixed_window(nums, k):
    window_sum = sum(nums[:k])
    result = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # Add new, remove old
        result = max(result, window_sum)
    return result
```

### The Invariant
The window slides one position at a time. We remove the element leaving the window and add the element entering the window. Both operations are O(1).

### Canonical Problem: Maximum Average Subarray I (LeetCode 643)
**Statement:** Find contiguous subarray of length k with maximum average.

```python
def find_max_average(nums, k):
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum / k
```

### Variation Family

**V1: Contains Duplicate II (LeetCode 219)**
- **Twist:** Return true if duplicates exist WITHIN distance K of each other
- **Change:** Set becomes a sliding window. Remove elements that fall outside the K window.
- **Key insight:** The set now represents "elements in the current window of size K"

```python
def contains_nearby_duplicate(nums, k):
    window = set()
    for i, n in enumerate(nums):
        if n in window:
            return True
        window.add(n)
        if len(window) > k:
            window.remove(nums[i - k])
    return False
```

**V2: Defuse the Bomb (LeetCode 1652)**
- **Twist:** Circular array, sum next k elements (or previous if k < 0)
- **Change:** Handle circular by concatenating or using modulo. Fixed window on circular array.

**V3: Number of Sub-arrays of Size K (LeetCode 1343)**
- **Twist:** Count subarrays of size K with average >= threshold
- **Change:** Window sum. Compare sum >= threshold * K.

**V4: Grumpy Bookstore Owner (LeetCode 1052)**
- **Twist:** Maximize satisfied customers using secret technique for X consecutive minutes
- **Change:** Fixed window on grumpy minutes. Base satisfaction + window bonus.

**Near Miss: Moving Average from Data Stream**
- **Looks like:** Fixed window
- **But:** Requires storing all elements. Actually just a queue.
- **Lesson:** Fixed window is about arrays, not streams.

---

## Archetype 5.2: Variable-Size Window (At Most K)

### Recognition Signal (10 seconds)
Words: **"longest substring with at most K distinct", "longest subarray with at most K odds"**

The question: **"Expand window while valid, shrink when invalid. Track max valid."**

### Core Structure
```python
def variable_window(s, k):
    left = 0
    freq = {}
    max_len = 0
    for right in range(len(s)):
        freq[s[right]] = freq.get(s[right], 0) + 1
        while len(freq) > k:  # Invalid condition
            freq[s[left]] -= 1
            if freq[s[left]] == 0:
                del freq[s[left]]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

### The Invariant
The window is always valid (satisfies the constraint). When we add a new element that breaks the constraint, we shrink from the left until valid again. The maximum valid window seen is our answer.

### Canonical Problem: Longest Substring Without Repeating Characters (LeetCode 3)
**Statement:** Longest substring with all unique characters.

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

### Variation Family

**V1: Longest Repeating Character Replacement (LeetCode 424)**
- **Twist:** Longest substring with same letter after replacing at most k letters
- **Change:** Window is valid if (window_size - max_freq) <= k. Track max frequency.
- **Key insight:** We don't shrink the window when invalid. We just don't update max_len.

```python
def character_replacement(s, k):
    freq = {}
    left = 0
    max_freq = 0
    max_len = 0
    for right in range(len(s)):
        freq[s[right]] = freq.get(s[right], 0) + 1
        max_freq = max(max_freq, freq[s[right]])
        while (right - left + 1) - max_freq > k:
            freq[s[left]] -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

**V2: Fruit Into Baskets (LeetCode 904)**
- **Twist:** Longest subarray with at most 2 distinct elements
- **Change:** At most 2 distinct = exactly the sliding window template with k=2

**V3: Max Consecutive Ones III (LeetCode 1004)**
- **Twist:** Max consecutive 1s if you can flip at most k 0s
- **Change:** Window is valid if zeros in window <= k

```python
def longest_ones(nums, k):
    left = 0
    zeros = 0
    max_len = 0
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

**V4: Maximize the Confusion of an Exam (LeetCode 2024)**
- **Twist:** Longest contiguous substring of T/F after changing at most k answers
- **Change:** Same as character replacement. Two passes: one for T, one for F.

**V5: Frequency of the Most Frequent Element (LeetCode 1838)**
- **Twist:** Max frequency after k increments
- **Change:** Sort + sliding window. Window valid if (nums[right] * window_size - window_sum) <= k.

**Near Miss: Subarray Sum Equals K (LeetCode 560)**
- **Looks like:** "Find sum equals target"
- **But:** Subarray means contiguous sequence, not a pair. Uses PREFIX SUMS + hash map.
- **Lesson:** Sliding window ONLY works when all numbers are positive (or condition is monotonic).

---

## Archetype 5.3: Variable-Size Window (At Least K / Minimum Window)

### Recognition Signal (10 seconds)
Words: **"minimum window", "smallest substring containing", "cover all characters"**

The question: **"Find the smallest window that satisfies a condition."**

### Core Structure
```python
def min_window(s, t):
    need = {}  # Characters we need
    for c in t:
        need[c] = need.get(c, 0) + 1
    missing = len(t)  # Count of characters still needed
    
    left = start = 0
    min_len = float('inf')
    
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        
        while missing == 0:  # Window is valid, try to shrink
            if right - left + 1 < min_len:
                min_len = right - left + 1
                start = left
            
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    
    return s[start:start + min_len] if min_len != float('inf') else ""
```

### The Invariant
We expand until the window is valid (contains all needed characters). Then we shrink from the left as much as possible while staying valid. Track the minimum valid window.

### Canonical Problem: Minimum Window Substring (LeetCode 76)
**Statement:** Minimum window in s containing all characters of t.

### Variation Family

**V1: Substring with Concatenation of All Words (LeetCode 30)**
- **Twist:** Find starting indices of substring that is concatenation of all words
- **Change:** All words same length. Window size = len(words) * len(word). Use hash map to match word frequencies.

**V2: Smallest Range Covering Elements from K Lists (LeetCode 632)**
- **Twist:** Smallest range with one element from each of k lists
- **Change:** Merge k lists with pointers. Window covers all k lists. Track min range.

**V3: Permutation in String (LeetCode 567)**
- **Twist:** Check if s2 contains permutation of s1
- **Change:** Fixed window of size len(s1). Compare character counts.

**Near Miss: Longest Substring with At Least K Repeating Characters**
- **Looks like:** Minimum window
- **But:** Divide and conquer or recursive split. Not sliding window.
- **Lesson:** "At least K" does not always mean sliding window.

---

## Archetype 5.4: Count-Based Window

### Recognition Signal (10 seconds)
Words: **"count subarrays with exactly K", "number of nice subarrays", "binary subarrays with sum"**

The question: **"Count how many subarrays satisfy a condition."**

### Key Insight
`exactly(K) = at_most(K) - at_most(K-1)`

### Canonical Problem: Subarrays with K Different Integers (LeetCode 992)
**Statement:** Count subarrays with exactly K different integers.

```python
def subarrays_with_k_distinct(nums, k):
    def at_most(k):
        count = {}
        left = 0
        result = 0
        for right in range(len(nums)):
            count[nums[right]] = count.get(nums[right], 0) + 1
            while len(count) > k:
                count[nums[left]] -= 1
                if count[nums[left]] == 0:
                    del count[nums[left]]
                left += 1
            result += right - left + 1
        return result
    
    return at_most(k) - at_most(k - 1)
```

### Variation Family

**V1: Count Number of Nice Subarrays (LeetCode 1248)**
- **Twist:** Count subarrays with exactly k odd numbers
- **Change:** at_most(k) - at_most(k-1) where condition is "odd count"

**V2: Binary Subarrays With Sum (LeetCode 930)**
- **Twist:** Count subarrays with sum equal to goal
- **Change:** at_most(goal) - at_most(goal - 1) for array of 0s and 1s

**Near Miss: Subarray Sums Divisible by K (LeetCode 974)**
- **Looks like:** Count subarrays
- **But:** Uses prefix sums modulo K, not sliding window
- **Lesson:** Counting subarrays with exact sums needs prefix sums, not sliding window

---

## Archetype 5.5: Multi-Condition Window

### Recognition Signal (10 seconds)
Words: **"subarrays with sum divisible by K", "longest subarray with equal 0s and 1s"**

The question: **"Window condition involves transformed data or multiple properties."**

### Canonical Problem: Continuous Subarray Sum (LeetCode 523)
**Statement:** Subarray sum divisible by k.

**Key insight:** (prefix[j] - prefix[i]) % k == 0 ↔ prefix[j] % k == prefix[i] % k

```python
def check_subarray_sum(nums, k):
    remainder_map = {0: -1}  # prefix sum 0 at index -1
    prefix = 0
    for i, num in enumerate(nums):
        prefix += num
        r = prefix % k
        if r in remainder_map:
            if i - remainder_map[r] > 1:
                return True
        else:
            remainder_map[r] = i
    return False
```

### Variation Family

**V1: Contiguous Array (LeetCode 525)**
- **Twist:** Longest subarray with equal 0s and 1s
- **Change:** Treat 0 as -1. Now find longest subarray with sum = 0.

**V2: Maximum Points You Can Obtain from Cards (LeetCode 1423)**
- **Twist:** Pick k cards from beginning or end. Maximize sum.
- **Change:** Complement: total - min subarray sum of middle (n-k) cards. Or: fixed window on ends.

**Near Miss: Shortest Subarray with Sum at Least K (LeetCode 862)**
- **Looks like:** Sliding window
- **But:** Can have negative numbers. Regular sliding window breaks.
- **Fix:** Monotonic deque on prefix sums
- **Lesson:** Sliding window only works when condition is monotonic

---

## Archetype 5.6: Window with Monotonic Queue

### Recognition Signal (10 seconds)
Words: **"sliding window maximum", "max in every window of size K"**

The question: **"Find max/min in every fixed window efficiently."**

### Template (Monotonic Deque)
```python
from collections import deque

def sliding_window_max(nums, k):
    dq = deque()  # Stores indices, values decrease from left to right
    result = []
    
    for i, num in enumerate(nums):
        # Remove elements smaller than current from back
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        dq.append(i)
        
        # Remove front if out of window
        if dq[0] <= i - k:
            dq.popleft()
        
        # Start adding to result once window is full
        if i >= k - 1:
            result.append(nums[dq[0]])
    
    return result
```

### The Invariant
The deque stores indices of elements in decreasing order. The front is always the maximum of the current window. When we see a new element, we remove all smaller elements from the back (they will never be the max). When the front slides out of the window, we remove it.

### Canonical Problem: Sliding Window Maximum (LeetCode 239)
**Statement:** Max in every window of size k.

### Variation Family

**V1: Sliding Window Median (LeetCode 480)**
- **Twist:** Median in every window of size k
- **Change:** Two heaps (max heap for lower half, min heap for upper half). Lazy deletion with hash map.

**V2: Shortest Subarray with Sum at Least K (LeetCode 862)**
- **Twist:** Shortest subarray with sum >= k (can have negative numbers)
- **Change:** Monotonic deque on prefix sums. For each prefix, remove from front if condition met. Maintain increasing deque.

```python
from collections import deque

def shortest_subarray(nums, k):
    n = len(nums)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]
    
    dq = deque()
    min_len = float('inf')
    
    for i in range(n + 1):
        while dq and prefix[i] - prefix[dq[0]] >= k:
            min_len = min(min_len, i - dq.popleft())
        while dq and prefix[i] <= prefix[dq[-1]]:
            dq.pop()
        dq.append(i)
    
    return min_len if min_len != float('inf') else -1
```

**Near Miss: Moving Average from Data Stream**
- **Looks like:** Sliding window
- **But:** Just a circular buffer. No deque needed.
- **Lesson:** Know when the problem is simpler than it looks.

---

## Pattern 05 Mastery Checklist

Before moving to Pattern 06, confirm you can:

- [ ] Fixed-size window sum update
- [ ] Variable window: expand while valid, shrink when invalid
- [ ] Minimum window with "missing" counter
- [ ] Exactly K = at_most(K) - at_most(K-1)
- [ ] Monotonic deque for window max
- [ ] Distinguish: sliding window vs two pointers vs prefix sums
- [ ] Know when NOT to use sliding window (negative numbers, non-monotonic)

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Using sliding window with negatives | Condition is not monotonic | Use prefix sums or monotonic deque |
| Forgetting to delete zero-count keys | len(freq) is wrong | `if freq[x] == 0: del freq[x]` |
| Confusing "at most K" with "exactly K" | Wrong answer | exactly(K) = at_most(K) - at_most(K-1) |
| Not handling empty window | Off-by-one errors | Initialize properly |
| Window max with heap instead of deque | O(n log k) instead of O(n) | Use monotonic deque |

---

## Pattern Blends (What Comes Next)

Sliding window does not live in isolation. It blends with:

- **Hash map:** When tracking frequencies in the window
- **Monotonic deque:** When finding extremes in the window
- **Prefix sums:** When dealing with sums and negative numbers
- **Two pointers:** When the window is on a sorted array

---

*Next: Pattern 06 — Linked List*
