# Pattern 18: Bit Manipulation — Complete Archetype Map

> **Pattern Recognition:** When you see "single number", "power of two", "XOR", "bitmask", "state compression", "count bits", "bitwise AND/OR" — think bit-level operations.
>
> **Fundamental Insight:** Bits are the fundamental unit of computation. XOR cancels duplicates, bitmasks compactly represent subsets, shifts multiply/divide by powers of two, and bitwise operations are O(1). When you see integers and state spaces of size 2^n, bits are usually the answer.

---

## Archetype 18.1: Single Number

### Recognition Signal (10 seconds)
Words: **"single number", "appears once", "others appear twice", "find unique", "only one"**

The question: **"Find the element that appears exactly once when all others appear twice (or some known multiple)."**

### Core Structure
```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result
```

### The Invariant
`a ^ a = 0` and `a ^ 0 = a`. XOR is commutative and associative. After XOR-ing all elements, pairs cancel out to 0, leaving only the unique element.

### Canonical Problem: Single Number (LeetCode 136)
**Statement:** Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one.

```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result
```

### Variation Family

**V1: Single Number II (LeetCode 137)**
- **Twist:** Every element appears three times except one. Find the single one.
- **Change:** Count bits. For each bit position, sum all numbers. If sum % 3 != 0, that bit belongs to the single number.
- **Key insight:** Bits of the unique number are the ones where total count is not divisible by 3.

```python
def single_number_ii(nums):
    result = 0
    for i in range(32):
        bit_sum = 0
        for num in nums:
            if (num >> i) & 1:
                bit_sum += 1
        if bit_sum % 3 != 0:
            result |= (1 << i)
    # Handle negative numbers in two's complement context
    if result >= 2**31:
        result -= 2**32
    return result
```

**V2: Single Number III (LeetCode 260)**
- **Twist:** Exactly two elements appear once, all others appear twice. Find both.
- **Change:** XOR all to get `a ^ b`. Find any set bit in this result. Partition array by this bit. XOR each partition separately.
- **Key insight:** `a` and `b` differ in at least one bit. Partitioning by that bit isolates them.

```python
def single_number_iii(nums):
    xor_all = 0
    for num in nums:
        xor_all ^= num
    
    # Find rightmost set bit
    diff_bit = xor_all & (-xor_all)
    
    a = b = 0
    for num in nums:
        if num & diff_bit:
            a ^= num
        else:
            b ^= num
    
    return [a, b]
```

**V3: Missing Number (LeetCode 268)**
- **Twist:** Array contains n distinct numbers from [0, n]. Find the missing one.
- **Change:** XOR all indices and all values.
- **Key insight:** XORing index with value cancels all present numbers, leaving the missing one.

```python
def missing_number(nums):
    n = len(nums)
    result = n
    for i in range(n):
        result ^= i ^ nums[i]
    return result
```

**V4: Set Mismatch (LeetCode 645)**
- **Twist:** One number is duplicated, one is missing. Find both.
- **Change:** Math approach or XOR. `dup - missing = sum(nums) - sum(1..n)`.
- **Key insight:** Two equations with two unknowns solve the problem efficiently.

**Near Miss: Contains Duplicate (LeetCode 217)**
- **Looks like:** Single number variant
- **But:** Just need to detect any duplicate. Hash set is simpler and more general.
- **Lesson:** XOR only works for integers and specific frequency patterns. Do not force bit manipulation where hashing is cleaner.

---

## Archetype 18.2: Power of Two

### Recognition Signal (10 seconds)
Words: **"power of two", "power of four", "exactly one bit set", "n & (n-1)", "is power of"**

The question: **"Determine if a number is a power of 2, 3, 4, etc., often with bit tricks."**

### Core Structure
```python
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0
```

### The Invariant
A power of two in binary has exactly one bit set (e.g., `8 = 1000`). Subtracting 1 flips all bits from the rightmost 1 to the end (e.g., `7 = 0111`). AND of `n` and `n-1` clears the lowest set bit. If the result is 0 and `n > 0`, exactly one bit was set.

