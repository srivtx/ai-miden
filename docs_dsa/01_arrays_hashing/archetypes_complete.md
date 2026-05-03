# Pattern 01: Arrays & Hashing — Complete Archetype Map

> **Pattern Recognition:** When you see "find", "count", "duplicate", "unique", "frequency", "group", "pair", "complement", "subarray sum" — think hash structures.
>
> **Fundamental Trade:** Brute force is O(n^2) with O(1) space. Hashing is O(n) time with O(n) space. Sorting is O(n log n) with O(1) space. Choose based on constraints.

---

## Archetype 1.1: Existence Checking (Set Membership)

### Recognition Signal (10 seconds)
Words: **"contains", "duplicate", "seen before", "already exists", "appears at least twice", "is present"**

The question is always: **"Have I seen this element before?"**

### Core Structure
```
Create empty set
For each element:
    If element in set: return True (or index, or count)
    Add element to set
Return False
```

### The Invariant
You only need to know if something EXISTS, not how many times or where. A set gives O(1) existence checking.

### Canonical Problem: Contains Duplicate (LeetCode 217)
**Statement:** Given an array, return true if any value appears at least twice.

**Why this archetype:** The entire problem is existence checking. We don't care about frequency, just "have I seen this number before?"

```python
def contains_duplicate(nums):
    seen = set()
    for n in nums:
        if n in seen:
            return True
        seen.add(n)
    return False
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

**V2: Contains Duplicate III (LeetCode 220)**
- **Twist:** Return true if there are two numbers whose absolute difference is at most t, and index difference at most k
- **Change:** Bucket sort + sliding window. Numbers are grouped into buckets of size t+1.
- **Key insight:** If two numbers are in the same bucket, their diff <= t. If in adjacent buckets, check explicitly.

**V3: First Unique Character (LeetCode 387)**
- **Twist:** Find the FIRST character that appears exactly once
- **Change:** Two passes. First pass: count frequencies (hash map). Second pass: find first with count 1.
- **Key insight:** Set is insufficient; you need frequency data. But the core is still existence/uniqueness.

**V4: Intersection of Two Arrays (LeetCode 349)**
- **Twist:** Find unique elements common to both arrays
- **Change:** Convert one array to set, iterate other array checking membership
- **Key insight:** Set intersection is a built-in operation, but understanding it as "existence in both sets" is the point

**V5: Happy Number (LeetCode 202)**
- **Twist:** Does repeatedly replacing n with sum of squares of digits eventually reach 1?
- **Change:** If not happy, it enters a cycle. Use set to detect cycle.
- **Key insight:** Not about array elements, but about detecting repeated states. Same archetype: "have I seen this state before?"

```python
def is_happy(n):
    seen = set()
    while n != 1:
        if n in seen:
            return False
        seen.add(n)
        n = sum(int(d)**2 for d in str(n))
    return True
```

**Near Miss: Single Number (LeetCode 136)**
- **Looks like:** "Find the element that appears only once"
- **But:** Using a set is O(n) space. XOR gives O(1) space.
- **Lesson:** Always check if bit manipulation can replace hashing for integer arrays.

### The Traps
| Trap | What Happens | Fix |
|---|---|---|
| Using a list instead of set | "if n in list" is O(n), making total O(n^2) | Always use set for existence |
| Forgetting to handle empty input | Runtime error | Check edge cases first |
| Modifying set while iterating | Runtime error | Iterate the array, not the set |

---

## Archetype 1.2: Frequency Counting

### Recognition Signal (10 seconds)
Words: **"count", "frequency", "how many times", "most common", "rarest", "anagram", "same characters"**

The question is always: **"How many times does each element appear?"**

### Core Structure
```
Create empty counter map
For each element:
    counter[element] += 1
