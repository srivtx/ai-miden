# Pattern 17: Math & Geometry — Drills Part 3

> **Focus:** Near Misses (5) + Pattern Blends (5) + Interview Simulation (5)
>
> **Goal:** Train pattern recognition under disguise, cross-pattern synthesis, and full interview-ready problem solving.

---

## Near Misses

### Problem 1. LeetCode 326. Power of Three
**Archetype:** 17.3 Power/Modulo
**Type:** Near Miss
**Statement:** Determine if an integer `n` is a power of three.
**Why it fits:** It looks like Power of Two, but the bit trick does not apply because 3 is not a power of 2. You must use loop division, logarithms with precision checks, or the max-power-of-three modulo trick.
**The Twist:** The elegant solution leverages the fact that `3^19 = 1162261467` is the max power of 3 in a 32-bit signed int. If `n > 0` and `1162261467 % n == 0`, then `n` is a power of three.
**Code Skeleton:**
```python
def is_power_of_three(n: int) -> bool:
    # 3^19 is the largest power of 3 that fits in a 32-bit signed integer
    MAX_POWER_OF_3 = 1162261467
    return n > 0 and MAX_POWER_OF_3 % n == 0
```

---

### Problem 2. LeetCode 593. Valid Square
**Archetype:** 17.4 Coordinate Geometry
**Type:** Near Miss
**Statement:** Given four points, determine if they form a valid square.
**Why it fits:** This tests geometric reasoning rather than formulas. A square has exactly two distinct distances: side length and diagonal length (where diagonal = side * sqrt(2)).
**The Twist:** You must compute all 6 pairwise distances and check that there are exactly 2 unique values, with the smaller appearing 4 times (sides) and the larger appearing 2 times (diagonals). Also, the side length must be non-zero.
**Code Skeleton:**
```python
def valid_square(p1, p2, p3, p4) -> bool:
    def dist_sq(a, b):
        return (a[0] - b[0])**2 + (a[1] - b[1])**2

    points = [p1, p2, p3, p4]
    distances = []

    for i in range(4):
        for j in range(i + 1, 4):
            distances.append(dist_sq(points[i], points[j]))

    distances.sort()
    # 4 smallest should be sides (equal), 2 largest should be diagonals (equal)
    # Side must be > 0
    return (distances[0] > 0 and
            distances[0] == distances[1] == distances[2] == distances[3] and
            distances[4] == distances[5] and
            distances[4] == 2 * distances[0])
```

---

### Problem 3. LeetCode 1680. Concatenation of Consecutive Binary Numbers
**Archetype:** 17.1 Prime & Factors / 18.6 Bit DP
**Type:** Near Miss
**Statement:** Given `n`, return the decimal value of the binary string formed by concatenating `1` to `n` in binary, modulo `10^9 + 7`.
**Why it fits:** This blends number theory with bit-length tracking. To concatenate `curr` after `prev`, you shift `prev` left by `len(bin(curr)) - 2` bits and OR with `curr`.
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

---

### Problem 4. LeetCode 453. Minimum Moves to Equal Array Elements
**Archetype:** 17.1 Prime & Factors
**Type:** Near Miss
**Statement:** Given an integer array, increment `n-1` elements by 1 each move. Return the minimum moves to make all elements equal.
**Why it fits:** This is a math insight problem disguised as a simulation. Incrementing `n-1` elements is equivalent to decrementing 1 element. The answer is simply `sum(nums) - n * min(nums)`.
**The Twist:** The simulation approach is O(moves), which is exponential in the input size. Recognizing the inverse operation (decrement instead of increment) converts it to O(n).
**Code Skeleton:**
```python
def min_moves(nums) -> int:
    # Incrementing n-1 elements is equivalent to decrementing 1 element.
    # All elements must reach the minimum value.
    min_val = min(nums)
    return sum(num - min_val for num in nums)
```

---

