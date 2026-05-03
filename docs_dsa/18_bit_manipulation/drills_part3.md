# Pattern 18: Bit Manipulation — Drills Part 3

> **Focus:** Near Misses (5) + Pattern Blends (5) + Interview Simulation (5)
>
> **Goal:** Train pattern recognition under disguise, cross-pattern synthesis, and full interview-ready problem solving.

---

## Near Misses

### Problem 1. LeetCode 476. Number Complement
**Archetype:** 18.5 Bitwise Operations
**Type:** Near Miss
**Statement:** Return the complement of a positive integer by flipping its bits, with the leading zeros up to the most significant 1 also considered.
**Why it fits:** This looks like a simple bitwise NOT, but Python's unlimited integer size means `~n` adds infinite leading 1s. You must create a mask of the same bit-length as `n`.
**The Twist:** The mask is `(1 << num_bits) - 1` where `num_bits = n.bit_length()`. The complement is then `mask ^ n`.
**Code Skeleton:**
```python
def find_complement(num: int) -> int:
    if num == 0:
        return 1

    # Create a mask with all 1s of the same length as num
    mask = (1 << num.bit_length()) - 1
    return num ^ mask
```

---

### Problem 2. LeetCode 1009. Complement of Base 10 Integer
**Archetype:** 18.5 Bitwise Operations
**Type:** Near Miss
**Statement:** Return the complement of a non-negative integer in base-10 representation of its binary form.
**Why it fits:** This is identical in logic to Number Complement but framed without referencing bits explicitly. It tests the same mask-generation insight.
**The Twist:** The edge case `n = 0` must return `1` because its binary is `0` and the complement is `1`. For all other `n`, you use the same bit-length mask approach.
**Code Skeleton:**
```python
def bitwise_complement(n: int) -> int:
    if n == 0:
        return 1

    # Mask covers exactly the bit-length of n
    mask = (1 << n.bit_length()) - 1
    return n ^ mask
```

---

### Problem 3. LeetCode 1318. Minimum Flips to Make the OR of Two Numbers Equal to Third
**Archetype:** 18.5 Bitwise Operations
**Type:** Near Miss
**Statement:** Given three positive integers `a`, `b`, and `c`, return the minimum flips required in some bits of `a` and/or `b` such that `a OR b == c`.
**Why it fits:** This requires case-by-case bit analysis rather than a single bit trick. For each bit position, you determine if `a` or `b` need to flip based on the target `c` bit.
**The Twist:** If `c` has a 0 bit, both `a` and `b` must have 0 at that position (potentially 2 flips). If `c` has a 1 bit, at least one of `a` or `b` must have 1 (0 or 1 flip). You analyze bit by bit.
**Code Skeleton:**
```python
def min_flips(a: int, b: int, c: int) -> int:
    flips = 0
    for _ in range(32):
        bit_a = a & 1
        bit_b = b & 1
        bit_c = c & 1

        if bit_c == 0:
            # Both a and b must have 0 here
            flips += bit_a + bit_b
        else:
            # At least one of a or b must have 1
            if bit_a == 0 and bit_b == 0:
                flips += 1

        a >>= 1
        b >>= 1
        c >>= 1

    return flips
```

---

### Problem 4. LeetCode 2997. Minimum Number of Operations to Make Array XOR Equal to K
**Archetype:** 18.3 XOR Properties
**Type:** Near Miss
**Statement:** Given a 0-indexed integer array `nums` and a positive integer `k`, return the minimum number of operations to make the bitwise XOR of all elements equal to `k`.
**Why it fits:** The XOR of all elements is a single value. Changing one element `nums[i]` to any value changes the total XOR by exactly `nums[i] ^ new_val`. The minimal operation count is the number of differing bits between `current_xor` and `k`.
**The Twist:** You can change any element to any value in a single operation. Thus, one operation can fix arbitrarily many bits. The answer is simply the Hamming distance between `xor_all` and `k`.
**Code Skeleton:**
```python
def min_operations(nums, k: int) -> int:
    xor_all = 0
    for num in nums:
        xor_all ^= num

    # Each differing bit between xor_all and k requires one operation
    diff = xor_all ^ k
    return bin(diff).count('1')
```