Use the counter to answer the question
```

### Canonical Problem: Valid Anagram (LeetCode 242)
**Statement:** Given two strings, determine if they are anagrams.

**Why this archetype:** Anagrams have identical character frequencies. Count in string s, decrement in string t, all counts must be zero.

```python
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    count = {}
    for c in s:
        count[c] = count.get(c, 0) + 1
    for c in t:
        if c not in count or count[c] == 0:
            return False
        count[c] -= 1
    return True
```

### Variation Family

**V1: Find the Difference (LeetCode 389)**
- **Twist:** String t is generated by shuffling s and adding one letter. Find the added letter.
- **Change:** Count characters in s, then in t. The one with count -1 is the answer.
- **Alternative:** XOR all characters in both strings. The result is the extra character.

**V2: Ransom Note (LeetCode 383)**
- **Twist:** Can you construct string A using characters from string B (each char in B can be used once)?
- **Change:** Count characters in magazine. For each char in ransomNote, decrement count. If any count goes negative, return False.
- **Key insight:** "Can I build X from Y?" is a frequency comparison where X's counts must be <= Y's counts.

```python
def can_construct(ransom_note, magazine):
    count = {}
    for c in magazine:
        count[c] = count.get(c, 0) + 1
    for c in ransom_note:
        if count.get(c, 0) <= 0:
            return False
        count[c] -= 1
    return True
```

**V3: Sort Characters by Frequency (LeetCode 451)**
- **Twist:** Sort characters by frequency, most frequent first
- **Change:** Count frequencies, then sort by frequency descending
- **Key insight:** Frequency counting + sorting by value. Buckets can make it O(n).

**V4: Frequency of the Most Frequent Element (LeetCode 1838)**
- **Twist:** You can increment elements. What's the max frequency achievable with k operations?
- **Change:** Sort + sliding window. For each window, check if you can make all elements equal to the max within k operations.
- **Pattern blend:** Frequency + sorting + sliding window. This is how problems get harder.

**V5: Minimum Consecutive Cards to Pick Up (LeetCode 2260)**
- **Twist:** Find minimum number of consecutive cards to pick up to get a matching pair
- **Change:** Track last seen index of each card. For each card, if seen before, window size = i - last_index + 1.
- **Key insight:** Frequency counting with INDEX tracking. The hash map stores the last position, not the count.

**Near Miss: Top K Frequent Elements**
- **Looks like:** Frequency counting
- **But:** Requires extracting top K, which needs a heap or bucket sort
- **Lesson:** Counting is step 1. Ranking/count extraction is step 2 and may need another pattern.

---

## Archetype 1.3: Complement Lookup (The Two-Sum Family)

### Recognition Signal (10 seconds)
Words: **"pair", "two numbers", "sum to", "complement", "add up to", "difference of"**

The question is always: **"For the current element, what partner do I need, and have I seen it?"**

### Core Structure
```
Create empty map: value -> index
For each element at index i:
    complement = target - element
    If complement in map:
        return [map[complement], i]
    map[element] = i
```

### The Invariant
The complement is what you need to reach the target. By storing seen elements, each new element only needs one lookup to find its partner.

**Critical rule:** Check the map BEFORE inserting the current element. This prevents self-matching.

### Canonical Problem: Two Sum (LeetCode 1)
**Statement:** Given nums and target, return indices of two numbers that add up to target.

```python
def two_sum(nums, target):
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
```

### Variation Family

**V1: Two Sum II — Sorted (LeetCode 167)**
- **Twist:** Array is sorted. Return 1-based indices.
- **Change:** Two pointers instead of hash map! Left and right converge.
- **Key insight:** When sorted, two pointers is O(1) space and O(n) time. Hash map is still valid but uses O(n) space unnecessarily.
- **Decision rule:** Sorted → two pointers. Unsorted → hash map.

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

**V2: 3Sum (LeetCode 15)**
- **Twist:** Find all unique triplets that sum to zero
- **Change:** Fix one number, then two-sum the rest with target = -fixed_num
- **Key insight:** Reduce N-sum to (N-1)-sum. Base case is always two-sum.
- **Optimization:** Sort first, then use two pointers for the inner two-sum. Skip duplicates.

```python
def three_sum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]:
                    left += 1
                while left < right and nums[right] == nums[right-1]:
                    right -= 1
                left += 1
                right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return result