### Canonical Problem: Power of Two (LeetCode 231)
**Statement:** Given an integer `n`, return `true` if it is a power of two. Otherwise, return `false`.

```python
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0
```

### Variation Family

**V1: Power of Three (LeetCode 326)**
- **Twist:** Is n a power of three?
- **Change:** Loop divide by 3, or use `3^19 % n == 0` for 32-bit integers.
- **Key insight:** No bit trick for power of 3 because 3 is not a power of 2.

```python
def is_power_of_three(n):
    if n <= 0:
        return False
    while n % 3 == 0:
        n //= 3
    return n == 1
```

**V2: Power of Four (LeetCode 342)**
- **Twist:** Is n a power of four?
- **Change:** Must be power of two AND the set bit must be in an odd position.
- **Key insight:** `0x55555555 = 01010101...` in binary. Mask with this to check odd positions.

```python
def is_power_of_four(n):
    return n > 0 and (n & (n - 1)) == 0 and (n & 0x55555555) != 0
```

**V3: Binary Number with Alternating Bits (LeetCode 693)**
- **Twist:** Check if binary representation has alternating bits (e.g., `1010`)
- **Change:** `n ^ (n >> 1)` should be all 1s. Then check if adding 1 gives power of two.
- **Key insight:** `1010 ^ 0101 = 1111`. All 1s means alternating bits.

**V4: Prime Number of Set Bits in Binary Representation (LeetCode 762)**
- **Twist:** Count numbers in range [L, R] where number of 1 bits is prime.
- **Change:** Count bits for each number. Check against small prime set.
- **Key insight:** For 32-bit integers, max set bits is 32. Only small primes needed.

**Near Miss: Pow(x, n) (LeetCode 50)**
- **Looks like:** Power
- **But:** Fast exponentiation algorithm, not bit property check.
- **Lesson:** "Power of two" is a property check (bit trick); "compute power" is an arithmetic algorithm.

---

## Archetype 18.3: XOR Properties

### Recognition Signal (10 seconds)
Words: **"missing number", "find duplicate", "XOR", "all numbers from 0 to n", "pairwise", "even/odd occurrences"**

The question: **"Use XOR properties to find missing, duplicate, or paired elements efficiently."**

### Core Structure
```python
def xor_properties(nums):
    result = len(nums)
    for i, num in enumerate(nums):
        result ^= i ^ num
    return result
```

### The Invariant
XOR has four critical properties: `a ^ a = 0`, `a ^ 0 = a`, commutative, associative. When paired with indices, `i ^ nums[i]` cancels all matched pairs, leaving only mismatched elements.

### Canonical Problem: Missing Number (LeetCode 268)
**Statement:** Given an array `nums` containing `n` distinct numbers in the range `[0, n]`, return the only number in the range that is missing from the array.

```python
def missing_number(nums):
    n = len(nums)
    result = n
    for i in range(n):
        result ^= i ^ nums[i]
    return result
```

### Variation Family

**V1: Single Number II (LeetCode 137)**
- **Twist:** Already covered in Archetype 18.1. Bit counting for triple occurrences.
- **Change:** Alternative: use two variables `ones` and `twos` to track bits seen once and twice.
- **Key insight:** State machine with bits. `ones` holds bits seen exactly once; `twos` holds bits seen exactly twice.

```python
def single_number_ii_circuit(nums):
    ones = twos = 0
    for num in nums:
        ones = (ones ^ num) & ~twos
        twos = (twos ^ num) & ~ones
    return ones
```

**V2: Single Number III (LeetCode 260)**
- **Twist:** Already covered in Archetype 18.1. Two single numbers.
- **Change:** Partition by rightmost set bit of `a ^ b`.
- **Key insight:** XOR properties isolate differences between the two unique numbers.