---

### Problem 5. LeetCode 2571. Minimum Operations to Reduce an Integer to 0
**Archetype:** 18.5 Bitwise Operations / 18.6 Bit DP
**Type:** Near Miss
**Statement:** Given an integer `n`, in one operation you can either flip the rightmost 0 bit and all bits to its right, or if the number is even, divide by 2. Return the minimum operations to reduce `n` to 0.
**Why it fits:** This is a greedy/bit manipulation problem disguised as BFS. Consecutive 1s can be merged by flipping the 0 to their left, and trailing 0s are removed by halving.
**The Twist:** The optimal strategy is greedy: remove trailing zeros with division. For trailing 1s, if there is only one 1, flip it. If there are multiple consecutive 1s, flip the 0 to their left to merge them into a single operation.
**Code Skeleton:**
```python
def minimum_operations(n: int) -> int:
    operations = 0
    while n > 0:
        if n % 2 == 0:
            n //= 2
        elif n == 3 or n % 4 == 1:
            # Single trailing 1: subtract it
            n -= 1
        else:
            # Multiple trailing 1s: add 1 to merge them
            n += 1
        operations += 1
    return operations
```

---

## Pattern Blends

### Problem 6. LeetCode 401. Binary Watch
**Archetype:** 18.4 Bit Masking / 09.1 Backtracking
**Type:** Pattern Blend
**Statement:** Given the number of LEDs that are currently on in a binary watch, return all possible times the watch could represent.
**Why it fits:** This blends subset enumeration (bitmask) with backtracking. Each LED corresponds to a bit; turning on `n` LEDs means choosing `n` bits from 10 total (4 hours + 6 minutes).
**The Twist:** You must validate that the generated hour and minute values are valid (hour < 12, minute < 60). The naive approach generates all 2^10 combinations and filters by popcount.
**Code Skeleton:**
```python
def read_binary_watch(turned_on: int):
    result = []

    for h in range(12):
        for m in range(60):
            # Count total set bits in hour and minute combined
            if bin(h).count('1') + bin(m).count('1') == turned_on:
                result.append(f"{h}:{m:02d}")

    return result
```

---

### Problem 7. LeetCode 1125. Smallest Sufficient Team
**Archetype:** 18.4 Bit Masking / 14.1 DP
**Type:** Pattern Blend
**Statement:** Given a list of required skills and a list of people with their skills, return the smallest sufficient team of people that collectively cover all required skills.
**Why it fits:** This is a set cover problem solved with bitmask DP. Each person's skill set is a bitmask, and the DP state tracks which skills have been covered so far.
**The Twist:** You must also reconstruct the actual team members, not just the size. The DP tracks both the minimum size and the predecessor state for backtracking.
**Code Skeleton:**
```python
def smallest_sufficient_team(req_skills, people):
    n = len(req_skills)
    skill_id = {skill: i for i, skill in enumerate(req_skills)}
    target = (1 << n) - 1

    # Convert each person's skills to a bitmask
    person_masks = []
    for person in people:
        mask = 0
        for skill in person:
            if skill in skill_id:
                mask |= 1 << skill_id[skill]
        person_masks.append(mask)

    # dp[mask] = (team_size, last_person_added, previous_mask)
    dp = {0: (0, -1, 0)}

    for i, p_mask in enumerate(person_masks):
        if p_mask == 0:
            continue
        # Iterate over existing states to avoid double counting within same iteration
        for curr_mask in list(dp.keys()):
            new_mask = curr_mask | p_mask
            new_size = dp[curr_mask][0] + 1
            if new_mask not in dp or new_size < dp[new_mask][0]:
                dp[new_mask] = (new_size, i, curr_mask)

    # Backtrack to find team members
    team = []
    mask = target
    while mask != 0:
        _, person_idx, prev_mask = dp[mask]
        team.append(person_idx)
        mask = prev_mask

    return team
```

---

