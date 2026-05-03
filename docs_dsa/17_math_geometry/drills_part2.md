# Pattern 17: Math & Geometry — Drills Part 2

> **Focus:** Warm-ups (5) + Core Drills (10)
>
> **Goal:** Build muscle memory for prime sieves, Euclidean GCD, fast power, matrix rotations, coordinate geometry, and game theory reasoning.

---

## Warm-Ups

### Problem 1. LeetCode 204. Count Primes
**Archetype:** 17.1 Prime & Factors
**Type:** Warm-Up
**Statement:** Count the number of prime numbers less than `n`.
**Why it fits:** This is the canonical Sieve of Eratosthenes implementation. It teaches the fundamental technique of marking multiples and is the foundation for nearly all prime-related number theory problems.
**The Twist:** Pure template. The optimization is to only sieve up to `sqrt(n)` and start marking from `i*i` rather than `2*i`.
**Code Skeleton:**
```python
def count_primes(n: int) -> int:
    if n <= 2:
        return 0

    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False

    # Only need to check up to sqrt(n)
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            # Mark multiples starting from i*i
            for j in range(i * i, n, i):
                is_prime[j] = False

    return sum(is_prime)
```

---

### Problem 2. LeetCode 231. Power of Two
**Archetype:** 17.3 Power/Modulo
**Type:** Warm-Up
**Statement:** Determine if an integer `n` is a power of two.
**Why it fits:** A power of two in binary has exactly one bit set. Using `n > 0 and (n & (n - 1)) == 0` is a classic bit-math property that every candidate should know.
**The Twist:** None — this is the bit-math identity. The edge case is `n <= 0`, which must return False.
**Code Skeleton:**
```python
def is_power_of_two(n: int) -> bool:
    # A power of two has exactly one bit set.
    # n & (n - 1) clears the lowest set bit.
    # If the result is 0 and n > 0, n was a power of two.
    return n > 0 and (n & (n - 1)) == 0
```

---

### Problem 3. LeetCode 50. Pow(x, n)
**Archetype:** 17.3 Power/Modulo
**Type:** Warm-Up
**Statement:** Implement `pow(x, n)`.
**Why it fits:** This is the canonical fast exponentiation (binary exponentiation) template. It reduces time complexity from O(n) to O(log n) by squaring the base and halving the exponent.
**The Twist:** Handle negative exponents by converting to positive and taking the reciprocal at the end. Use a loop, not recursion, to avoid stack overflow on large exponents.
**Code Skeleton:**
```python
def my_pow(x: float, n: int) -> float:
    if n < 0:
        x = 1 / x
        n = -n

    result = 1.0
    current_product = x

    while n > 0:
        # If the lowest bit of n is set, multiply result by current power of x
        if n % 2 == 1:
            result *= current_product
        current_product *= current_product
        n //= 2

    return result
```

---

### Problem 4. LeetCode 48. Rotate Image
**Archetype:** 17.5 Matrix Operations
**Type:** Warm-Up
**Statement:** Rotate a matrix 90 degrees clockwise in-place.
**Why it fits:** The canonical matrix rotation uses two steps: transpose (swap across diagonal) then reverse each row. This pattern appears in many matrix transformation problems.
**The Twist:** The rotation must be done in-place (O(1) extra space). Creating a new matrix is the obvious but wrong approach for the follow-up constraint.
**Code Skeleton:**
```python
def rotate(matrix):
    n = len(matrix)

    # Step 1: Transpose — swap matrix[i][j] with matrix[j][i]
    for i in range(n):
        for j in range(i, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

    # Step 2: Reverse each row
    for i in range(n):
        matrix[i].reverse()
```

---