### Problem 5. LeetCode 319. Bulb Switcher
**Archetype:** 17.1 Prime & Factors
**Type:** Near Miss
**Statement:** Given `n` bulbs initially off, toggle every i-th bulb for i from 1 to n. Return how many bulbs are on.
**Why it fits:** This is the classic factor-counting insight. A bulb ends up on if it is toggled an odd number of times, which happens only for perfect squares (they have an odd number of divisors).
**The Twist:** The brute-force simulation is O(n^2). The math insight reduces it to counting perfect squares <= n, which is `int(sqrt(n))` in O(1).
**Code Skeleton:**
```python
import math

def bulb_switch(n: int) -> int:
    # Bulb i ends up on iff i has an odd number of divisors.
    # Only perfect squares have an odd number of divisors.
    return int(math.isqrt(n))
```

---

## Pattern Blends

### Problem 6. LeetCode 73. Set Matrix Zeroes
**Archetype:** 17.5 Matrix Operations / 01.1 Arrays & Hashing
**Type:** Pattern Blend
**Statement:** If an element in the matrix is 0, set its entire row and column to 0. Do it in-place.
**Why it fits:** This blends matrix traversal with space-optimized hashing. The challenge is tracking which rows/columns to zero without using O(m*n) extra space.
**The Twist:** You can use the first row and first column as markers, but then you need two extra variables to track whether the first row/column themselves should be zeroed.
**Code Skeleton:**
```python
def set_zeroes(matrix):
    if not matrix or not matrix[0]:
        return

    m, n = len(matrix), len(matrix[0])
    first_row_has_zero = any(matrix[0][j] == 0 for j in range(n))
    first_col_has_zero = any(matrix[i][0] == 0 for i in range(m))

    # Use first row and column as markers
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0

    # Zero out cells based on markers
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0

    # Handle first row
    if first_row_has_zero:
        for j in range(n):
            matrix[0][j] = 0

    # Handle first column
    if first_col_has_zero:
        for i in range(m):
            matrix[i][0] = 0
```

---

### Problem 7. LeetCode 240. Search a 2D Matrix II
**Archetype:** 17.5 Matrix Operations / 02.1 Two Pointers
**Type:** Pattern Blend
**Statement:** Search for a target in an m x n matrix where rows and columns are sorted in ascending order.
**Why it fits:** This blends matrix properties with the two-pointer technique. Starting from the top-right (or bottom-left) allows you to eliminate one row or column per step.
**The Twist:** Binary search on rows is O(m log n) but suboptimal. The O(m + n) two-pointer solution is optimal because it exploits both row and column ordering simultaneously.
**Code Skeleton:**
```python
def search_matrix(matrix, target: int) -> bool:
    if not matrix or not matrix[0]:
        return False

    m, n = len(matrix), len(matrix[0])
    row, col = 0, n - 1  # Start at top-right

    while row < m and col >= 0:
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] > target:
            col -= 1  # Eliminate current column
        else:
            row += 1  # Eliminate current row

    return False
```

---

### Problem 8. LeetCode 528. Random Pick with Weight
**Archetype:** 17.6 Randomized/Simulation / 01.1 Arrays & Hashing
**Type:** Pattern Blend
**Statement:** Given an array of weights, randomly pick an index proportionally to its weight.
**Why it fits:** This combines prefix sums with binary search and random number generation. The prefix sum array transforms the weighted distribution into a contiguous range problem.
**The Twist:** You must build a prefix sum array once, then for each pick generate a random number in `[1, total_weight]` and binary search for the first prefix sum >= that number.
**Code Skeleton:**
```python
import random
import bisect

class Solution:
    def __init__(self, w):
        self.prefix = []
        total = 0
        for weight in w:
            total += weight
            self.prefix.append(total)

    def pickIndex(self) -> int:
        target = random.randint(1, self.prefix[-1])
        return bisect.bisect_left(self.prefix, target)
```

---

