# Pattern 18: Bit Manipulation — Drills Part 2

> **Focus:** Warm-ups (5) + Core Drills (10)
>
> **Goal:** Build muscle memory for XOR properties, power-of-two checks, bit masking, subset generation, and counting set bits.

---

## Warm-Ups

### Problem 1. LeetCode 136. Single Number
**Archetype:** 18.1 Single Number
**Type:** Warm-Up
**Statement:** Given an array where every element appears twice except one, find the single element.
**Why it fits:** This is the canonical XOR problem. The properties `a ^ a = 0` and `a ^ 0 = a` allow all pairs to cancel out, leaving the unique number.
**The Twist:** Pure template. The XOR approach is O(n) time and O(1) space, beating any hash-map solution on space complexity.
**Code Skeleton:**
```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result
```

---

### Problem 2. LeetCode 231. Power of Two
**Archetype:** 18.2 Power of Two
**Type:** Warm-Up
**Statement:** Determine if an integer `n` is a power of two.
**Why it fits:** This is the bit-math identity problem. A power of two has exactly one bit set, so `n > 0 and (n & (n - 1)) == 0` is both necessary and sufficient.
**The Twist:** None — this is the bit trick. The edge case is `n <= 0`, which must return False.
**Code Skeleton:**
```python
def is_power_of_two(n: int) -> bool:
    # A power of two has exactly one bit set.
    # n & (n - 1) clears the lowest set bit.
    # If the result is 0 and n > 0, n was a power of two.
    return n > 0 and (n & (n - 1)) == 0
```

---

### Problem 3. LeetCode 268. Missing Number
**Archetype:** 18.3 XOR Properties
**Type:** Warm-Up
**Statement:** Given an array containing `n` distinct numbers in range `[0, n]`, find the missing number.
**Why it fits:** This teaches the "range XOR" technique. XORing all indices and all values causes every present number to cancel, leaving only the missing number.
**The Twist:** The XOR solution avoids integer overflow issues that a sum-based approach might have in fixed-width languages. In Python this is less critical, but the XOR method is still elegant.
**Code Skeleton:**
```python
def missing_number(nums):
    n = len(nums)
    result = n  # XOR with n first since indices only go up to n-1

    for i in range(n):
        result ^= i ^ nums[i]

    return result
```

---

### Problem 4. LeetCode 191. Number of 1 Bits
**Archetype:** 18.5 Bitwise Operations
**Type:** Warm-Up
**Statement:** Return the number of '1' bits in the binary representation of an unsigned integer.
**Why it fits:** This is the canonical hamming weight / popcount problem. The Brian Kernighan algorithm (`n &= n - 1` clears the lowest set bit) counts bits in O(number of set bits).
**The Twist:** Pure template. The naive approach (checking each of 32 bits) is also acceptable but the Kernighan algorithm is faster for sparse numbers.
**Code Skeleton:**
```python
def hamming_weight(n: int) -> int:
    count = 0
    while n:
        n &= n - 1  # Clear the lowest set bit
        count += 1
    return count
```

---

### Problem 5. LeetCode 190. Reverse Bits
**Archetype:** 18.5 Bitwise Operations
**Type:** Warm-Up
**Statement:** Reverse the bits of a given 32-bit unsigned integer.
**Why it fits:** This teaches bit extraction and construction. For each bit in the input, you place it in the mirrored position in the output using shifts and OR.
**The Twist:** You must process exactly 32 bits. The loop runs 32 times regardless of the input value, and you shift the result left before adding each new bit.
**Code Skeleton:**
```python
def reverse_bits(n: int) -> int:
    result = 0
    for _ in range(32):
        # Shift result left to make room for the next bit
        result <<= 1
        # Extract the lowest bit of n and add it to result
        result |= n & 1
        # Shift n right to process the next bit
        n >>= 1
    return result
```

---

## Core Drills

### Problem 6. LeetCode 137. Single Number II
**Archetype:** 18.1 Single Number
**Type:** Core Drill
**Statement:** Given an array where every element appears three times except one, find the single element.
**Why it fits:** This extends the XOR pattern to a ternary counting system. Instead of one state (XOR), you need two states (`ones` and `twos`) to count occurrences modulo 3.
**The Twist:** The transition equations `ones = (ones ^ num) & ~twos` and `twos = (twos ^ num) & ~ones` are non-obvious. You must understand that a bit appears in `ones` if it has appeared once (mod 3) and not twice.
**Code Skeleton:**
```python
def single_number_ii(nums):
    ones = twos = 0
    for num in nums:
        # First appearance: add to ones, remove from twos
        # Second appearance: remove from ones, add to twos
        # Third appearance: remove from twos
        ones = (ones ^ num) & ~twos
        twos = (twos ^ num) & ~ones
    return ones
```