```

**V3: 4Sum (LeetCode 18)**
- **Twist:** Find all unique quadruplets that sum to target
- **Change:** Fix two numbers, two-sum the rest. Or: sort, then nested loops + two pointers.
- **Key insight:** The pattern generalizes. N-sum = sort + (N-2) nested loops + two pointers.

**V4: Two Sum with Duplicates Allowed (LeetCode 1 variant)**
- **Twist:** Can use same element twice? (Usually no, but what if yes?)
- **Change:** If yes, check map AFTER inserting. If no, check BEFORE.
- **Key insight:** The order of "check vs insert" determines whether self-pairing is allowed.

**V5: Count Pairs with Sum Less Than Target**
- **Twist:** Count all pairs (i,j) where nums[i] + nums[j] < target
- **Change:** Sort + two pointers. For each left, move right inward until sum < target. All pairs between left and right are valid.
- **Key insight:** "Count pairs with condition" usually needs sorting + two pointers, not hash map.

**V6: Two Sum Less Than or Equal to K (Bucket)**
- **Twist:** Find max pair sum <= K
- **Change:** Sort + two pointers. Start from ends, if sum <= K, record it and move left up. Else move right down.
- **Pattern blend:** Complement idea + optimization (max/min instead of exact).

**Near Miss: Subarray Sum Equals K (LeetCode 560)**
- **Looks like:** "Find sum equals target"
- **But:** Subarray means contiguous sequence, not a pair. Uses PREFIX SUM + hash map.
- **Lesson:** "Sum equals K" could mean pair (two-sum) OR subarray (prefix sums). Read carefully!

---

## Archetype 1.4: Grouping by Signature

### Recognition Signal (10 seconds)
Words: **"group", "categorize", "anagrams together", "same type", "equivalent", "transform into same form"**

The question is always: **"These items are different on the surface but equivalent in structure. How do I group them?"**

### Core Structure
```
Create empty map: signature -> list of items
For each item:
    signature = compute_signature(item)
    map[signature].append(item)
Return map.values()
```

### The Invariant
Two items belong in the same group if and only if they have the same signature. The signature is a "canonical form."

**Key question:** What is the signature?
- Anagrams → sorted string OR character count tuple
- Same digits → digit frequency tuple
- Equivalent expressions → normalized form

### Canonical Problem: Group Anagrams (LeetCode 49)
**Statement:** Group all anagrams together.

**Signature options:**
1. Sorted string: "eat" → "aet". Time: O(k log k) per string.
2. Character count tuple: (1,0,0,...,1,0,1). Time: O(k) per string.

```python
def group_anagrams(strs):
    groups = {}
    for s in strs:
        # Signature: sorted string
        sig = ''.join(sorted(s))
        # Or: character count tuple
        # sig = tuple(sorted(Counter(s).items()))
        groups.setdefault(sig, []).append(s)
    return list(groups.values())
```

### Variation Family

**V1: Find Duplicate File in System (LeetCode 609)**
- **Twist:** Group files with the same content together
- **Change:** Signature is the file content itself (or a hash of it)
- **Key insight:** The file path is the item, the content is the signature. Group by content.

**V2: Uncommon Words from Two Sentences (LeetCode 884)**
- **Twist:** Find words that appear exactly once across both sentences
- **Change:** Signature is the word itself. Group by word, filter groups with size 1.
- **Key insight:** Grouping + frequency filtering.

**V3: Determine if Two Strings Are Close (LeetCode 1657)**
- **Twist:** Two strings are "close" if you can transform one to the other by swapping any two existing characters
- **Change:** Signature = (set of characters, sorted frequency counts). Both must match.
- **Key insight:** The operation preserves character set and frequency distribution, but not which char has which frequency.

```python
def close_strings(word1, word2):
    if set(word1) != set(word2):
        return False
    return sorted(Counter(word1).values()) == sorted(Counter(word2).values())
