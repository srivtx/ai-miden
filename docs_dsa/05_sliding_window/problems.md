# Pattern 05: Sliding Window — Practice Problems

## Fixed-Size Window

### 643. Maximum Average Subarray I
**Statement:** Find contiguous subarray of length k with maximum average.
**Intuition:** Window sum. Add new element, subtract element leaving window.
**Code:**
```python
def find_max_average(nums, k):
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum / k
```

### 219. Contains Duplicate II
**Statement:** Contains duplicate within distance k.
**Intuition:** Set window of size k. Check existence before adding.
**Code:**
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

### 1652. Defuse the Bomb
**Statement:** Circular array, sum next k elements (or previous if k < 0).
**Intuition:** Handle circular by concatenating or using modulo. Fixed window.

### 1343. Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold
**Statement:** Count subarrays of size K with average >= threshold.
**Intuition:** Window sum. Compare sum >= threshold * K.

### 1052. Grumpy Bookstore Owner
**Statement:** Maximize satisfied customers using secret technique for X consecutive minutes.
**Intuition:** Fixed window on grumpy minutes. Base satisfaction + window bonus.

---

## Variable-Size Window (At Most K)

### 3. Longest Substring Without Repeating Characters
**Statement:** Longest substring with all unique characters.
**Intuition:** Hash set tracks window. Shrink when duplicate found.
**Code:**
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

### 424. Longest Repeating Character Replacement
**Statement:** Longest substring with same letter after replacing at most k letters.
**Intuition:** Window is valid if (window_size - max_freq) <= k. Track max frequency.
**Code:**
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

### 904. Fruit Into Baskets
**Statement:** Longest subarray with at most 2 distinct elements.
**Intuition:** At most 2 distinct = exactly the sliding window template.
**Code:**
```python
def total_fruit(fruits):
    basket = {}
    left = 0
    max_picked = 0
    for right in range(len(fruits)):
        basket[fruits[right]] = basket.get(fruits[right], 0) + 1
        while len(basket) > 2:
            basket[fruits[left]] -= 1
            if basket[fruits[left]] == 0:
                del basket[fruits[left]]
            left += 1
        max_picked = max(max_picked, right - left + 1)
    return max_picked
```

### 1004. Max Consecutive Ones III
**Statement:** Max consecutive 1s if you can flip at most k 0s.
**Intuition:** Window is valid if zeros in window <= k.
**Code:**
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

### 1493. Longest Subarray of 1's After Deleting One Element
**Statement:** Longest subarray of 1s after deleting one element.
**Intuition:** Same as max consecutive ones with k=1, but must delete exactly one.

### 2024. Maximize the Confusion of an Exam
**Statement:** Longest contiguous substring of T/F after changing at most k answers.
**Intuition:** Same as character replacement. Two passes: one for T, one for F.

### 1838. Frequency of the Most Frequent Element
**Statement:** Max frequency after k increments.
**Intuition:** Sort + sliding window. Window valid if (nums[right] * window_size - window_sum) <= k.

---

## Variable-Size Window (Minimum Window)

### 76. Minimum Window Substring
**Statement:** Minimum window in s containing all characters of t.
**Intuition:** Expand until window contains all needed. Shrink from left while still valid.
**Code:**
```python
def min_window(s, t):
    need = {}
    for c in t:
        need[c] = need.get(c, 0) + 1
    missing = len(t)
    left = start = 0
    min_len = float('inf')
    for right, ch in enumerate(s):
        if need.get(ch, 0) > 0:
            missing -= 1
        need[ch] = need.get(ch, 0) - 1
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

### 209. Minimum Size Subarray Sum
**Statement:** Minimum length subarray with sum >= target.
**Intuition:** Positive numbers only. Expand right, shrink left while sum >= target.
**Code:**
```python
def min_sub_array_len(target, nums):
    left = total = 0
    min_len = float('inf')
    for right in range(len(nums)):
        total += nums[right]
        while total >= target:
            min_len = min(min_len, right - left + 1)
            total -= nums[left]
            left += 1
    return min_len if min_len != float('inf') else 0