**V3: Reverse Bits (LeetCode 190)**
- **Twist:** Reverse bits of a given 32-bit unsigned integer.
- **Change:** Iterate 32 times. Shift result left, add LSB of n, shift n right.
- **Key insight:** Bit-by-bit reconstruction. Mask and shift.

```python
def reverse_bits(n):
    result = 0
    for i in range(32):
        result <<= 1
        result |= n & 1
        n >>= 1
    return result
```

**V4: XOR Queries of a Subarray (LeetCode 1310)**
- **Twist:** Answer multiple queries of XOR over subarrays efficiently.
- **Change:** Prefix XOR array. `xor[i..j] = prefix[j+1] ^ prefix[i]`.
- **Key insight:** XOR prefix array works exactly like sum prefix array because XOR is its own inverse.

```python
def xor_queries(arr, queries):
    prefix = [0] * (len(arr) + 1)
    for i in range(len(arr)):
        prefix[i + 1] = prefix[i] ^ arr[i]
    
    result = []
    for left, right in queries:
        result.append(prefix[right + 1] ^ prefix[left])
    return result
```

**Near Miss: Single Number (LeetCode 136)**
- **Looks like:** XOR properties
- **But:** The simplest XOR application. This archetype covers more advanced uses.
- **Lesson:** Build from simple XOR cancelation to prefix XOR and bit-level state machines.

---

## Archetype 18.4: Bit Masking

### Recognition Signal (10 seconds)
Words: **"bitmask", "state compression", "subset", "assign", "can I win", "used", "taken", "state dp"**

The question: **"Represent a subset of items as bits in an integer to enable O(1) subset operations and memoization."**

### Core Structure
```python
def can_i_win(max_choosable, desired_total):
    memo = {}
    
    def dfs(mask, current_total):
        if mask in memo:
            return memo[mask]
        
        for i in range(max_choosable):
            if not (mask & (1 << i)):
                if current_total + i + 1 >= desired_total or not dfs(mask | (1 << i), current_total + i + 1):
                    memo[mask] = True
                    return True
        
        memo[mask] = False
        return False
    
    if max_choosable * (max_choosable + 1) // 2 < desired_total:
        return False
    return dfs(0, 0)
```

### The Invariant
Each bit in the mask represents whether a particular item has been used. With n <= 20, the state space 2^n is tractable with memoization. The mask compactly encodes the entire game state.

### Canonical Problem: Can I Win (LeetCode 464)
**Statement:** In the "100 game" two players take turns adding integers 1 to `maxChoosableInteger` to a running total. The first player who causes the total to reach or exceed `desiredTotal` wins. Return `true` if the first player can force a win.

```python
def can_i_win(max_choosable_integer, desired_total):
    total_sum = max_choosable_integer * (max_choosable_integer + 1) // 2
    if total_sum < desired_total:
        return False
    
    memo = {}
    
    def can_win(mask, current_total):
        if mask in memo:
            return memo[mask]
        
        for i in range(max_choosable_integer):
            bit = 1 << i
            if not (mask & bit):
                if current_total + i + 1 >= desired_total or not can_win(mask | bit, current_total + i + 1):
                    memo[mask] = True
                    return True
        
        memo[mask] = False
        return False
    
    return can_win(0, 0)
```

### Variation Family

**V1: Beautiful Arrangement (LeetCode 526)**
- **Twist:** Count permutations of 1..n where number at position i is divisible by i or vice versa.
- **Change:** Backtracking with bitmask to track used numbers.
- **Key insight:** n <= 15 makes bitmask memoization feasible. State = which numbers are placed.

```python
def count_arrangement(n):
    memo = {}
    
    def dfs(mask, pos):
        if pos > n:
            return 1
        if mask in memo:
            return memo[mask]
        
        count = 0
        for num in range(1, n + 1):
            if not (mask & (1 << num)) and (num % pos == 0 or pos % num == 0):
                count += dfs(mask | (1 << num), pos + 1)
        
        memo[mask] = count
        return count
    
    return dfs(0, 1)
```