---

### Problem 7. LeetCode 260. Single Number III
**Archetype:** 18.1 Single Number
**Type:** Core Drill
**Statement:** Given an array where exactly two elements appear once and the rest appear twice, find those two elements.
**Why it fits:** This extends Single Number by using XOR to find the combined difference, then using the lowest set bit of that difference to partition the array into two groups, each containing one unique number.
**The Twist:** You cannot simply XOR everything because the two unique numbers do not cancel. You must find a bit where they differ (using `diff &= -diff`), then partition and XOR within each group.
**Code Skeleton:**
```python
def single_number_iii(nums):
    # XOR all numbers: result is a ^ b where a and b are the two unique numbers
    xor_all = 0
    for num in nums:
        xor_all ^= num

    # Get the lowest set bit of xor_all (a guaranteed differing bit)
    diff_bit = xor_all & (-xor_all)

    a = b = 0
    for num in nums:
        if num & diff_bit:
            a ^= num
        else:
            b ^= num

    return [a, b]
```

---

### Problem 8. LeetCode 342. Power of Four
**Archetype:** 18.2 Power of Two
**Type:** Core Drill
**Statement:** Determine if an integer `n` is a power of four.
**Why it fits:** This extends the power-of-two check. A power of four is also a power of two, but with the additional constraint that the single set bit must be in an odd position (1, 4, 16, 64...).
**The Twist:** The bitmask `0x55555555` (`10101010...` in binary) has 1s in all odd positions. Checking `(n & 0x55555555) != 0` confirms the bit is in an odd position.
**Code Skeleton:**
```python
def is_power_of_four(n: int) -> bool:
    # Must be positive, a power of two, and the set bit in an odd position
    return n > 0 and (n & (n - 1)) == 0 and (n & 0x55555555) != 0
```

---

### Problem 9. LeetCode 389. Find the Difference
**Archetype:** 18.3 XOR Properties
**Type:** Core Drill
**Statement:** Given two strings `s` and `t` where `t` is `s` with one extra character, find the extra character.
**Why it fits:** This applies XOR to character codes. XORing all characters in both strings causes every character from `s` to cancel with its counterpart in `t`, leaving only the extra character.
**The Twist:** You can also use a frequency map or sum difference, but XOR is O(n) time and O(1) space. The character codes are just integers, so XOR works seamlessly.
**Code Skeleton:**
```python
def find_the_difference(s: str, t: str) -> str:
    result = 0
    for ch in s:
        result ^= ord(ch)
    for ch in t:
        result ^= ord(ch)
    return chr(result)
```

---

### Problem 10. LeetCode 78. Subsets
**Archetype:** 18.4 Bit Masking
**Type:** Core Drill
**Statement:** Given an integer array of unique elements, return all possible subsets.
**Why it fits:** This is the canonical bitmask application. For `n` elements, there are `2^n` subsets, each representable by an `n`-bit mask where bit `i` indicates whether `nums[i]` is included.
**The Twist:** The iterative backtracking solution is more common, but the bitmask approach is O(2^n * n) and directly maps the combinatorial structure to bit operations.
**Code Skeleton:**
```python
def subsets(nums):
    n = len(nums)
    result = []

    for mask in range(1 << n):
        subset = []
        for i in range(n):
            if mask & (1 << i):
                subset.append(nums[i])
        result.append(subset)

    return result
```

---