```

**V4: Number of Provinces (LeetCode 547 variant with signatures)**
- **Twist:** Group cities by direct/indirect connection
- **Change:** Signature is the connected component. Use Union-Find (but conceptually: group by equivalence).
- **Pattern blend:** Grouping + graph connectivity.

**V5: Largest Component Size by Common Factor (LeetCode 952)**
- **Twist:** Group numbers that share a common factor > 1
- **Change:** Signature = prime factors. Group numbers with overlapping prime factors.
- **Key insight:** Use union-find on prime factors. Two numbers are connected if they share any prime factor.

**Near Miss: Top K Frequent Words**
- **Looks like:** Grouping by word
- **But:** Requires sorting by frequency then lexicographical order
- **Lesson:** Grouping is step 1. Ranking within groups is step 2.

---

## Archetype 1.5: Prefix Aggregate (Running Totals)

### Recognition Signal (10 seconds)
Words: **"subarray sum", "running total", "cumulative", "prefix", "up to index i", "balance", "count of subarrays where..."**

The question is always: **"What is the aggregate from index 0 to i, and how does that help us?"**

### Core Structure
```
prefix = 0
for i in range(n):
    prefix += nums[i]
    # Use prefix to answer question
```

### The Invariant
prefix[i] = sum of nums[0..i-1]. The sum of any subarray nums[i..j] = prefix[j+1] - prefix[i].

### Canonical Problem: Subarray Sum Equals K (LeetCode 560)
**Statement:** Find total number of continuous subarrays whose sum equals k.

**Key insight:** 
- sum(i..j) = prefix[j+1] - prefix[i]
- We want prefix[j+1] - prefix[i] = k
- Therefore: prefix[i] = prefix[j+1] - k

As we iterate j, we count how many times (current_prefix - k) has occurred before.

```python
def subarray_sum(nums, k):
    count = {0: 1}  # prefix sum of 0 occurs before array starts
    prefix = 0
    result = 0
    for num in nums:
        prefix += num
        if prefix - k in count:
            result += count[prefix - k]
        count[prefix] = count.get(prefix, 0) + 1
    return result
```

**Critical initialization:** `count[0] = 1` handles subarrays starting from index 0.

### Variation Family

**V1: Continuous Subarray Sum (LeetCode 523)**
- **Twist:** Subarray sum is divisible by k
- **Change:** Store prefix % k instead of prefix. If same remainder seen before, subarray sum is divisible by k.
- **Key insight:** (prefix[j] - prefix[i]) % k == 0  ↔  prefix[j] % k == prefix[i] % k
- **Trick:** Remainder must be positive. Use `(prefix % k + k) % k` for negative numbers.

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

**V2: Product of Array Except Self (LeetCode 238)**
- **Twist:** Each element = product of all others. No division.
- **Change:** Two prefix passes. Left-to-right: prefix products. Right-to-left: suffix products, multiplied into result.
- **Key insight:** result[i] = (product of all before i) * (product of all after i)

```python
def product_except_self(nums):
    n = len(nums)
    result = [1] * n
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n-1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]
    return result