**V2: Smallest Sufficient Team (LeetCode 1125)**
- **Twist:** Given required skills and people with skill sets, find smallest sufficient team.
- **Change:** Bitmask represents skill set. DP over people.
- **Key insight:** Map each skill to a bit. Each person's skills become a bitmask.

**V3: Maximum Students Taking Exam (LeetCode 1349)**
- **Twist:** Seating arrangement where no two students are adjacent (including diagonally). Maximize students.
- **Change:** Bitmask DP row by row.
- **Key insight:** Each row's valid seating is a bitmask with no adjacent bits. Check compatibility with previous row.

**V4: Number of Ways to Wear Different Hats to Each Other (LeetCode 1434)**
- **Twist:** Assign hats to people. Each person has a list of preferred hats. Count valid assignments.
- **Change:** DP over hats. `dp[mask]` = ways to assign hats to people represented by mask.
- **Key insight:** Process hats one by one. For each hat, try giving it to any eligible person.

**Near Miss: Subsets (LeetCode 78)**
- **Looks like:** Bitmask
- **But:** Generating all subsets with bitmask is possible, but backtracking is more common.
- **Lesson:** Bitmask shines when you need to memoize states or perform DP over subsets, not just enumerate them.

---

## Archetype 18.5: Bitwise Operations

### Recognition Signal (10 seconds)
Words: **"count bits", "number of 1 bits", "hamming weight", "range AND", "bitwise AND", "population count"**

The question: **"Count set bits, find common bits across a range, or perform arithmetic using only bitwise ops."**

### Core Structure
```python
def count_bits(n):
    result = [0] * (n + 1)
    for i in range(1, n + 1):
        result[i] = result[i >> 1] + (i & 1)
    return result
```

### The Invariant
The number of 1 bits in `i` equals the number of 1 bits in `i >> 1` plus the least significant bit of `i`. This DP relation computes all popcounts in O(n) time.

### Canonical Problem: Counting Bits (LeetCode 338)
**Statement:** Given an integer `n`, return an array `ans` of length `n + 1` such that for each `i` (`0 <= i <= n`), `ans[i]` is the number of 1's in the binary representation of `i`.

```python
def count_bits(n):
    result = [0] * (n + 1)
    for i in range(1, n + 1):
        result[i] = result[i >> 1] + (i & 1)
    return result
```

### Variation Family

**V1: Number of 1 Bits (LeetCode 191)**
- **Twist:** Count number of 1 bits in a single unsigned integer.
- **Change:** Brian Kernighan's algorithm: `n &= n - 1` clears the lowest set bit. Count iterations.
- **Key insight:** Each iteration of `n &= n - 1` removes exactly one set bit.

```python
def hamming_weight(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
```

**V2: Bitwise AND of Numbers Range (LeetCode 201)**
- **Twist:** Compute bitwise AND of all numbers in range [left, right].
- **Change:** Find common prefix of left and right in binary. Right-shift until equal, then shift back.
- **Key insight:** Once numbers differ at a bit position, all lower bits will vary across the range, producing 0 in those positions.

```python
def range_bitwise_and(left, right):
    shift = 0
    while left < right:
        left >>= 1
        right >>= 1
        shift += 1
    return left << shift
```

**V3: Sum of Two Integers (LeetCode 371)**
- **Twist:** Calculate sum of two integers without using + or - operators.
- **Change:** XOR for sum without carry, AND + left shift for carry. Repeat until no carry.
- **Key insight:** `a ^ b` gives sum without carry. `(a & b) << 1` gives the carry bits.

```python
def get_sum(a, b):
    # 32-bit mask in hexadecimal
    mask = 0xFFFFFFFF
    while b != 0:
        carry = (a & b) << 1
        a = (a ^ b) & mask
        b = carry & mask
    
    # If a is negative in 32-bit, convert to Python negative
    if a > 0x7FFFFFFF:
        a = ~(a ^ mask)
    return a
```