### Problem 5. LeetCode 292. Nim Game
**Archetype:** 17.7 Game Theory
**Type:** Warm-Up
**Statement:** Given `n` stones, two players take turns removing 1-3 stones. Return True if you can win assuming optimal play.
**Why it fits:** This introduces the simplest form of combinatorial game theory: losing positions are multiples of 4 because whatever you take (1-3), the opponent can always complement to 4.
**The Twist:** The solution is a one-liner, but the reasoning requires understanding invariant states. Extending this to arbitrary move sizes is a common follow-up.
**Code Skeleton:**
```python
def can_win_nim(n: int) -> bool:
    # If n is a multiple of 4, you are in a losing position.
    # Whatever you take (1-3), opponent takes (4 - your_move) to stay on multiples of 4.
    return n % 4 != 0
```

---

## Core Drills

### Problem 6. LeetCode 263. Ugly Number
**Archetype:** 17.1 Prime & Factors
**Type:** Core Drill
**Statement:** Determine if a number is ugly (its only prime factors are 2, 3, and 5).
**Why it fits:** This teaches repeated division by a fixed set of primes. It is the iterative factor-stripping pattern used in more advanced factorization problems.
**The Twist:** The number could be 0 or negative, which must return False. The order of division does not matter, but you must divide out all occurrences of each factor.
**Code Skeleton:**
```python
def is_ugly(n: int) -> bool:
    if n <= 0:
        return False

    for prime in [2, 3, 5]:
        while n % prime == 0:
            n //= prime

    # If all prime factors were 2, 3, or 5, n should now be 1
    return n == 1
```

---

### Problem 7. LeetCode 264. Ugly Number II
**Archetype:** 17.1 Prime & Factors
**Type:** Core Drill
**Statement:** Find the `n`-th ugly number.
**Why it fits:** This uses a three-pointer / merge pattern similar to merging sorted lists. Each new ugly number is the minimum of `2*p2`, `3*p3`, `5*p5` where `p2`, `p3`, `p5` are previous ugly numbers.
**The Twist:** You must advance all pointers that generated the minimum value to avoid duplicates. This is essentially generating the union of three arithmetic sequences on the fly.
**Code Skeleton:**
```python
def nth_ugly_number(n: int) -> int:
    ugly = [1]
    p2 = p3 = p5 = 0

    for _ in range(1, n):
        next_ugly = min(ugly[p2] * 2, ugly[p3] * 3, ugly[p5] * 5)
        ugly.append(next_ugly)

        # Advance all pointers that produced this minimum to avoid duplicates
        if ugly[p2] * 2 == next_ugly:
            p2 += 1
        if ugly[p3] * 3 == next_ugly:
            p3 += 1
        if ugly[p5] * 5 == next_ugly:
            p5 += 1

    return ugly[-1]
```

---

### Problem 8. LeetCode 372. Super Pow
**Archetype:** 17.3 Power/Modulo
**Type:** Core Drill
**Statement:** Calculate `a^b mod 1337`, where `b` is a very large number given as an array of digits.
**Why it fits:** This extends fast power with modular arithmetic and the property that `a^b = (a^(b//10))^10 * a^(b%10)`. It combines math induction with the fast-power template.
**The Twist:** `b` is too large to convert to an integer. You must process it digit by digit, using the property that `pow(a, 10*x + d) = pow(pow(a, x), 10) * pow(a, d)`.
**Code Skeleton:**
```python
def super_pow(a: int, b):
    MOD = 1337

    def mod_pow(base, exp):
        # Fast power modulo MOD
        result = 1
        base %= MOD
        while exp > 0:
            if exp % 2 == 1:
                result = (result * base) % MOD
            base = (base * base) % MOD
            exp //= 2
        return result

    result = 1
    for digit in b:
        # result = result^10 * a^digit (mod MOD)
        result = mod_pow(result, 10) * mod_pow(a, digit) % MOD

    return result
```

---

