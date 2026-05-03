# Pattern 18: Bit Manipulation — Practice Problems

## Single Number

### 136. Single Number
**Statement:** Every element appears twice except one.
**Code:**
```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result
```

### 137. Single Number II
**Statement:** Every element appears three times except one.
**Code:**
```python
def single_number_ii(nums):
    ones = twos = 0
    for num in nums:
        ones = (ones ^ num) & ~twos
        twos = (twos ^ num) & ~ones
    return ones
```

### 260. Single Number III
**Statement:** Two elements appear once, others twice.
**Intuition:** XOR all to get a^b. Find any set bit. Partition by that bit. XOR each partition.

---

## Power of Two

### 231. Power of Two
**Statement:** Is n a power of two?
**Code:**
```python
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0
```

### 342. Power of Four
**Statement:** Is n a power of four?
**Code:**
```python
def is_power_of_four(n):
    return n > 0 and (n & (n - 1)) == 0 and (n & 0x55555555) != 0
```

---

## XOR Properties

### 268. Missing Number
**Statement:** Find missing number in [0, n].
**Code:**
```python
def missing_number(nums):
    n = len(nums)
    result = n
    for i, num in enumerate(nums):
        result ^= i ^ num
    return result
```

### 389. Find the Difference
**Statement:** Find letter added to t.
**Intuition:** XOR all chars in s and t.

---

## Bit Masking

### 78. Subsets (Bitmask version)
**Statement:** All subsets.
**Code:**
```python
def subsets(nums):
    n = len(nums)
    result = []
    for mask in range(1 << n):
        subset = [nums[i] for i in range(n) if mask & (1 << i)]
        result.append(subset)
    return result
```

### 318. Maximum Product of Word Lengths
**Statement:** Max product of lengths where words share no letters.
**Intuition:** Bitmask for each word's letters. Check `(mask1 & mask2) == 0`.

---

## Bitwise Operations

### 191. Number of 1 Bits
**Statement:** Count set bits.
**Code (Brian Kernighan):**
```python
def hamming_weight(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
```

### 338. Counting Bits
**Statement:** Count bits for all numbers 0 to n.
**Code:**
```python
def count_bits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

### 190. Reverse Bits
**Statement:** Reverse bits of unsigned integer.
**Code:**
```python
def reverse_bits(n):
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
```

### 201. Bitwise AND of Numbers Range
**Statement:** AND of all numbers in [m, n].
**Intuition:** Find common prefix. Right shift until equal.

---

## Mixed Drill Set

1. 136 — Single number
2. 268 — Missing number
3. 191 — Number of 1 bits
4. 231 — Power of two
5. 338 — Counting bits
6. 190 — Reverse bits
7. 137 — Single number II
8. 260 — Single number III
9. 389 — Find the difference
10. 201 — Bitwise AND range
11. 78 — Subsets (bitmask)
12. 342 — Power of four