**V4: Divide Two Integers (LeetCode 29)**
- **Twist:** Divide two integers without using multiplication, division, or mod operators.
- **Change:** Binary long division. Subtract largest possible multiples (using bit shifts) of divisor from dividend.
- **Key insight:** `divisor << k` is the largest value <= remaining dividend. Accumulate `1 << k` into quotient.

```python
def divide(dividend, divisor):
    # Handle overflow edge case
    if dividend == -2**31 and divisor == -1:
        return 2**31 - 1
    
    negative = (dividend < 0) != (divisor < 0)
    dvd, dvs = abs(dividend), abs(divisor)
    quotient = 0
    
    while dvd >= dvs:
        temp = dvs
        multiple = 1
        while dvd >= (temp << 1):
            temp <<= 1
            multiple <<= 1
        dvd -= temp
        quotient += multiple
    
    return -quotient if negative else quotient
```

**Near Miss: Hamming Distance (LeetCode 461)**
- **Looks like:** Bitwise operations
- **But:** Simply XOR then count bits. Very straightforward.
- **Lesson:** Hamming distance is a direct application of XOR + popcount, not a standalone archetype.

---

## Archetype 18.6: Bit DP

### Recognition Signal (10 seconds)
Words: **"minimum number of work sessions", "assign tasks", "state compression dp", "bitmask dp", "subset dp"**

The question: **"Assign tasks to workers or sessions where n is small (<= 15-20). Use bitmask to represent which tasks are done."**

### Core Structure
```python
def bit_dp(tasks, session_time):
    n = len(tasks)
    dp = [float('inf')] * (1 << n)
    dp[0] = 0
    
    for mask in range(1 << n):
        if dp[mask] == float('inf'):
            continue
        # Try adding each unused task
        for i in range(n):
            if not (mask & (1 << i)):
                new_mask = mask | (1 << i)
                # Update dp[new_mask] based on problem constraints
                dp[new_mask] = min(dp[new_mask], dp[mask] + cost)
    
    return dp[(1 << n) - 1]
```

### The Invariant
`dp[mask]` represents the optimal answer for the subset of tasks represented by `mask`. We build up solutions from smaller subsets to larger subsets. Each bit transition corresponds to adding one task to the current state.

### Canonical Problem: Minimum Number of Work Sessions to Finish the Tasks (LeetCode 1986)
**Statement:** There are `n` tasks assigned to you. The task times are represented as an integer array `tasks`. Each session has a duration of `sessionTime`. Return the minimum number of work sessions needed to finish all tasks.

```python
def min_sessions(tasks, session_time):
    n = len(tasks)
    # valid[mask] = True if tasks in mask can fit in one session
    valid = [False] * (1 << n)
    
    for mask in range(1 << n):
        total = 0
        for i in range(n):
            if mask & (1 << i):
                total += tasks[i]
        valid[mask] = total <= session_time
    
    # dp[mask] = minimum sessions to complete tasks in mask
    dp = [float('inf')] * (1 << n)
    dp[0] = 0
    
    for mask in range(1 << n):
        if dp[mask] == float('inf'):
            continue
        # Try all submasks of remaining tasks that form a valid session
        remaining = ((1 << n) - 1) ^ mask
        submask = remaining
        while submask:
            if valid[submask]:
                new_mask = mask | submask
                dp[new_mask] = min(dp[new_mask], dp[mask] + 1)
            submask = (submask - 1) & remaining
    
    return dp[(1 << n) - 1]
```

### Variation Family

**V1: Smallest Sufficient Team (LeetCode 1125)**
- **Twist:** Find smallest team covering all required skills.
- **Change:** `dp[mask]` = minimum team size to cover skill mask. For each person, update masks.
- **Key insight:** Process people one by one. Each person contributes a skill bitmask.