```

**V3: Find Pivot Index (LeetCode 724)**
- **Twist:** Find index where left sum equals right sum
- **Change:** Total sum - left_sum - current = right_sum. Check if left_sum == right_sum.
- **Key insight:** Prefix sum on the fly. No hash map needed, just one running total.

**V4: Range Sum Query — Immutable (LeetCode 303)**
- **Twist:** Multiple sum range queries on same array
- **Change:** Precompute prefix sums once. Each query is O(1): sum(i,j) = prefix[j+1] - prefix[i]
- **Key insight:** Precomputation trades O(n) space for O(1) query time.

**V5: Contiguous Array (LeetCode 525)**
- **Twist:** Find longest subarray with equal 0s and 1s
- **Change:** Treat 0 as -1. Now find longest subarray with sum = 0.
- **Key insight:** Transform the problem into "subarray sum equals K" where K=0.

```python
def find_max_length(nums):
    count_map = {0: -1}  # balance -> first index
    balance = 0
    max_len = 0
    for i, num in enumerate(nums):
        balance += 1 if num == 1 else -1
        if balance in count_map:
            max_len = max(max_len, i - count_map[balance])
        else:
            count_map[balance] = i
    return max_len
```

**Near Miss: Maximum Subarray (LeetCode 53)**
- **Looks like:** Subarray sum
- **But:** Wants maximum sum, not count of subarrays with specific sum. Uses Kadane's algorithm (greedy/DP), not prefix sums.
- **Lesson:** "Subarray sum" could mean count (hash map) OR maximum (Kadane). Read the goal carefully.

---

## Archetype 1.6: Hash Map Design (Custom Data Structures)

### Recognition Signal (10 seconds)
Words: **"design", "implement", "data structure", "O(1) time", "O(1) space per operation", "get", "put", "delete"**

The question is always: **"Build a data structure that supports specific operations in O(1) time."**

### Core Structure
```
Usually combines:
- Hash map for O(1) lookup
- Array or linked list for O(1) insertion/deletion
- Or: Multiple hash maps for bidirectional lookup
```

### Canonical Problem: Insert Delete GetRandom O(1) (LeetCode 380)
**Statement:** Design a data structure that supports insert, remove, and getRandom in average O(1).

**Why this needs two structures:**
- Array gives O(1) random access (for getRandom)
- Hash map gives O(1) lookup (for insert/delete)
- But array deletion is O(n) unless we swap with last element

```python
class RandomizedSet:
    def __init__(self):
        self.val_to_idx = {}  # Hash map: value -> index in array
        self.values = []      # Array: values
    
    def insert(self, val):
        if val in self.val_to_idx:
            return False
        self.val_to_idx[val] = len(self.values)
        self.values.append(val)
        return True
    
    def remove(self, val):
        if val not in self.val_to_idx:
            return False
        # Swap with last element for O(1) deletion
        idx = self.val_to_idx[val]
        last_val = self.values[-1]
        self.values[idx] = last_val
        self.val_to_idx[last_val] = idx
        self.values.pop()
        del self.val_to_idx[val]
        return True
    
    def getRandom(self):
        return random.choice(self.values)
```

**Critical trick:** Swap-to-end. This makes array deletion O(1) but requires updating the moved element's index in the hash map.

### Variation Family

**V1: LRU Cache (LeetCode 146)**
- **Twist:** Least Recently Used cache with get and put in O(1)
- **Change:** Hash map + Doubly Linked List. Hash map for O(1) lookup. Linked list for O(1) move-to-front and remove.
- **Key insight:** The doubly linked list maintains access order. Most recent at head, least recent at tail.
- **This is the most important design problem.** Master it completely.

**V2: LFU Cache (LeetCode 460)**
- **Twist:** Least Frequently Used cache
- **Change:** Hash map + multiple doubly linked lists (one per frequency). Plus a min-frequency tracker.
- **Key insight:** More complex than LRU. Need to track both frequency AND recency within the same frequency.

**V3: All O(1) Data Structure (LeetCode 432)**
- **Twist:** Insert, delete, getMaxKey, getMinKey all in O(1)
- **Change:** Hash map + doubly linked list of frequency buckets. Each bucket contains keys with that frequency.
- **Key insight:** Similar to LFU but tracks ALL keys, not just cache eviction.

**V4: Time Based Key-Value Store (LeetCode 981)**
- **Twist:** Set key-value with timestamp. Get returns value at or before given timestamp.
- **Change:** Hash map of key -> list of (timestamp, value). Get uses binary search on timestamps.
- **Pattern blend:** Hash map + binary search. Not pure O(1) for get.

**V5: Design Underground System (LeetCode 1396)**
- **Twist:** Check in at station A, check out at station B. Calculate average travel time.
- **Change:** Two hash maps. Active trips: id -> (station, time). Completed stats: (start, end) -> (total_time, count)
- **Key insight:** Multiple hash maps track different states of the same entity.

**Near Miss: Snapshot Array**
- **Looks like:** Design problem with O(1) get/put
- **But:** Requires version history. Uses hash map of sparse arrays or binary search on versions.
- **Lesson:** If history matters, pure O(1) is impossible. Some form of versioning or binary search is needed.

---

## Archetype 1.7: Constraint Satisfaction (Validation)

### Recognition Signal (10 seconds)
Words: **"valid", "is it correct", "satisfy", "rules", "constraints", "no duplicates in row/column/box"**

The question is always: **"Does this configuration violate any rules?"**

### Core Structure
```
For each rule:
    Use hash set/map to check for violations
