# Pattern 01: Arrays & Hashing

## The Trigger (Read This First)

When you see ANY of these words or concepts in a problem, your brain should immediately think:

> **"Hash Map or Hash Set. Trade space for time."**

| Trigger Words | What It Means |
|---|---|
| "Find two numbers that..." | You need to look up complements or pairs. Hash map. |
| "Count how many times..." | Frequency counting. Hash map. |
| "Contains duplicate" | Existence checking. Hash set. |
| "Is an anagram of..." | Character frequency comparison. Hash map. |
| "Group by..." | Categorization with a key. Hash map. |
| "Unique elements" | Deduplication. Hash set. |
| "Most frequent / top K" | Counting then ranking. Hash map + heap. |
| "In O(n) time" | They are forbidding the O(n^2) brute force. Hash structure is the only way. |
| "Two sum", "Three sum" | Looking for complements. Hash map (or two pointers if sorted). |
| "Check if all characters..." | Set operations. Hash set. |

**The 5-Second Test:** If the brute force solution involves nested loops checking every pair, and they want better than O(n^2), think hashing.

---

## The Core Insight

> **Arrays give you O(1) access by index. Hash maps give you O(1) access by ANY key. When you need to look things up by value, content, or property instead of position, use a hash map.**

### The Fundamental Trade

| Approach | Time | Space | When to Use |
|---|---|---|---|
| Brute force (nested loops) | O(n^2) | O(1) | Small n, or when you cannot use extra space |
| Sort + two pointers | O(n log n) | O(1) or O(log n) | When the array is already sorted, or sorting is allowed and space is tight |
| Hash map/set | O(n) | O(n) | When you need fast lookup and can afford extra space |

**99% of array problems that ask for "better than O(n^2)" are solved by choosing between:
1. Sort + two pointers (if order does not matter and you need O(1) space)
2. Hash map (if order matters or you need O(n) time guaranteed)**

---

## The Mental Model

### The Librarian Analogy

Imagine a library with 10,000 books in a random pile.

- **Brute force:** Walk through every book one by one. Looking for "Harry Potter"? Check book 1, book 2, book 3... O(n).
- **Sorted + binary search:** Arrange books alphabetically. Find "Harry Potter" by checking the middle, then half, then quarter... O(log n). But arranging costs O(n log n).
- **Hash map:** Build a catalog. "Harry Potter is on shelf 7, row 3." Next time, go directly there. O(1) lookup. But you need a whole extra room for the catalog (O(n) space).

### The Frequency Counter Analogy

You are counting votes in an election.

- **Brute force:** For each vote, count how many times that name appears in the entire list. O(n^2).
- **Hash map:** One pass. Tally marks on a whiteboard. "Alice: ||||, Bob: |||". O(n).

### The Set Analogy

You are at a party with a "no duplicate names" rule.

- **Brute force:** For every new person, ask everyone already inside if they have the same name. O(n^2).
- **Hash set:** A bouncer with a clipboard. Check the name, tick it off. O(1) per person. O(n) total.

---

## The Decision Tree

```
Does the problem involve checking existence or membership?
├── YES
│   └── Can you afford O(n) extra space?
│       ├── YES → Hash Set
│       └── NO → Sort + binary search, or bit manipulation if integers are bounded
│
Does the problem involve counting frequencies?
├── YES → Hash Map (key → count)
│
Does the problem involve finding pairs or complements?
├── YES
│   └── Is the array sorted?
│       ├── YES → Two pointers
│       └── NO → Hash Map (store seen elements, check for complement)
│
Does the problem involve grouping or categorizing?
├── YES → Hash Map (key → list of items)
│
Does the problem ask for the most/least frequent?
├── YES → Hash Map for counting, then heap or quickselect for top K
```

---

## The Template

### Hash Set Template (Existence Checking)

```python
def solve(nums):
    seen = set()
    for num in nums:
        if num in seen:          # O(1) lookup
            return True          # Found duplicate / pair
        seen.add(num)            # O(1) insert
    return False
```

### Hash Map Template (Frequency Counting)

```python
def solve(nums):
    count = {}                   # or collections.Counter
    for num in nums:
        count[num] = count.get(num, 0) + 1
    
    # Now use the counts
    for num, freq in count.items():
        if freq > 1:
            return num
```

### Hash Map Template (Complement / Two Sum)

```python
def two_sum(nums, target):
    seen = {}                    # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:   # O(1) lookup
            return [seen[complement], i]
        seen[num] = i            # Store for future lookups
```

