# Pattern 18: Bit Manipulation

> **Pattern Recognition:** When you see "single number", "power of two", "XOR", "subset", "missing number", "hamming weight" — think bit manipulation.
>
> **Fundamental Insight:** Bit operations are O(1) and use minimal space. XOR, AND, OR, shifts, and masks can solve problems that seem to need hash maps or arrays.

---

## Archetype 18.1: Single Number

### Recognition Signal
Words: **"single number", "appears once", "others appear twice", "unique"**

### Key Property: XOR
- `a ^ a = 0`
- `a ^ 0 = a`
- XOR is commutative and associative

### Template
```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result
```

### Problems
- Single Number (LeetCode 136)
- Single Number II (LeetCode 137) — appears once, others 3 times
- Single Number III (LeetCode 260) — two single numbers

**Single Number II:**
```python
def single_number_ii(nums):
    ones = twos = 0
    for num in nums:
        ones = (ones ^ num) & ~twos
        twos = (twos ^ num) & ~ones
    return ones
```

---

## Archetype 18.2: Power of Two

### Recognition Signal
Words: **"power of two", "power of four", "power of three"**

### Key Property
- Power of 2: `n > 0 and (n & (n - 1)) == 0`
- Power of 4: Power of 2 AND `(n & 0x55555555) != 0` (bit in odd position)

### Problems
- Power of Two (LeetCode 231)
- Power of Three (LeetCode 326) — not bit manipulation, but math
- Power of Four (LeetCode 342)

---

## Archetype 18.3: XOR Properties

### Recognition Signal
Words: **"missing number", "find duplicate", "range XOR"**

### Template: Missing Number
```python
def missing_number(nums):
    n = len(nums)
    xor_all = 0
    for i in range(n + 1):
        xor_all ^= i
    for num in nums:
        xor_all ^= num
    return xor_all
```

### Problems
- Missing Number (LeetCode 268)
- Find the Duplicate Number (LeetCode 287) — Floyd's cycle, not XOR
- Find the Difference (LeetCode 389) — XOR all chars

---

## Archetype 18.4: Bit Masking

### Recognition Signal
Words: **"subsets", "mask", "bitmask", "state", "permutations"**

### Template: Generate Subsets with Mask
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

### Problems
- Subsets (LeetCode 78) — can use bitmask
- Maximum Product of Word Lengths (LeetCode 318)
- Partition to K Equal Sum Subsets (LeetCode 698) — bitmask DP

---

## Archetype 18.5: Bitwise Operations

### Recognition Signal
Words: **"reverse bits", "number of 1 bits", "hamming weight", "bitwise AND"**

### Problems
- Number of 1 Bits (LeetCode 191)
- Counting Bits (LeetCode 338)
- Reverse Bits (LeetCode 190)
- Bitwise AND of Numbers Range (LeetCode 201)
- Binary Number with Alternating Bits (LeetCode 693)

**Counting bits (DP):**
```python
def count_bits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

---

## Archetype 18.6: Bit DP

### Recognition Signal
Words: **"counting", "DP with bitmask", "state compression"**

### Problems
- Counting Bits (LeetCode 338)
- Concatenation of Consecutive Binary Numbers (LeetCode 1680)

---

## Mastery Checklist
- [ ] XOR properties: `a^a=0`, `a^0=a`
- [ ] Check power of 2: `n & (n-1) == 0`
- [ ] Count set bits: Brian Kernighan or lookup table
- [ ] Generate subsets with bitmask
- [ ] Reverse bits
- [ ] Missing number with XOR
- [ ] Hamming distance

---

## Common Bit Tricks

```python
# Check if bit i is set
x & (1 << i)

# Set bit i
x | (1 << i)

# Clear bit i
x & ~(1 << i)

# Toggle bit i
x ^ (1 << i)

# Get lowest set bit
x & (-x)

# Clear lowest set bit
x & (x - 1)

# Check if power of 2
x > 0 and (x & (x - 1)) == 0

# Swap without temp
a ^= b
b ^= a
a ^= b

# Get sign
-(x < 0)  # -1 if negative, 0 if non-negative
```

---

## Common Traps

**Trap:** Signed integer right shift fills with 1s for negative numbers.
- Fix: Use unsigned shift `>>>` (in Java/C++). In Python, ints are unbounded.

**Trap:** Overflow in bit operations.
- Fix: Python handles big ints, but be careful in other languages.

**Trap:** Confusing `&` (AND) with `&&` (logical AND).
- Fix: `&` is bitwise, `and` is logical.

**Near Miss: Gray Code**
- Generate sequence where adjacent differ by one bit
- `g = i ^ (i >> 1)`
