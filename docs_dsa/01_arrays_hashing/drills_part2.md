# Pattern 01: Arrays & Hashing -- Drills Part 2

> **Focus:** Warm-ups and Core Drills
> **Goal:** Solidify recognition of Arrays & Hashing archetypes with progressive difficulty.

---

## Warm-ups

### 1. 217. Contains Duplicate
**Archetype:** 1.1 Existence Checking
**Type:** Warm-Up
**Statement:** Given an integer array, return true if any value appears at least twice.
**Why it fits:** This is the canonical existence-checking problem. We only need to know whether an element has been seen before, which is exactly what a hash set provides in O(1) time.
**The Twist:** None--this is the baseline. The array is unsorted and we only care about presence, not frequency or position.
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

### 2. 242. Valid Anagram
**Archetype:** 1.2 Frequency Counting
**Type:** Warm-Up
**Statement:** Given two strings, return true if one is an anagram of the other.
**Why it fits:** Anagrams have identical character frequencies. A hash map lets us count occurrences in O(n) time and verify equivalence in a single pass.
**The Twist:** None--this is the canonical frequency-counting problem. The strings are lower-case English letters and lengths are moderate.
**Code Skeleton:**
```python
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    count = {}
    for c in s:
        count[c] = count.get(c, 0) + 1
    for c in t:
        if count.get(c, 0) == 0:
            return False
        count[c] -= 1
    return True
```

### 3. 1. Two Sum
**Archetype:** 1.3 Complement Lookup
**Type:** Warm-Up
**Statement:** Given an array of integers and a target, return indices of two numbers that add up to target.
**Why it fits:** For each element, the complement (target - num) is what we need to find. A hash map stores seen values with their indices for O(1) lookup.
**The Twist:** None--this is the canonical complement-lookup problem. Exactly one solution exists, so we can return immediately upon finding a match.
**Code Skeleton:**
```python
def two_sum(nums, target):
    seen = {}  # value -> index
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []  # no solution per problem statement
```

### 4. 49. Group Anagrams
**Archetype:** 1.4 Grouping by Signature
**Type:** Warm-Up
**Statement:** Given an array of strings, group anagrams together.
**Why it fits:** Anagrams share the same sorted-character signature. A hash map keyed by signature groups all matching strings in O(n * k log k) time.
**The Twist:** None--this is the canonical grouping problem. We normalize each string into a canonical form (sorted tuple or count tuple) to serve as the map key.
**Code Skeleton:**
```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())
```

### 5. 560. Subarray Sum Equals K
**Archetype:** 1.5 Prefix Aggregate
**Type:** Warm-Up
**Statement:** Given an array of integers and an integer k, return the total number of subarrays whose sum equals k.
**Why it fits:** The prefix sum at index j minus the prefix sum at index i gives the subarray sum (i, j]. A hash map stores prefix-sum frequencies to count valid pairs in O(n).
**The Twist:** None--this is the canonical prefix-aggregate problem. We accumulate running sums and query how many times (current - k) has occurred.
**Code Skeleton:**
```python
from collections import defaultdict

def subarray_sum(nums, k):
    count = 0
    prefix_sum = 0
    freq = defaultdict(int)
    freq[0] = 1  # empty prefix
    for n in nums:
        prefix_sum += n
        count += freq[prefix_sum - k]
        freq[prefix_sum] += 1
    return count
```

## Core Drills

### 6. 219. Contains Duplicate II
**Archetype:** 1.1 Existence Checking
**Type:** Core Drill
**Statement:** Given an array and integer k, return true if there are two distinct indices i and j such that nums[i] == nums[j] and abs(i - j) <= k.
**Why it fits:** We still only need to check existence, but the "seen" window is now bounded by k. The set represents elements whose indices are within k of the current index.
**The Twist:** The set becomes a sliding window. We must evict the element at index i-k before adding the new element, or the existence check spans too far.
**Code Skeleton:**
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

### 7. 349. Intersection of Two Arrays
**Archetype:** 1.1 Existence Checking
**Type:** Core Drill
**Statement:** Given two integer arrays, return an array of their intersection with each element unique.
**Why it fits:** After loading one array into a set, we iterate the second array and test membership. The result itself should be a set to avoid duplicates in the output.
**The Twist:** Unlike Contains Duplicate, we are doing cross-array existence checking and must deduplicate the result. The smaller array should be hashed to minimize space.
**Code Skeleton:**
```python
def intersection(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    seen = set(nums1)
    result = set()
    for n in nums2:
        if n in seen:
            result.add(n)
    return list(result)
```

### 8. 383. Ransom Note
**Archetype:** 1.2 Frequency Counting
**Type:** Core Drill
**Statement:** Given two strings ransomNote and magazine, return true if ransomNote can be constructed from magazine.
**Why it fits:** We count available characters in magazine, then decrement for each character in ransomNote. Any negative count means the magazine is insufficient.
**The Twist:** Unlike Valid Anagram, the strings are asymmetric. Magazine may have extras, but we only care whether it has enough of each required letter.
**Code Skeleton:**
```python
def can_construct(ransom_note, magazine):
    count = {}
    for c in magazine:
        count[c] = count.get(c, 0) + 1
    for c in ransom_note:
        if count.get(c, 0) == 0:
            return False
        count[c] -= 1
    return True
```