### Problem 9. LeetCode 223. Rectangle Area
**Archetype:** 17.4 Coordinate Geometry
**Type:** Core Drill
**Statement:** Find the total area covered by two rectangles in the plane, counting overlaps once.
**Why it fits:** This is the 2D version of interval intersection. You compute each rectangle's area, sum them, and subtract the overlap area if the rectangles intersect.
**The Twist:** The rectangles may not overlap at all. The overlap width is `max(0, min(x2, x4) - max(x1, x3))`. If this is negative or zero, there is no overlap.
**Code Skeleton:**
```python
def compute_area(ax1: int, ay1: int, ax2: int, ay2: int,
                 bx1: int, by1: int, bx2: int, by2: int) -> int:
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)

    # Overlap dimensions
    overlap_width = max(0, min(ax2, bx2) - max(ax1, bx1))
    overlap_height = max(0, min(ay2, by2) - max(ay1, by1))
    overlap_area = overlap_width * overlap_height

    return area_a + area_b - overlap_area
```

---

### Problem 10. LeetCode 149. Max Points on a Line
**Archetype:** 17.2 GCD/LCM / 17.4 Coordinate Geometry
**Type:** Core Drill
**Statement:** Given an array of points, return the maximum number of points that lie on the same straight line.
**Why it fits:** This combines coordinate geometry with the Euclidean algorithm. To avoid floating-point errors, you represent slope as a reduced fraction `(dy/gcd, dx/gcd)` and use a hash map to count occurrences.
**The Twist:** Vertical lines have infinite slope; handle them with a sentinel value. Duplicate points must be counted separately and added to every slope group originating from that point.
**Code Skeleton:**
```python
from math import gcd
from collections import defaultdict

def max_points(points):
    if len(points) <= 2:
        return len(points)

    max_count = 0
    for i in range(len(points)):
        slopes = defaultdict(int)
        duplicates = 1  # Count the point itself
        x1, y1 = points[i]

        for j in range(i + 1, len(points)):
            x2, y2 = points[j]
            dx = x2 - x1
            dy = y2 - y1

            if dx == 0 and dy == 0:
                duplicates += 1
                continue

            # Reduce the slope fraction to its lowest terms
            g = gcd(dx, dy)
            dx //= g
            dy //= g

            # Normalize sign so that (-1, 2) and (1, -2) are the same slope
            if dx < 0:
                dx = -dx
                dy = -dy
            elif dx == 0:
                dy = 1  # Vertical line normalization

            slopes[(dx, dy)] += 1

        # Max points through points[i] = max slope count + duplicates
        current_max = max(slopes.values(), default=0) + duplicates
        max_count = max(max_count, current_max)

    return max_count
```

---

### Problem 11. LeetCode 54. Spiral Matrix
**Archetype:** 17.5 Matrix Operations
**Type:** Core Drill
**Statement:** Return all elements of a matrix in spiral order.
**Why it fits:** This tests boundary management in matrix traversal. You maintain four boundaries (top, bottom, left, right) and shrink them after traversing each layer.
**The Twist:** The matrix is not necessarily square. The loop termination condition must handle both even and odd dimensions correctly, and you must avoid double-visiting the center element in odd-dimension matrices.
**Code Skeleton:**
```python
def spiral_order(matrix):
    if not matrix or not matrix[0]:
        return []

    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        # Traverse right
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1

        # Traverse down
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1

        # Traverse left
        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1

        # Traverse up
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1

    return result
```

---

### Problem 12. LeetCode 384. Shuffle an Array
**Archetype:** 17.6 Randomized/Simulation
**Type:** Core Drill
**Statement:** Implement the Fisher-Yates shuffle to return a random permutation of the array.
**Why it fits:** This is the canonical unbiased shuffle algorithm. It guarantees that every permutation is equally likely by swapping each element with a randomly chosen element from the unshuffled suffix.
**The Twist:** The naive approach of swapping with any random index (including already-shuffled positions) is biased. You must only swap with indices `>= i` to maintain uniform probability.
**Code Skeleton:**
```python
import random

class Solution:
    def __init__(self, nums):
        self.original = nums[:]
        self.array = nums[:]

    def reset(self):
        self.array = self.original[:]
        return self.array

    def shuffle(self):
        n = len(self.array)
        for i in range(n):
            # Pick a random index from [i, n-1]
            j = random.randrange(i, n)
            self.array[i], self.array[j] = self.array[j], self.array[i]
        return self.array
```