```

### 30. Substring with Concatenation of All Words
**Statement:** Find all starting indices of substring that is concatenation of all words.
**Intuition:** All words same length. Window size = len(words) * len(word). Use hash map to match word frequencies.

### 632. Smallest Range Covering Elements from K Lists
**Statement:** Smallest range that includes at least one number from each of k lists.
**Intuition:** Merge k lists with pointers. Window covers all k lists. Track min range.

### 567. Permutation in String
**Statement:** Check if s2 contains permutation of s1.
**Intuition:** Fixed window of size len(s1). Compare character counts.

---

## Count-Based Window (Exactly K)

### 992. Subarrays with K Different Integers
**Statement:** Count subarrays with exactly K different integers.
**Intuition:** at_most(K) - at_most(K-1).
**Code:**
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

### 1248. Count Number of Nice Subarrays
**Statement:** Count subarrays with exactly k odd numbers.
**Intuition:** at_most(k) - at_most(k-1) where condition is "odd count".

### 930. Binary Subarrays With Sum
**Statement:** Count subarrays with sum equal to goal.
**Intuition:** at_most(goal) - at_most(goal - 1) for array of 0s and 1s.

---

## Multi-Condition / Advanced

### 862. Shortest Subarray with Sum at Least K
**Statement:** Shortest subarray with sum >= k (can have negative numbers).
**Intuition:** Monotonic deque on prefix sums. For each prefix, remove from front if condition met. Maintain increasing deque.
**Code:**
```python
def shortest_subarray(nums, k):
    from collections import deque
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

### 239. Sliding Window Maximum
**Statement:** Max in every window of size k.
**Intuition:** Monotonic decreasing deque. Front is max.
**Code:**
```python
def max_sliding_window(nums, k):
    from collections import deque
    dq = deque()
    result = []
    for i, num in enumerate(nums):
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

### 480. Sliding Window Median
**Statement:** Median in every window of size k.
**Intuition:** Two heaps (max heap for lower half, min heap for upper half). Lazy deletion with hash map.

### 1423. Maximum Points You Can Obtain from Cards
**Statement:** Pick k cards from beginning or end. Maximize sum.
**Intuition:** Complement: total - min subarray sum of middle (n-k) cards. Or: fixed window on ends.

### 523. Continuous Subarray Sum
**Statement:** Subarray sum divisible by k.
**Intuition:** Prefix sum mod k. If same remainder at two indices, subarray between them is divisible by k.

### 525. Contiguous Array
**Statement:** Longest subarray with equal 0s and 1s.
**Intuition:** Treat 0 as -1. Want subarray sum = 0. Prefix sum + first occurrence map.

---

## Near Misses & Traps

**Trap:** Using sliding window when numbers can be negative.
- Example: Shortest subarray sum >= K with negatives.
- Fix: Monotonic deque or prefix sums. Regular sliding window breaks because shrinking doesn't guarantee sum decreases.

**Trap:** Confusing "at most K" with "exactly K".
- Fix: exactly(K) = at_most(K) - at_most(K-1). Always.

**Trap:** Window with hash map but forgetting to delete zero-count keys.
- Fix: `if freq[x] == 0: del freq[x]` so `len(freq)` is accurate.

**Near Miss:** Subarray Sum Equals K (560) with negative numbers.
- Looks like sliding window but requires prefix sums + hash map.
- Lesson: Sliding window ONLY works when all numbers are positive (or condition is monotonic).

---

## Mixed Drill Set

Solve these in order. Identify the archetype before coding:
1. 643 — Fixed window
2. 3 — Variable window, at most
3. 209 — Variable window, minimum
4. 992 — Count-based, exactly K
5. 862 — Monotonic deque
6. 239 — Monotonic deque
7. 424 — Variable window with replacement
8. 76 — Minimum window substring
9. 1004 — Variable window, count condition
10. 1838 — Sort + window