### Problem 8. LeetCode 1349. Maximum Students Taking Exam
**Archetype:** 18.4 Bit Masking / 14.2 DP
**Type:** Pattern Blend
**Statement:** Given a classroom matrix where broken seats are marked '#', place students in '.' seats such that no two adjacent students can cheat. Return the maximum number of students.
**Why it fits:** This is a classic bitmask DP on grid rows. Each valid row configuration is a bitmask with no adjacent 1s. Compatibility between consecutive rows requires no vertical or diagonal adjacency.
**The Twist:** You must precompute valid masks for each row (considering broken seats), then DP over rows where `dp[row][mask]` = max students up to this row with the given seating mask.
**Code Skeleton:**
```python
def max_students(seats):
    m = len(seats)
    n = len(seats[0])

    # Convert each row to a mask of available seats (1 = available)
    available = []
    for row in seats:
        mask = 0
        for j in range(n):
            if row[j] == '.':
                mask |= 1 << j
        available.append(mask)

    # Check if a mask has no adjacent 1s
    def valid(mask):
        return (mask & (mask << 1)) == 0

    # Precompute valid masks for each row
    valid_masks = []
    for i in range(m):
        masks = []
        for mask in range(1 << n):
            if valid(mask) and (mask & available[i]) == mask:
                masks.append(mask)
        valid_masks.append(masks)

    # dp[mask] = max students for previous row with this mask
    dp = {0: 0}

    for i in range(m):
        new_dp = {}
        for curr_mask in valid_masks[i]:
            curr_count = bin(curr_mask).count('1')
            best_prev = 0
            for prev_mask, prev_count in dp.items():
                # No vertical or diagonal adjacency
                if (curr_mask & prev_mask) == 0 and (curr_mask & (prev_mask << 1)) == 0 and (curr_mask & (prev_mask >> 1)) == 0:
                    best_prev = max(best_prev, prev_count)
            new_dp[curr_mask] = best_prev + curr_count
        dp = new_dp

    return max(dp.values(), default=0)
```

---

### Problem 9. LeetCode 1994. The Number of Good Subsets
**Archetype:** 18.4 Bit Masking / 17.1 Prime & Factors / 14.1 DP
**Type:** Pattern Blend
**Statement:** Given an array of positive integers, return the number of good subsets where the product of its elements has no prime factor with an exponent > 1.
**Why it fits:** This combines prime factorization with bitmask DP. Numbers 1-30 factor into primes <= 29 (10 primes). A subset is "good" if no two numbers share a prime factor, which is exactly a bitmask independence condition.
**The Twist:** The number 1 is special: it can appear any number of times and multiplies the count by `2^count(1)`. You must factor each number, check for square factors (which make it unusable), and then DP over prime bitmasks.
**Code Skeleton:**
```python
def number_of_good_subsets(nums):
    from collections import Counter
    count = Counter(nums)
    MOD = 10**9 + 7

    # Primes up to 30
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    # Factor each number 1-30 into a bitmask of its prime factors
    # -1 means the number has a squared prime factor (not usable)
    factor_mask = [0] * 31
    for num in range(2, 31):
        x = num
        mask = 0
        valid = True
        for i, p in enumerate(primes):
            if x % p == 0:
                x //= p
                if x % p == 0:
                    valid = False
                    break
                mask |= 1 << i
        if not valid:
            factor_mask[num] = -1
        else:
            factor_mask[num] = mask

    # dp[mask] = number of ways to form a subset with exactly these primes used
    dp = [0] * (1 << 10)
    dp[0] = 1

    for num in range(2, 31):
        mask = factor_mask[num]
        if mask == -1 or count[num] == 0:
            continue

        # Update dp in reverse to avoid using updated values within same iteration
        for curr_mask in range((1 << 10) - 1, -1, -1):
            if (curr_mask & mask) == 0:
                dp[curr_mask | mask] = (dp[curr_mask | mask] + dp[curr_mask] * count[num]) % MOD

    # Exclude the empty subset, then multiply by 2^count[1] for ones
    total = (sum(dp) - 1) % MOD
    total = total * pow(2, count[1], MOD) % MOD
    return total
```

---