---

### Problem 13. LeetCode 470. Implement Rand10() Using Rand7()
**Archetype:** 17.6 Randomized/Simulation
**Type:** Core Drill
**Statement:** Given `rand7()`, implement `rand10()` with uniform distribution.
**Why it fits:** This teaches rejection sampling. You create a larger uniform space (7x7 = 49) and reject values outside your target range (1-10), then map accepted values uniformly.
**The Twist:** Simply `rand7() % 10` is not uniform. You must generate a number in `[1, 49]`, reject 41-49, and map 1-40 to 1-10. This generalizes to any `randA() -> randB()` conversion.
**Code Skeleton:**
```python
import random

def rand7():
    return random.randint(1, 7)

def rand10():
    while True:
        # Generate a uniform number in [1, 49]
        row = rand7()
        col = rand7()
        num = (row - 1) * 7 + col

        # Reject 41-49; accept 1-40
        if num <= 40:
            # Map 1-40 uniformly to 1-10
            return (num - 1) % 10 + 1
```

---

### Problem 14. LeetCode 166. Fraction to Recurring Decimal
**Archetype:** 17.2 GCD/LCM
**Type:** Core Drill
**Statement:** Given two integers representing a fraction, return the string representation. If fractional part is repeating, enclose it in parentheses.
**Why it fits:** Long division simulation combined with a hash map to detect cycles. The GCD is used to simplify, and the hash map stores the index where each remainder first appears to know where to insert parentheses.
**The Twist:** Handle sign, integer overflow (use long), and the edge case where remainder becomes 0 (terminating decimal). The repeating part is detected when a remainder repeats.
**Code Skeleton:**
```python
def fraction_to_decimal(numerator: int, denominator: int) -> str:
    if numerator == 0:
        return "0"

    result = []
    # Determine sign
    if (numerator < 0) ^ (denominator < 0):
        result.append("-")

    num, den = abs(numerator), abs(denominator)

    # Integer part
    integer_part = num // den
    result.append(str(integer_part))

    remainder = num % den
    if remainder == 0:
        return "".join(result)

    result.append(".")

    # Map remainder -> index in result where it first appeared
    remainder_map = {}
    while remainder != 0:
        if remainder in remainder_map:
            # Insert opening parenthesis at the first occurrence index
            start_idx = remainder_map[remainder]
            result.insert(start_idx, "(")
            result.append(")")
            break

        remainder_map[remainder] = len(result)
        remainder *= 10
        result.append(str(remainder // den))
        remainder %= den

    return "".join(result)
```

---

### Problem 15. LeetCode 313. Super Ugly Number
**Archetype:** 17.1 Prime & Factors
**Type:** Core Drill
**Statement:** Find the `n`-th super ugly number given a list of primes.
**Why it fits:** This generalizes Ugly Number II from the fixed primes {2,3,5} to an arbitrary list. The multi-pointer merge pattern scales directly: one pointer per prime.
**The Twist:** The number of primes `k` can be up to 100, so you need an array of `k` pointers. The same duplicate-avoidance logic applies: advance every pointer that produced the minimum.
**Code Skeleton:**
```python
def nth_super_ugly_number(n: int, primes):
    ugly = [1]
    k = len(primes)
    pointers = [0] * k  # One pointer per prime

    for _ in range(1, n):
        # Find the next ugly number as the min of ugly[pointer[i]] * primes[i]
        next_ugly = min(ugly[pointers[i]] * primes[i] for i in range(k))
        ugly.append(next_ugly)

        # Advance all pointers that produced this minimum
        for i in range(k):
            if ugly[pointers[i]] * primes[i] == next_ugly:
                pointers[i] += 1

    return ugly[-1]
```