If any violation found, return False
Return True
```

### Canonical Problem: Valid Sudoku (LeetCode 36)
**Statement:** Determine if a 9x9 Sudoku board is valid.

**Key insight:** Three constraints: no duplicates in any row, column, or 3x3 box.
Instead of three separate data structures, encode the constraint into the set key.

```python
def is_valid_sudoku(board):
    seen = set()
    for i in range(9):
        for j in range(9):
            val = board[i][j]
            if val == '.':
                continue
            # Encode: (row, val), (col, val), (box, val)
            row_key = (i, val)
            col_key = (j, val)
            box_key = (i // 3, j // 3, val)
            
            if row_key in seen or col_key in seen or box_key in seen:
                return False
            seen.update([row_key, col_key, box_key])
    return True
```

**Critical trick:** `box_key = (i // 3, j // 3, val)` maps each cell to its 3x3 box.

### Variation Family

**V1: Isomorphic Strings (LeetCode 205)**
- **Twist:** Two strings are isomorphic if chars in s can be replaced to get t, with one-to-one mapping
- **Change:** Two hash maps: s->t and t->s. Bidirectional mapping must be consistent.
- **Key insight:** One map is insufficient. Need to check both directions.

```python
def is_isomorphic(s, t):
    if len(s) != len(t):
        return False
    s_to_t = {}
    t_to_s = {}
    for c1, c2 in zip(s, t):
        if c1 in s_to_t and s_to_t[c1] != c2:
            return False
        if c2 in t_to_s and t_to_s[c2] != c1:
            return False
        s_to_t[c1] = c2
        t_to_s[c2] = c1
    return True
```

**V2: Word Pattern (LeetCode 290)**
- **Twist:** Pattern "abba" matches "dog cat cat dog"
- **Change:** Same as isomorphic strings, but mapping is pattern char -> word
- **Key insight:** Split the string into words first, then apply isomorphic check.

**V3: Minimum Index Sum of Two Lists (LeetCode 599)**
- **Twist:** Find common restaurant with minimum index sum
- **Change:** Hash map: restaurant -> index in list1. Iterate list2, check common and track min index sum.
- **Key insight:** Validation + optimization. First find common, then optimize the metric.

**V4: Check if Every Row and Column Contains All Integers (LeetCode 2133)**
- **Twist:** Check if n x n matrix is a valid Latin square (each row/col has 1..n)
- **Change:** For each row and column, check if set equals {1, 2, ..., n}
- **Key insight:** Constraint satisfaction on both dimensions.

**Near Miss: Valid Parentheses**
- **Looks like:** "Valid" constraint checking
- **But:** Uses a stack, not a hash set. Order matters (last opened must be first closed).
- **Lesson:** "Valid" could mean order-dependent (stack) or order-independent (set).

---

## Archetype 1.8: Sequence Building (State Tracking)

### Recognition Signal (10 seconds)
Words: **"longest consecutive", "streak", "sequence", "chain", "build", "connect", "union"**

The question is always: **"What is the longest sequence I can build from these elements?"**

### Core Structure
```
Put all elements in a set
For each element:
    If element-1 is NOT in set:  # This is the start of a sequence
        Build sequence forward
        Track maximum length
```

### The Invariant
Each sequence is built exactly once — when we encounter its smallest element. The `if num-1 not in set` check ensures this.

### Canonical Problem: Longest Consecutive Sequence (LeetCode 128)
**Statement:** Find the length of the longest consecutive elements sequence.

```python
def longest_consecutive(nums):
    num_set = set(nums)
    longest = 0
    
    for num in num_set:
        # Only start counting if this is the beginning of a sequence
        if num - 1 not in num_set:
            current_num = num
            current_streak = 1
            
            while current_num + 1 in num_set:
                current_num += 1
                current_streak += 1
            
            longest = max(longest, current_streak)
    
    return longest
```

**Why this is O(n):** Each number is visited at most twice: once as a potential start, once in a while loop.

### Variation Family

**V1: Longest Harmonious Subsequence (LeetCode 594)**
- **Twist:** Longest subsequence where max-min = 1
- **Change:** Count frequencies. For each unique number, check if num+1 exists. Length = count[num] + count[num+1]
- **Key insight:** The sequence only has two distinct values. Count frequencies, then check adjacent pairs.

```python
def find_lhs(nums):
    count = Counter(nums)
    longest = 0
    for num in count:
        if num + 1 in count:
            longest = max(longest, count[num] + count[num + 1])
    return longest
```

**V2: Maximum Size Subarray Sum Equals K (already covered in prefix aggregate)**
- **Pattern blend:** Sequence building + prefix sums

**V3: Array of Doubled Pairs (LeetCode 954)**
- **Twist:** Can you reorder array so that every even-indexed element is double the previous?
- **Change:** Count frequencies. Start from smallest. For each x, check if 2x exists with sufficient count.
- **Key insight:** Greedy + frequency map. Always try to pair the smallest available element first.

**V4: Replace Elements in an Array (LeetCode 2295)**
- **Twist:** Replace all occurrences of element with another element
- **Change:** Hash map tracks current value for each "logical" position. When replacing, update the mapping.
- **Key insight:** The array values change, but we track the logical identity through a map.

**Near Miss: Union-Find Problems**
- **Looks like:** "Connect elements", "groups"
- **But:** Uses union-find data structure, not just hash sets
- **Lesson:** For simple consecutive sequences, hash set is enough. For arbitrary connections, union-find is needed.

---

## Pattern 01 Mastery Checklist

Before moving to Pattern 02, confirm you can:

- [ ] **Existence:** See "contains duplicate" and write set solution in 30 seconds
- [ ] **Frequency:** See "anagram" and write counter solution in 30 seconds
- [ ] **Complement:** See "two sum" and write hash map solution in 30 seconds
- [ ] **Grouping:** See "group anagrams" and write signature-based grouping in 45 seconds
- [ ] **Prefix:** See "subarray sum equals K" and write prefix sum + hash map in 60 seconds
- [ ] **Design:** Explain how to combine array + hash map for O(1) insert/delete/random
- [ ] **Validation:** See "valid Sudoku" and write encoded-key set solution in 45 seconds
- [ ] **Sequence:** See "longest consecutive" and write start-from-beginning solution in 45 seconds
- [ ] **Distinguish:** Tell apart "two sum" (complement) vs "subarray sum" (prefix) vs "max subarray" (Kadane)
- [ ] **Blend:** Recognize when a problem needs hashing + another pattern (sorting, two pointers, etc.)

---

*Next: Pattern 02 — Two Pointers*