### Problem 10. LeetCode 1066. Campus Bikes II
**Archetype:** 18.4 Bit Masking / 14.1 DP
**Type:** Pattern Blend
**Statement:** Given workers and bikes on a 2D grid, assign each worker a unique bike to minimize the sum of Manhattan distances.
**Why it fits:** This is the assignment problem solved with bitmask DP. The state `dp[mask]` represents the minimum cost to assign bikes (indicated by set bits in `mask`) to the first `k` workers where `k = popcount(mask)`.
**The Twist:** The brute-force approach is O(n!) permutations. The bitmask DP reduces this to O(n * 2^n) by assigning one bike at a time and using the bit count to determine which worker we're assigning.
**Code Skeleton:**
```python
def assign_bikes(workers, bikes):
    n = len(workers)
    m = len(bikes)

    def manhattan(w, b):
        return abs(workers[w][0] - bikes[b][0]) + abs(workers[w][1] - bikes[b][1])

    # dp[mask] = min distance to assign bikes in mask to first popcount(mask) workers
    INF = float('inf')
    dp = [INF] * (1 << m)
    dp[0] = 0

    for mask in range(1 << m):
        worker_idx = bin(mask).count('1')
        if worker_idx >= n:
            continue

        for bike_idx in range(m):
            if not (mask & (1 << bike_idx)):
                new_mask = mask | (1 << bike_idx)
                dp[new_mask] = min(dp[new_mask], dp[mask] + manhattan(worker_idx, bike_idx))

    # Find minimum among all states where n workers have bikes
    return min(dp[mask] for mask in range(1 << m) if bin(mask).count('1') == n)
```

---

## Interview Simulation

### Problem 11. LeetCode 1611. Minimum One Bit Operations to Make Integers Zero
**Archetype:** 18.5 Bitwise Operations / 18.6 Bit DP
**Type:** Interview Sim
**Statement:** Given an integer `n`, return the minimum number of operations to transform it into 0 using specific bit-flip rules.
**Why it fits:** This problem generates the Gray code sequence. The minimum operations to reduce `n` to 0 follows a recursive pattern related to the most significant bit.
**The Twist:** The recurrence is `f(n) = 2^(msb) - 1 - f(n ^ 2^(msb))`, where `msb` is the highest set bit. Recognizing the Gray code connection simplifies the derivation.
**Code Skeleton:**
```python
def minimum_one_bit_operations(n: int) -> int:
    if n == 0:
        return 0

    # Find the most significant bit
    msb = 1 << (n.bit_length() - 1)

    # Recurrence: f(n) = 2*msb - 1 - f(n ^ msb)
    return (2 * msb - 1) - minimum_one_bit_operations(n ^ msb)
```

---

### Problem 12. LeetCode 421. Maximum XOR of Two Numbers in an Array
**Archetype:** 18.3 XOR Properties / 18.4 Bit Masking
**Type:** Interview Sim
**Statement:** Given an integer array, return the maximum result of `nums[i] XOR nums[j]`.
**Why it fits:** This is a classic Trie + bit manipulation problem. You build a binary Trie of all numbers and for each number, greedily try to take the opposite bit at every level to maximize XOR.
**The Twist:** The greedy approach works because you process bits from most significant to least significant. A prefix-based hash set approach also works: for each bit position, check if there exist two prefixes with the opposite bit.
**Code Skeleton:**
```python
def find_maximum_xor(nums):
    # Trie node structure
    trie = {}

    def insert(num):
        node = trie
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            if bit not in node:
                node[bit] = {}
            node = node[bit]

    def query(num):
        node = trie
        xor = 0
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            opposite = 1 - bit
            if opposite in node:
                xor |= (1 << i)
                node = node[opposite]
            else:
                node = node[bit]
        return xor

    max_xor = 0
    for num in nums:
        insert(num)
        max_xor = max(max_xor, query(num))

    return max_xor
```

---