**Critical detail:** In the two-sum template, we check BEFORE we add the current element. Why? Because we cannot use the same element twice. If we add first, we might match with ourselves.

---

## The Problem Family

### Warm-Up: Build the Muscle

**Problem W1: Contains Duplicate (LeetCode 217)**
- **Statement:** Given an array, return true if any value appears at least twice.
- **Trigger:** "Contains duplicate", "appears at least twice"
- **Muscle:** Hash set for existence checking.
- **Why this pattern:** You need to check if you have seen a number before. Set gives O(1) "have I seen this?"
- **Code:**
```python
def contains_duplicate(nums):
    seen = set()
    for n in nums:
        if n in seen:
            return True
        seen.add(n)
    return False
```

**Problem W2: Valid Anagram (LeetCode 242)**
- **Statement:** Given two strings, determine if they are anagrams.
- **Trigger:** "Anagram", "same characters", "rearrangement"
- **Muscle:** Hash map for frequency counting.
- **Why this pattern:** Two strings are anagrams iff every character appears the same number of times. Count in one, decrement in other.
- **Code:**
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

**Problem W3: Two Sum (LeetCode 1)**
- **Statement:** Given nums and target, return indices of two numbers that add up to target.
- **Trigger:** "Two numbers that add up to", "pair with sum"
- **Muscle:** Hash map for complement lookup.
- **Why this pattern:** For each number, the complement is `target - num`. If we have seen the complement, we are done.
- **Critical insight:** We check the map BEFORE inserting the current number. This prevents using the same element twice.

---

### Core Problems: Master the Pattern

**Problem C1: Group Anagrams (LeetCode 49)**
- **Statement:** Group all anagrams together.
- **Trigger:** "Group", "anagrams", "categorize"
- **Muscle:** Hash map where the KEY is derived from the item.
- **Key insight:** The key for anagram grouping can be:
  - Sorted string: "eat" and "tea" both become "aet" → O(k log k) per string
  - Character count tuple: (1,0,0,...,1,0,1) for a,e,t → O(k) per string
- **Why this is powerful:** You are not storing the original string as the key. You are storing a *signature* of the string. Any two strings with the same signature are anagrams.
- **Template extension:** When grouping, ask: "What property of the item can serve as a canonical key?"

**Problem C2: Top K Frequent Elements (LeetCode 347)**
- **Statement:** Return the k most frequent elements.
- **Trigger:** "Top K", "most frequent", "highest frequency"
- **Muscle:** Hash map for counting + heap/quickselect for extracting top K.
- **Key insight:** This is a TWO-STEP problem. Step 1: count (hash map). Step 2: find top K (heap or bucket sort).
- **Optimization:** Bucket sort by frequency. Frequency is bounded by n, so bucket sort is O(n).
  - `buckets[frequency].append(num)`
  - Then iterate buckets from high to low.
- **Pattern blend:** Hashing + bucket sort. This is faster than a heap (O(n log k)) when k is large.

**Problem C3: Product of Array Except Self (LeetCode 238)**
- **Statement:** Return an array where each element is the product of all other elements. No division.
- **Trigger:** "Product of all other", "except self", "without division"
- **Muscle:** Prefix/suffix arrays (not hashing, but uses array tricks).
- **Key insight:** The product except self at index i = (product of all before i) * (product of all after i).
  - First pass: compute prefix products.
  - Second pass: compute suffix products and multiply.
- **Why it is here:** It tests whether you think about array relationships without brute force. The hash map pattern does not apply, but the MENTALITY of trading space for time does.
- **Template:**
```python
def product_except_self(nums):
    n = len(nums)
    result = [1] * n
    
    # Prefix products
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]
    
    # Suffix products, multiplied in place
    suffix = 1
    for i in range(n-1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]
    
    return result
```

**Problem C4: Valid Sudoku (LeetCode 36)**
- **Statement:** Determine if a 9x9 Sudoku board is valid.
- **Trigger:** "Valid", "no duplicates in row/column/box"
- **Muscle:** Hash set with ENCODED keys.
- **Key insight:** You need to check three constraints simultaneously. Instead of three separate data structures, encode the constraint into the set key.
  - `(row, num)` for rows
  - `(col, num)` for columns
  - `(box_row, box_col, num)` for boxes
- **Critical trick:** `box_index = (row // 3) * 3 + (col // 3)` turns a 2D box coordinate into a 1D index.
- **Why this is beautiful:** One set. Three constraints. O(1) lookup per constraint.