### Problem 9. LeetCode 462. Minimum Moves to Equal Array Elements II
**Archetype:** 17.4 Coordinate Geometry / 15.1 Greedy
**Type:** Pattern Blend
**Statement:** Given an integer array, find the minimum number of moves required to make all array elements equal, where a move is incrementing or decrementing an element by 1.
**Why it fits:** This blends statistics (median minimizes sum of absolute deviations) with sorting. The geometric interpretation is finding a point on the number line that minimizes total distance to all given points.
**The Twist:** The mean minimizes squared distance, but the median minimizes absolute distance. Sorting and picking the middle element gives the answer in O(n log n) or O(n) with quickselect.
**Code Skeleton:**
```python
def min_moves2(nums) -> int:
    nums.sort()
    n = len(nums)
    median = nums[n // 2]  # Lower median works; either median is fine

    # Sum of absolute differences to the median
    return sum(abs(num - median) for num in nums)
```

---

### Problem 10. LeetCode 587. Erect the Fence
**Archetype:** 17.4 Coordinate Geometry / 03.1 Stack
**Type:** Pattern Blend
**Statement:** Given the locations of trees, return the coordinates of the fence enclosing all trees.
**Why it fits:** This is the Convex Hull problem, combining coordinate geometry with a monotonic stack (Graham scan or Jarvis march). It tests cross-product orientation and stack-based boundary construction.
**The Twist:** You must handle collinear points on the hull boundary. The cross product determines if three points make a counter-clockwise turn; a non-CCW turn means the middle point is not on the hull.
**Code Skeleton:**
```python
def outer_trees(trees):
    # Cross product of vectors OA and OB
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    n = len(trees)
    if n <= 3:
        return trees

    # Sort by x, then by y
    trees.sort()

    # Build lower hull
    lower = []
    for p in trees:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) < 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(trees):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) < 0:
            upper.pop()
        upper.append(p)

    # Concatenate and remove duplicates
    return list(set(tuple(p) for p in lower[:-1] + upper[:-1]))
```

---

## Interview Simulation

### Problem 11. LeetCode 592. Fraction Addition and Subtraction
**Archetype:** 17.2 GCD/LCM / 17.6 Randomized/Simulation
**Type:** Interview Sim
**Statement:** Given a string representing an expression of fractions, return the result as a string in irreducible form.
**Why it fits:** This is a full simulation problem combining parsing, arithmetic, and fraction reduction using GCD. It tests careful string processing and exact arithmetic.
**The Twist:** Parsing is the hardest part: you must handle optional signs, mixed signs, and the fact that fractions are separated by `+` or `-` operators. The result must be reduced using GCD and handle negative signs consistently.
**Code Skeleton:**
```python
from math import gcd

def fraction_addition(expression: str) -> str:
    # Parse all fractions from the expression
    import re
    fractions = re.findall(r'([+-]?\d+)/(\d+)', expression)

    num = 0
    den = 1

    for n_str, d_str in fractions:
        n, d = int(n_str), int(d_str)
        # Add current fraction to running total: num/den + n/d
        num = num * d + n * den
        den = den * d

        # Reduce by GCD
        g = gcd(abs(num), abs(den))
        num //= g
        den //= g

    # Normalize sign
    if den < 0:
        num = -num
        den = -den

    return f"{num}/{den}"
```

---

### Problem 12. LeetCode 43. Multiply Strings
**Archetype:** 17.6 Randomized/Simulation
**Type:** Interview Sim
**Statement:** Given two non-negative integers as strings, return their product as a string.
**Why it fits:** This simulates grade-school multiplication digit by digit. It tests array indexing, carry propagation, and handling large numbers without built-in big integer support.
**The Twist:** The result length is at most `len(num1) + len(num2)`. You compute the product at each position first, then propagate carries in a second pass. Reversing the strings or using index arithmetic from the end is required.
**Code Skeleton:**
```python
def multiply(num1: str, num2: str) -> str:
    if num1 == "0" or num2 == "0":
        return "0"

    m, n = len(num1), len(num2)
    result = [0] * (m + n)

    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            product = int(num1[i]) * int(num2[j])
            p1, p2 = i + j, i + j + 1
            total = product + result[p2]

            result[p2] = total % 10
            result[p1] += total // 10

    # Convert to string, skipping leading zeros
    output = []
    for digit in result:
        if not (len(output) == 0 and digit == 0):
            output.append(str(digit))

    return "".join(output)
```