```python
def smallest_sufficient_team(req_skills, people):
    skill_index = {skill: i for i, skill in enumerate(req_skills)}
    n = len(req_skills)
    target = (1 << n) - 1
    
    # Convert each person's skills to bitmask
    person_masks = []
    for person in people:
        mask = 0
        for skill in person:
            if skill in skill_index:
                mask |= 1 << skill_index[skill]
        person_masks.append(mask)
    
    dp = {0: []}
    for i, p_mask in enumerate(person_masks):
        if p_mask == 0:
            continue
        # Iterate over a snapshot of current dp keys
        for mask, team in list(dp.items()):
            new_mask = mask | p_mask
            if new_mask not in dp or len(dp[new_mask]) > len(team) + 1:
                dp[new_mask] = team + [i]
    
    return dp[target]
```

**V2: Find the Shortest Superstring (LeetCode 943)**
- **Twist:** Given an array of strings, find the shortest string that contains each string as a substring.
- **Change:** TSP-style DP. `dp[mask][i]` = shortest superstring covering mask and ending with string i.
- **Key insight:** Precompute overlap between every pair of strings. DP over subsets tries all orderings.

**V3: Campus Bikes II (LeetCode 1066)**
- **Twist:** Assign bikes to workers to minimize sum of Manhattan distances. Each worker gets one bike.
- **Change:** `dp[mask]` = minimum cost where mask represents which bikes are used.
- **Key insight:** Workers are processed in order. The mask tracks which bikes are taken.

**V4: Stickers to Spell Word (LeetCode 691)**
- **Twist:** Given stickers with letters, form target word. Minimize stickers used.
- **Change:** BFS or DP over mask of formed characters in target.
- **Key insight:** State is which characters of target are already covered. Each sticker transitions the state.

**Near Miss: Partition Equal Subset Sum (LeetCode 416)**
- **Looks like:** Bit DP
- **But:** Classic 0/1 knapsack with boolean array. No need for exponential state space.
- **Lesson:** Bit DP is for n <= 20 where 2^n is manageable. For larger n, use polynomial DP or other techniques.

---

## Pattern 18 Mastery Checklist

Before moving beyond Pattern 18, confirm you can:

- [ ] Single Number: write XOR solution in 10 seconds
- [ ] Power of Two: explain `n & (n-1)` trick and power of four mask
- [ ] XOR Properties: use prefix XOR for range queries and duplicate detection
- [ ] Bit Masking: represent subsets as integers and write memoized DFS
- [ ] Bitwise Operations: implement Brian Kernighan's popcount and binary addition
- [ ] Bit DP: write `dp[mask]` recurrence for n <= 15 problems
- [ ] Handle negatives: manage two's complement for 32-bit integers in Python
- [ ] Distinguish: when XOR works vs when hash map is better
- [ ] Space optimize: recognize when bit DP can be replaced by polynomial DP

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Using XOR on non-integer data | TypeError or wrong logic | XOR only works on integers. Use hash maps for strings/objects. |
| Not handling negative numbers in bit shifts | Infinite loop or wrong sign | In Python, integers are arbitrary precision. Mask to 32 bits when needed. |
| Wrong bitmask size | Index out of range or wrong state | Use `1 << n` for n items. Verify n <= 20 for tractability. |
| Forgetting to check n > 0 in power of two | Returns True for 0 | Always check `n > 0` before `(n & (n-1)) == 0` |
| O(2^n) bit DP on n = 25 | TLE or memory error | Bit DP is only for n <= 20-22. For larger n, find polynomial alternatives. |
| Using `&` instead of `&&` / mixing bitwise and logical ops | Wrong boolean logic | In Python, `&` is bitwise AND, `and` is logical. Use correctly. |

---

## Pattern Blends (What Comes Next)

Bit Manipulation does not live in isolation. It blends with:

- **Arrays & Hashing:** Single number can be solved with hash map; choose based on constraints
- **Math:** Fast exponentiation, GCD/LCM, number theory all use bit-level optimizations
- **DP:** Bitmask DP (state compression) combines bits with dynamic programming
- **Backtracking:** Beautiful arrangement uses bitmask to track used elements in DFS
- **Geometry:** Coordinate compression, grid representations sometimes use bitmasks

---

*End of DSA Pattern Archetypes*