### Problem 11. LeetCode 318. Maximum Product of Word Lengths
**Archetype:** 18.4 Bit Masking
**Type:** Core Drill
**Statement:** Given an array of words, find the maximum value of `length(word[i]) * length(word[j])` where the two words do not share common letters.
**Why it fits:** This applies bitmasking to character sets. Each word is converted to a 26-bit mask representing its letter set. Two words share no letters iff their masks AND to 0.
**The Twist:** You must precompute masks for all words. The brute-force O(n^2 * L) comparison becomes O(n^2) after precomputation, which is crucial for large inputs.
**Code Skeleton:**
```python
def max_product(words):
    n = len(words)
    masks = [0] * n
    lengths = [0] * n

    for i, word in enumerate(words):
        mask = 0
        for ch in word:
            mask |= 1 << (ord(ch) - ord('a'))
        masks[i] = mask
        lengths[i] = len(word)

    max_prod = 0
    for i in range(n):
        for j in range(i + 1, n):
            if masks[i] & masks[j] == 0:
                max_prod = max(max_prod, lengths[i] * lengths[j])

    return max_prod
```

---

### Problem 12. LeetCode 338. Counting Bits
**Archetype:** 18.6 Bit DP
**Type:** Core Drill
**Statement:** Given an integer `n`, return an array where `ans[i]` is the number of 1 bits in the binary representation of `i` for `0 <= i <= n`.
**Why it fits:** This is the canonical bit DP problem. The number of set bits in `i` relates to the number in `i >> 1` (divide by 2) plus the least significant bit `i & 1`.
**The Twist:** The DP relation `dp[i] = dp[i >> 1] + (i & 1)` allows O(n) computation. The naive approach of calling `bin(i).count('1')` for each `i` is O(n log n).
**Code Skeleton:**
```python
def count_bits(n: int):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

---

### Problem 13. LeetCode 201. Bitwise AND of Numbers Range
**Archetype:** 18.5 Bitwise Operations
**Type:** Core Drill
**Statement:** Given two integers `left` and `right`, return the bitwise AND of all numbers in the inclusive range.
**Why it fits:** This tests understanding of how bits change across a range. The AND of a range keeps only the common prefix of `left` and `right`; all lower bits must have flipped from 0 to 1 somewhere in the range.
**The Twist:** Right-shifting both numbers until they are equal finds the common prefix. Then shift back left. This is equivalent to finding the highest bit where they differ.
**Code Skeleton:**
```python
def range_bitwise_and(left: int, right: int) -> int:
    shift = 0
    # Right-shift both until they are equal (find common prefix)
    while left < right:
        left >>= 1
        right >>= 1
        shift += 1

    # Shift back to reconstruct the common prefix with trailing zeros
    return left << shift
```

---

### Problem 14. LeetCode 693. Binary Number with Alternating Bits
**Archetype:** 18.5 Bitwise Operations
**Type:** Core Drill
**Statement:** Determine if a positive integer has alternating bits in its binary representation.
**Why it fits:** This tests bit-pattern recognition. If bits alternate, `n ^ (n >> 1)` produces all 1s (e.g., `1010 ^ 0101 = 1111`). Then you check if that result is of the form `2^k - 1`.
**The Twist:** Alternatively, `n & (n >> 1) == 0` checks that no two adjacent bits are both 1, but you also need `n & (n >> 2) == n >> 2` to ensure they actually alternate rather than having gaps.
**Code Skeleton:**
```python
def has_alternating_bits(n: int) -> bool:
    # XOR of n and n>>1 should be all 1s if bits alternate
    # e.g., 1010 ^ 0101 = 1111
    x = n ^ (n >> 1)
    # Check if x is of the form 2^k - 1 (all bits set)
    return (x & (x + 1)) == 0
```

---

### Problem 15. LeetCode 1680. Concatenation of Consecutive Binary Numbers
**Archetype:** 18.6 Bit DP
**Type:** Core Drill
**Statement:** Given `n`, return the decimal value of the binary string formed by concatenating `1` to `n` in binary, modulo `10^9 + 7`.
**Why it fits:** This combines bit-length tracking with modular arithmetic. To concatenate `curr` after `prev`, you shift `prev` left by the bit-length of `curr` and OR with `curr`.
**The Twist:** Direct string concatenation is O(n^2) in bit length. The math approach tracks the length of the current number in bits and uses modular arithmetic to avoid overflow.
**Code Skeleton:**
```python
def concatenated_binary(n: int) -> int:
    MOD = 10**9 + 7
    result = 0
    length = 0  # Bit length of current number

    for i in range(1, n + 1):
        # When i is a power of two, its bit length increases by 1
        if i & (i - 1) == 0:
            length += 1

        # Shift result left by 'length' bits and add i
        result = ((result << length) | i) % MOD

    return result
```