**Problem C5: Longest Consecutive Sequence (LeetCode 128)**
- **Statement:** Find the length of the longest consecutive elements sequence.
- **Trigger:** "Consecutive", "sequence", "longest streak"
- **Muscle:** Hash set + sequence building.
- **Key insight:** Put all numbers in a set. For each number, ONLY start counting if `num - 1` is NOT in the set. This ensures each sequence is counted exactly once.
- **Why this is O(n):** Each number is visited at most twice (once as a potential start, once in a sequence).
- **Template:**
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

---

### Advanced Twists: Test Your Depth

**Problem A1: Subarray Sum Equals K (LeetCode 560)**
- **Statement:** Find the total number of continuous subarrays whose sum equals k.
- **Trigger:** "Subarray sum equals", "count subarrays"
- **Muscle:** Prefix sum + hash map.
- **Key insight:** `sum(i..j) = prefix[j+1] - prefix[i]`. We want `prefix[j+1] - prefix[i] = k`, so `prefix[i] = prefix[j+1] - k`. As we iterate, we store prefix sums in a hash map and check how many times `current_prefix - k` has occurred.
- **Why this is advanced:** It combines hashing with the prefix sum technique. You are not storing elements; you are storing AGGREGATES.
- **Common trap:** Forgetting to initialize `count[0] = 1` to handle subarrays starting from index 0.

**Problem A2: Design Underground System (LeetCode 1396)**
- **Statement:** Design a system to track check-in/check-out times and calculate average travel time between stations.
- **Trigger:** "Design", "average", "track"
- **Muscle:** Two hash maps (in-progress trips and completed statistics).
- **Key insight:** Not all hash map problems are "count frequencies." Sometimes you need MULTIPLE hash maps to track different states of the same entity.
  - `check_ins[id] = (station_name, time)` for active trips
  - `travel_stats[(start, end)] = (total_time, count)` for averages

**Problem A3: Insert Delete GetRandom O(1) (LeetCode 380)**
- **Statement:** Design a data structure that supports insert, delete, and getRandom in average O(1).
- **Trigger:** "Design", "O(1)", "getRandom"
- **Muscle:** Hash map + array SWAP-TO-END for O(1) deletion.
- **Key insight:** Arrays give O(1) random access (for getRandom). Hash maps give O(1) lookup. To delete from an array in O(1), SWAP the element with the last element and pop.
  - `val_to_index[val]` tells us where `val` lives in the array.
  - To delete: swap with last, update the moved element's index, pop.
- **Why this is powerful:** It combines two data structures, each contributing the operation they are best at.

---

## The Traps

| Trap | What They Do | How to Beat It |
|---|---|---|
| "Sort first" | They give you an unsorted array but you sort it anyway, losing the original indices | Read the problem: do they want indices or just values? If indices, you cannot sort without tracking original positions (use enumerate). |
| "Use too much space" | They constrain space to O(1) | Then you cannot use a hash map. Sort + two pointers, or bit manipulation, or in-place swaps. |
| "Check before insert" | In two-sum, if you insert before checking, you might match an element with itself | Always check the map BEFORE adding the current element. |
| "Off-by-one in prefix sums" | Prefix sum array is length n+1 | `prefix[i]` = sum of `nums[0..i-1]`. `sum(i..j)` = `prefix[j+1] - prefix[i]`. |
| "Forgetting to initialize" | In subarray sum = k, forgetting `count[0] = 1` | A prefix sum of 0 occurs before the array starts. Initialize it. |
| "Mutable keys" | Using a list as a hash map key | Keys must be hashable. Use tuples instead of lists. |

---

## The Mastery Checklist

Before moving to Pattern 02, you should be able to:

- [ ] See "find two numbers that sum to X" and immediately write the hash map two-sum template
- [ ] See "count frequency" and immediately write the counter template
- [ ] See "group by" and ask "what is the canonical key?"
- [ ] See "consecutive sequence" and think "set + only start from beginnings"
- [ ] See "subarray sum equals K" and think "prefix sum + hash map"
- [ ] Know when to use a set (existence) vs a map (frequency/grouping)
- [ ] Know when sorting + two pointers beats a hash map
- [ ] Design a data structure that combines array + hash map for O(1) everything

---

## Pattern Blends (What Comes Next)

Arrays & Hashing does not live in isolation. It blends with:

- **Two Pointers:** When the array is sorted and you need pairs.
- **Sliding Window:** When you need subarrays with a property, and you use a hash map to track window contents.
- **Heap:** When you need top K frequent elements (hash map counts, heap extracts).
- **Bit Manipulation:** When you need to find a single number (XOR beats hash set for space).

---

*Next: Pattern 02 — Two Pointers*