### 9. 387. First Unique Character in a String
**Archetype:** 1.2 Frequency Counting
**Type:** Core Drill
**Statement:** Given a string, find the first non-repeating character and return its index.
**Why it fits:** We need frequency data to know what is unique, but we also need the original order to find the first. Two passes: one to count, one to scan.
**The Twist:** A set is insufficient; we need a hash map of frequencies. The second pass must preserve input order, so we iterate the string again rather than the map.
**Code Skeleton:**
```python
def first_uniq_char(s):
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    for i, c in enumerate(s):
        if freq[c] == 1:
            return i
    return -1
```

### 10. 451. Sort Characters By Frequency
**Archetype:** 1.2 Frequency Counting
**Type:** Core Drill
**Statement:** Given a string, sort it in decreasing order based on character frequency.
**Why it fits:** We count character frequencies, then bucket characters by their counts. The bucket array acts as an inverted index from frequency to characters.
**The Twist:** After counting, we need ordering by value, not by key. Bucket sort achieves O(n) time because the maximum frequency is bounded by the string length.
**Code Skeleton:**
```python
from collections import defaultdict

def frequency_sort(s):
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    buckets = defaultdict(list)
    for c, f in freq.items():
        buckets[f].append(c)
    result = []
    for f in range(len(s), 0, -1):
        for c in buckets.get(f, []):
            result.append(c * f)
    return "".join(result)
```

### 11. 170. Two Sum III - Data structure design
**Archetype:** 1.6 Hash Map Design
**Type:** Core Drill
**Statement:** Design a data structure that accepts a stream of integers and checks if any two elements sum to a value.
**Why it fits:** The archetype shifts from a single function to a class-based design. The hash map must support add() in O(1) and find() in O(n) or better by iterating keys.
**The Twist:** We must handle duplicates carefully. If the target is even and the queried value is target/2, we need to ensure it appears at least twice in the data structure.
**Code Skeleton:**
```python
from collections import defaultdict

class TwoSum:
    def __init__(self):
        self.freq = defaultdict(int)

    def add(self, number):
        self.freq[number] += 1

    def find(self, value):
        for num in self.freq:
            complement = value - num
            if complement in self.freq:
                if complement != num or self.freq[num] > 1:
                    return True
        return False
```

### 12. 454. 4Sum II
**Archetype:** 1.3 Complement Lookup
**Type:** Core Drill
**Statement:** Given four integer arrays, compute how many tuples (i, j, k, l) exist such that A[i] + B[j] + C[k] + D[l] = 0.
**Why it fits:** We pair the arrays into two groups, store all sums of A+B in a hash map, then for each sum of C+D look up its negation. This is complement lookup across four dimensions.
**The Twist:** Instead of a single complement, we are matching pairs of sums. The hash map value is a frequency count because duplicate sums are allowed and each contributes distinct tuples.
**Code Skeleton:**
```python
from collections import defaultdict

def four_sum_count(A, B, C, D):
    count = 0
    sum_ab = defaultdict(int)
    for a in A:
        for b in B:
            sum_ab[a + b] += 1
    for c in C:
        for d in D:
            count += sum_ab.get(-(c + d), 0)
    return count
```

### 13. 205. Isomorphic Strings
**Archetype:** 1.4 Grouping by Signature
**Type:** Core Drill
**Statement:** Given two strings, determine if they are isomorphic.
**Why it fits:** Two strings are isomorphic if their character-to-index mappings are identical in shape. We encode each string into a signature of first-occurrence indices and compare.
**The Twist:** The signature is not the characters themselves, but the pattern of first appearances. We need two maps (or one bidirectional map) to enforce a strict one-to-one relationship.
**Code Skeleton:**
```python
def is_isomorphic(s, t):
    if len(s) != len(t):
        return False
    s_map, t_map = {}, {}
    for i, (cs, ct) in enumerate(zip(s, t)):
        if s_map.get(cs, -1) != t_map.get(ct, -1):
            return False
        s_map[cs] = i
        t_map[ct] = i
    return True
```

### 14. 525. Contiguous Array
**Archetype:** 1.5 Prefix Aggregate
**Type:** Core Drill
**Statement:** Given a binary array, find the maximum length of a contiguous subarray with an equal number of 0 and 1.
**Why it fits:** We treat 0 as -1 and compute prefix sums. When the same prefix sum occurs at two indices, the subarray between them has equal 0s and 1s. A hash map stores first occurrences.
**The Twist:** The prefix sum here is not a simple sum but a transformed balance (count(1) - count(0)). We store the first index of each balance to maximize subarray length.
**Code Skeleton:**
```python
def find_max_length(nums):
    balance = 0
    first_index = {0: -1}  # empty prefix
    max_len = 0
    for i, n in enumerate(nums):
        balance += 1 if n == 1 else -1
        if balance in first_index:
            max_len = max(max_len, i - first_index[balance])
        else:
            first_index[balance] = i
    return max_len
```

### 15. 128. Longest Consecutive Sequence
**Archetype:** 1.8 Sequence Building
**Type:** Core Drill
**Statement:** Given an unsorted array of integers, return the length of the longest consecutive elements sequence.
**Why it fits:** A hash set gives O(1) existence checks. For each number, if it is the start of a sequence (num-1 not in set), we count forward until the sequence breaks.
**The Twist:** We avoid O(n log n) sorting. The key optimization is only starting sequence checks from true sequence beginnings, ensuring overall O(n) time despite the nested-looking loop.
**Code Skeleton:**
```python
def longest_consecutive(nums):
    num_set = set(nums)
    longest = 0
    for n in num_set:
        if n - 1 not in num_set:
            current = n
            streak = 1
            while current + 1 in num_set:
                current += 1
                streak += 1
            longest = max(longest, streak)
    return longest
```