### Problem 13. LeetCode 1707. Maximum XOR With an Element From Array
**Archetype:** 18.3 XOR Properties / 18.4 Bit Masking
**Type:** Interview Sim
**Statement:** Given an array and queries `[xi, mi]`, return the maximum XOR of `xi` with any element in `nums` that is <= `mi`.
**Why it fits:** This extends the maximum XOR problem with an inequality constraint. Sorting both the array and queries offline allows you to build the Trie incrementally, only adding elements <= current `mi`.
**The Twist:** The offline processing is key. Sort `nums` and queries by their threshold (`mi`). As you process queries in increasing order of `mi`, insert eligible numbers into the Trie and answer each query.
**Code Skeleton:**
```python
def maximize_xor(nums, queries):
    nums.sort()
    # Sort queries by mi, keeping original indices
    sorted_queries = sorted((mi, xi, i) for i, (xi, mi) in enumerate(queries))

    # Trie node structure
    trie = {}

    def insert(num):
        node = trie
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            if bit not in node:
                node[bit] = {}
            node = node[bit]

    def query(num):
        if not trie:
            return -1
        node = trie
        xor = 0
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            opposite = 1 - bit
            if opposite in node:
                xor |= (1 << i)
                node = node[opposite]
            else:
                node = node[bit]
        return xor

    result = [-1] * len(queries)
    num_idx = 0

    for mi, xi, q_idx in sorted_queries:
        while num_idx < len(nums) and nums[num_idx] <= mi:
            insert(nums[num_idx])
            num_idx += 1
        result[q_idx] = query(xi)

    return result
```

---

### Problem 14. LeetCode 1178. Number of Valid Words for Each Puzzle
**Archetype:** 18.4 Bit Masking
**Type:** Interview Sim
**Statement:** Given a list of words and puzzles, for each puzzle count how many words are valid: the word contains the puzzle's first letter, and every letter in the word is in the puzzle.
**Why it fits:** This is a frequency map + bitmask problem. Each word and puzzle is converted to a 26-bit mask. A word is valid if its mask is a subset of the puzzle's mask and contains the first letter.
**The Twist:** The number of puzzles and words can be large (up to 10^5). Instead of checking each word against each puzzle, you enumerate all submasks of each puzzle's mask and look up their frequencies in a precomputed hash map.
**Code Skeleton:**
```python
from collections import Counter

def find_num_of_valid_words(words, puzzles):
    # Convert words to frequency map of bitmasks
    word_masks = Counter()
    for word in words:
        mask = 0
        for ch in set(word):
            mask |= 1 << (ord(ch) - ord('a'))
        word_masks[mask] += 1

    result = []
    for puzzle in puzzles:
        puzzle_mask = 0
        for ch in puzzle:
            puzzle_mask |= 1 << (ord(ch) - ord('a'))

        first_letter_mask = 1 << (ord(puzzle[0]) - ord('a'))

        # Enumerate all submasks of puzzle_mask that contain first_letter_mask
        submask = puzzle_mask
        count = 0
        while submask:
            if submask & first_letter_mask:
                count += word_masks.get(submask, 0)
            submask = (submask - 1) & puzzle_mask

        result.append(count)

    return result
```

---

### Problem 15. LeetCode 982. Triples with Bitwise AND Equal To Zero
**Archetype:** 18.4 Bit Masking / 18.5 Bitwise Operations
**Type:** Interview Sim
**Statement:** Given an integer array, return the number of triples `(i, j, k)` such that `nums[i] & nums[j] & nums[k] == 0`.
**Why it fits:** This combines bitmask enumeration with a meet-in-the-middle strategy. For each possible AND result of two numbers, count how many times it occurs, then for each third number count compatible pairs.
**The Twist:** Brute force is O(n^3). Precomputing all pair ANDs reduces to O(n^2 + n * 2^16) if numbers are bounded, or using a hash map for sparse cases. The key insight is that `a & b & c == 0` iff `(a & b) & c == 0`.
**Code Skeleton:**
```python
from collections import Counter

def count_triplets(nums):
    # If numbers are bounded by 2^16, we can use array counting
    # Otherwise, use a hash map for pair AND frequencies
    pair_and = Counter()

    for i in range(len(nums)):
        for j in range(len(nums)):
            pair_and[nums[i] & nums[j]] += 1

    count = 0
    for k in range(len(nums)):
        for and_val, freq in pair_and.items():
            if and_val & nums[k] == 0:
                count += freq

    return count
```