---

### Problem 13. LeetCode 400. Nth Digit
**Archetype:** 17.1 Prime & Factors
**Type:** Interview Sim
**Statement:** Find the `n`-th digit of the infinite integer sequence `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ...`
**Why it fits:** This tests pattern finding in digit sequences. There are 9 one-digit numbers, 90 two-digit numbers, 900 three-digit numbers, etc. You determine which "block" the n-th digit falls into.
**The Twist:** You cannot generate the sequence. You must calculate: for `k`-digit numbers, there are `9 * 10^(k-1)` numbers, contributing `9 * 10^(k-1) * k` digits. Find `k`, then find the exact number and digit within it.
**Code Skeleton:**
```python
def find_nth_digit(n: int) -> int:
    # Determine the length of the number where the n-th digit resides
    length = 1
    count = 9
    start = 1

    while n > length * count:
        n -= length * count
        length += 1
        count *= 10
        start *= 10

    # Find the exact number
    number = start + (n - 1) // length

    # Find the exact digit within that number
    digit_index = (n - 1) % length
    return int(str(number)[digit_index])
```

---

### Problem 14. LeetCode 483. Smallest Good Base
**Archetype:** 17.1 Prime & Factors / 17.3 Power/Modulo
**Type:** Interview Sim
**Statement:** Given a string representation of an integer `n`, return the smallest good base of `n` in string format.
**Why it fits:** A good base `k` means `n = 1 + k + k^2 + ... + k^(m-1)` for some `m`. This is a geometric series, so `n = (k^m - 1) / (k - 1)`. You search over possible `m` and use binary search for `k`.
**The Twist:** For each possible length `m` (from log2(n) down to 2), you binary search for a base `k` such that the geometric series equals `n`. This combines number theory with binary search.
**Code Skeleton:**
```python
def smallest_good_base(n: str) -> str:
    n = int(n)
    max_m = n.bit_length()

    for m in range(max_m, 1, -1):
        # Binary search for base k
        lo, hi = 2, n - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            # Compute 1 + mid + mid^2 + ... + mid^(m-1)
            total = 1
            term = 1
            overflow = False
            for _ in range(1, m):
                term *= mid
                total += term
                if total > n:
                    overflow = True
                    break

            if overflow or total > n:
                hi = mid - 1
            elif total < n:
                lo = mid + 1
            else:
                return str(mid)

    return str(n - 1)
```

---

### Problem 15. LeetCode 1515. Best Position for a Service Centre
**Archetype:** 17.4 Coordinate Geometry
**Type:** Interview Sim
**Statement:** Given the positions of customers, find the position of a service centre that minimizes the sum of Euclidean distances to all customers.
**Why it fits:** This is the geometric median problem, which has no closed-form solution. It requires gradient descent / Weiszfeld's algorithm or simulated annealing to approximate.
**The Twist:** The objective function is not differentiable when the centre coincides with a customer. You must use iterative approximation with a learning rate that decays over time, or Weiszfeld's algorithm.
**Code Skeleton:**
```python
def get_min_dist_sum(positions):
    # Initialize at the centroid
    x = sum(p[0] for p in positions) / len(positions)
    y = sum(p[1] for p in positions) / len(positions)

    learning_rate = 1.0
    epsilon = 1e-7

    while learning_rate > epsilon:
        # Compute gradient: sum of unit vectors from centre to each point
        grad_x = grad_y = 0.0
        for px, py in positions:
            dx = x - px
            dy = y - py
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < epsilon:
                continue
            grad_x += dx / dist
            grad_y += dy / dist

        # Move in the negative gradient direction
        new_x = x - learning_rate * grad_x
        new_y = y - learning_rate * grad_y

        # If no improvement, reduce learning rate
        if ((new_x - x)**2 + (new_y - y)**2) ** 0.5 < epsilon:
            learning_rate *= 0.5
        else:
            x, y = new_x, new_y

    # Return total distance (or the coordinate, depending on problem variant)
    return sum(((x - px)**2 + (y - py)**2) ** 0.5 for px, py in positions)
```
