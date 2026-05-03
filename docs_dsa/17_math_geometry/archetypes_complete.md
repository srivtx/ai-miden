# Pattern 17: Math & Geometry — Complete Archetype Map

> **Pattern Recognition:** When you see "prime", "GCD", "power", "modulo", "coordinate", "matrix", "random", "game theory" — think mathematical properties, formulas, and number-theoretic algorithms.
>
> **Fundamental Insight:** Many problems have a mathematical structure that allows O(1), O(log n), or O(sqrt(n)) solutions where brute force would be O(n) or worse. Know the Euclidean algorithm, fast exponentiation, sieve, and geometric primitives.

---

## Archetype 17.1: Prime & Factors

### Recognition Signal (10 seconds)
Words: **"prime", "count primes", "factors", "divisors", "sieve", "prime numbers", "factorization"**

The question: **"Count primes up to n, find prime factors, or test primality efficiently."**

### Core Structure
```python
def sieve_of_eratosthenes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    
    return [i for i in range(2, n + 1) if is_prime[i]]
```

### The Invariant
After processing prime `i`, all multiples of `i` up to `n` are marked as composite. We only need to check up to `sqrt(n)` because any composite number `c <= n` has a prime factor `<= sqrt(c) <= sqrt(n)`.

### Canonical Problem: Count Primes (LeetCode 204)
**Statement:** Given an integer `n`, return the number of prime numbers that are strictly less than `n`.

```python
def count_primes(n):
    if n <= 2:
        return 0
    
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            # Start from i*i because smaller multiples are already marked
            for j in range(i * i, n, i):
                is_prime[j] = False
    
    return sum(is_prime)
```

### Variation Family

**V1: Perfect Number (LeetCode 507)**
- **Twist:** A perfect number equals the sum of its positive divisors excluding itself
- **Change:** Sum divisors up to sqrt(n). Check if sum equals n.
- **Key insight:** Only a few perfect numbers exist (6, 28, 496, 8128, ...). Could even hardcode.

```python
def check_perfect_number(num):
    if num <= 1:
        return False
    total = 1
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            total += i
            if i != num // i:
                total += num // i
    return total == num
```

**V2: Four Divisors (LeetCode 1390)**
- **Twist:** Find sum of integers in array that have exactly four divisors
- **Change:** For each number, count divisors by trial division up to sqrt.
- **Key insight:** Exactly four divisors means n = p^3 or n = p*q where p and q are distinct primes.

**V3: Closest Prime Numbers in Range (LeetCode 2523)**
- **Twist:** Given left and right, find closest prime pair in [left, right]
- **Change:** Sieve segment [left, right], then scan for minimum gap.
- **Key insight:** Segment sieve for large ranges with small width.

**V4: Prime Arrangements (LeetCode 1175)**
- **Twist:** Arrange numbers 1..n such that prime-indexed positions hold primes
- **Change:** Count primes <= n. Answer = (prime_count)! * (n - prime_count)! mod 10^9 + 7.
- **Key insight:** Primes must go to prime indices; non-primes to non-prime indices. Factorials count arrangements.

**Near Miss: Ugly Number II (LeetCode 264)**
- **Looks like:** Prime factors
- **But:** Dynamic programming / three-pointer problem. Finding n-th number with only 2, 3, 5 as prime factors.
- **Lesson:** Not all factorization problems use sieve. Some use DP or heap.

---

## Archetype 17.2: GCD / LCM

### Recognition Signal (10 seconds)
Words: **"greatest common divisor", "GCD", "LCM", "water jug", "Bézout", "coprime", "divisible"**

The question: **"Find GCD of two numbers, or use GCD properties to determine feasibility."**

### Core Structure
```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return a * b // gcd(a, b)
```

### The Invariant
The Euclidean algorithm maintains that `gcd(a, b) = gcd(b, a % b)`. The remainder strictly decreases, guaranteeing termination. By Bézout's identity, `ax + by = gcd(a, b)` has integer solutions.

### Canonical Problem: Water and Jug Problem (LeetCode 365)
**Statement:** You are given two jugs with capacities `jug1Capacity` and `jug2Capacity` liters. Return `true` if you can measure exactly `targetCapacity` liters.

```python
def can_measure_water(jug1, jug2, target):
    if target > jug1 + jug2:
        return False
    if target == 0:
        return True
    # By Bézout's identity, target must be divisible by GCD of jug capacities
    return target % gcd(jug1, jug2) == 0
```

### Variation Family

**V1: Greatest Common Divisor of Strings (LeetCode 1071)**
- **Twist:** Find largest string x such that `str1 = x + x + ...` and `str2 = x + x + ...`
- **Change:** `gcd(str1, str2)` exists iff `str1 + str2 == str2 + str1`. Length of GCD string = `gcd(len(str1), len(str2))`.
- **Key insight:** String concatenation commutativity mirrors GCD existence.

```python
def gcd_of_strings(str1, str2):
    if str1 + str2 != str2 + str1:
        return ""
    from math import gcd
    return str1[:gcd(len(str1), len(str2))]
```

**V2: Find Greatest Common Divisor of Array (LeetCode 1979)**
- **Twist:** Find GCD of all numbers in array
- **Change:** Reduce array using `gcd(result, nums[i])`.
- **Key insight:** GCD is associative: `gcd(a, b, c) = gcd(gcd(a, b), c)`.

**V3: Nth Magical Number (LeetCode 878)**
- **Twist:** Find n-th positive integer divisible by a or b
- **Change:** Binary search on answer. Count of magical numbers <= x = `x//a + x//b - x//lcm(a,b)`.
- **Key insight:** Inclusion-exclusion principle with LCM. Binary search for the n-th element.

**V4: Number of Beautiful Pairs (LeetCode 2748)**
- **Twist:** Count pairs where GCD(first_digit(nums[i]), last_digit(nums[j])) == 1
- **Change:** Precompute first/last digits. Use frequency map + GCD check.
- **Key insight:** Only 9 possible first digits and 10 possible last digits. Can optimize with counting.

**Near Miss: Sum of Square Numbers (LeetCode 633)**
- **Looks like:** Number theory
- **But:** Two-pointer problem. Check if c = a^2 + b^2.
- **Lesson:** Not every number theory problem requires GCD. Some use algebraic manipulation or two pointers.

---

## Archetype 17.3: Power / Modulo

### Recognition Signal (10 seconds)
Words: **"power", "exponent", "modulo", "pow", "fast exponentiation", "modular arithmetic", "large exponent"**

The question: **"Compute base^exponent efficiently, often with modulo to prevent overflow."**

### Core Structure
```python
def fast_pow(base, exp, mod):
    result = 1
    base = base % mod
    
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    
    return result
```

### The Invariant
At each step, `result * base^exp` equals the original `base^original_exp` (modulo `mod`). We halve the exponent each iteration, achieving O(log exp) time.

### Canonical Problem: Pow(x, n) (LeetCode 50)
**Statement:** Implement `pow(x, n)`, which calculates `x` raised to the power `n`.

```python
def my_pow(x, n):
    if n == 0:
        return 1.0
    if n < 0:
        x = 1 / x
        n = -n
    
    result = 1.0
    while n > 0:
        if n % 2 == 1:
            result *= x
        x *= x
        n //= 2
    
    return result
```

### Variation Family

**V1: Super Pow (LeetCode 372)**
- **Twist:** Compute a^b mod 1337 where b is a very large number represented as an array
- **Change:** Use property: `a^b mod m = (a^(b//10))^10 * a^(b%10) mod m`. Process digits recursively.
- **Key insight:** Reduce large exponent digit by digit using modular exponentiation.

```python
def super_pow(a, b):
    MOD = 1337
    
    def pow_mod(base, exp, mod):
        result = 1
        base %= mod
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp >>= 1
        return result
    
    result = 1
    for digit in b:
        result = pow_mod(result, 10, MOD) * pow_mod(a, digit, MOD) % MOD
    return result
```

**V2: Power of Three (LeetCode 326)**
- **Twist:** Is n a power of three?
- **Change:** Loop division by 3, or math: `n > 0 and 3^19 % n == 0` (since 3^19 is max power of 3 in 32-bit int).
- **Key insight:** Logarithm approach has precision issues. Integer division or modular check is safer.

**V3: Power of Four (LeetCode 342)**
- **Twist:** Is n a power of four?
- **Change:** `n > 0 and (n & (n - 1)) == 0 and (n & 0x55555555) != 0`. Power of 4 has exactly one bit set in an odd position.
- **Key insight:** Power of 4 is also power of 2, but the set bit must be in position 0, 2, 4, ... (0-indexed).

**V4: Maximize the Number of Nice Divisors (LeetCode 1808)**
- **Twist:** Given primeFactors, form a number with exactly that many prime factors. Maximize number of nice divisors (divisors that are prime). Use as many 3s as possible.
- **Change:** Greedy decomposition into 3s. Use fast pow for large exponents mod 10^9 + 7.
- **Key insight:** For a fixed sum, product is maximized by using as many 3s as possible (mathematical optimization).

**Near Miss: Sqrt(x) (LeetCode 69)**
- **Looks like:** Power / root
- **But:** Newton's method or binary search problem. Not fast exponentiation.
- **Lesson:** Roots and powers are related but require different algorithms.

---

## Archetype 17.4: Coordinate Geometry

### Recognition Signal (10 seconds)
Words: **"points", "line", "slope", "coordinates", "convex hull", "area", "distance", "collinear"**

The question: **"Analyze geometric relationships between points: collinearity, distance, area, containment."**

### Core Structure
```python
def max_points_on_line(points):
    from math import gcd
    max_count = 0
    
    for i in range(len(points)):
        slopes = {}
        same_point = 1
        for j in range(i + 1, len(points)):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            
            if dx == 0 and dy == 0:
                same_point += 1
                continue
            
            # Reduce slope to lowest terms
            g = gcd(dx, dy)
            dx //= g
            dy //= g
            
            # Normalize sign so slope is unique
            if dx < 0:
                dx, dy = -dx, -dy
            elif dx == 0:
                dy = 1
            
            slopes[(dx, dy)] = slopes.get((dx, dy), 0) + 1
        
        current_max = max(slopes.values(), default=0) + same_point
        max_count = max(max_count, current_max)
    
    return max_count
```

### The Invariant
For each point `i`, we compute the reduced slope to every other point. Points with the same reduced slope relative to `i` lie on the same line through `i`. We use GCD to normalize slopes and avoid floating-point precision issues.

### Canonical Problem: Max Points on a Line (LeetCode 149)
**Statement:** Given an array of `points` where `points[i] = [xi, yi]`, return the maximum number of points that lie on the same straight line.

```python
def max_points(points):
    from math import gcd
    n = len(points)
    if n <= 2:
        return n
    
    max_count = 0
    
    for i in range(n):
        slopes = {}
        same_point = 1
        for j in range(i + 1, n):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            
            if dx == 0 and dy == 0:
                same_point += 1
                continue
            
            g = gcd(dx, dy)
            dx //= g
            dy //= g
            
            # Normalize sign
            if dx < 0:
                dx, dy = -dx, -dy
            elif dx == 0:
                dy = abs(dy)
            
            slopes[(dx, dy)] = slopes.get((dx, dy), 0) + 1
        
        current_max = max(slopes.values(), default=0) + same_point
        max_count = max(max_count, current_max)
    
    return max_count
```

### Variation Family

**V1: Rectangle Area (LeetCode 223)**
- **Twist:** Compute total area covered by two rectangles (including overlap)
- **Change:** Area = area1 + area2 - overlap_area. Overlap is intersection of x and y intervals.
- **Key insight:** 2D geometry reduces to 1D interval intersection for each axis.

**V2: Valid Square (LeetCode 593)**
- **Twist:** Given four points, determine if they form a valid square
- **Change:** Compute all 6 pairwise distances. A square has 4 equal sides and 2 equal diagonals.
- **Key insight:** Square properties in terms of distances. Check for exactly 2 unique non-zero distances.

**V3: Erect the Fence (LeetCode 587)**
- **Twist:** Find convex hull of a set of points
- **Change:** Monotone chain (Andrew's algorithm) or Graham scan. Sort points, build lower and upper hulls.
- **Key insight:** Cross product determines orientation (clockwise vs counter-clockwise).

**V4: Minimum Area Rectangle II (LeetCode 963)**
- **Twist:** Find minimum area of any rectangle (not necessarily axis-aligned) formed by points
- **Change:** For each pair of points, treat as diagonal. Midpoint and diagonal length must match for rectangle.
- **Key insight:** Rectangle diagonals bisect each other and are equal in length.

**Near Miss: K Closest Points to Origin (LeetCode 973)**
- **Looks like:** Coordinate geometry
- **But:** Heap or quickselect problem. Distance formula is trivial; the challenge is selection.
- **Lesson:** Geometry is the setup; the algorithm is usually sorting, heap, or hash map.

---

## Archetype 17.5: Matrix Operations

### Recognition Signal (10 seconds)
Words: **"rotate matrix", "spiral", "set zeroes", "transpose", "diagonal", "in-place", "layer"**

The question: **"Manipulate a matrix in-place or produce a specific traversal pattern."**

### Core Structure
```python
def rotate_matrix(matrix):
    n = len(matrix)
    # Transpose
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    # Reverse each row
    for i in range(n):
        matrix[i].reverse()
```

### The Invariant
Rotating 90 degrees clockwise is equivalent to transposing the matrix and then reversing each row. Each element moves to its correct position through these two well-defined operations.

### Canonical Problem: Rotate Image (LeetCode 48)
**Statement:** You are given an `n x n` 2D `matrix` representing an image, rotate the image by 90 degrees (clockwise) in-place.

```python
def rotate(matrix):
    n = len(matrix)
    
    # Transpose: swap across diagonal
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    
    # Reverse each row
    for i in range(n):
        matrix[i].reverse()
```

### Variation Family

**V1: Spiral Matrix (LeetCode 54)**
- **Twist:** Return elements of matrix in spiral order
- **Change:** Track boundaries (top, bottom, left, right). Traverse and shrink boundaries.
- **Key insight:** Maintain four boundaries and traverse in order: right, down, left, up.

```python
def spiral_order(matrix):
    if not matrix:
        return []
    
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            result.append(matrix[top][j])
        top += 1
        
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1
        
        if top <= bottom:
            for j in range(right, left - 1, -1):
                result.append(matrix[bottom][j])
            bottom -= 1
        
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
    
    return result
```

**V2: Set Matrix Zeroes (LeetCode 73)**
- **Twist:** If an element is 0, set its entire row and column to 0. Do it in-place.
- **Change:** Use first row/column as markers. Track if first row/column themselves need zeroing.
- **Key insight:** O(1) space by reusing matrix boundaries as flags.

**V3: Diagonal Traverse (LeetCode 498)**
- **Twist:** Return matrix elements in diagonal order
- **Change:** Elements on the same diagonal have constant `i + j`. Collect by sum, alternate direction.
- **Key insight:** Diagonal index = `row + col`. Even sums go up, odd sums go down.

**V4: Spiral Matrix III (LeetCode 885)**
- **Twist:** Start at (r0, c0) and walk in a spiral. Return coordinates in order until all cells visited.
- **Change:** Simulate spiral walk. Step lengths increase every two directions.
- **Key insight:** Spiral step pattern: 1 right, 1 down, 2 left, 2 up, 3 right, 3 down, ...

**Near Miss: Search a 2D Matrix (LeetCode 74)**
- **Looks like:** Matrix operation
- **But:** Binary search treats matrix as sorted 1D array. No matrix manipulation needed.
- **Lesson:** Matrix form does not always imply matrix operations. Check if the structure is just a sorted container.

---

## Archetype 17.6: Randomized / Simulation

### Recognition Signal (10 seconds)
Words: **"random", "rand7", "rand10", "rejection sampling", "Monte Carlo", "simulation", "uniform", "probability"**

The question: **"Generate random numbers or simulate a probabilistic process uniformly."**

### Core Structure
```python
def rand10():
    # Using rand7() to generate uniform 1..10
    while True:
        # Generate uniform 0..48 (7*7 - 1)
        num = (rand7() - 1) * 7 + (rand7() - 1)
        if num < 40:
            return num % 10 + 1
```

### The Invariant
Rejection sampling maintains uniformity by discarding values that would bias the distribution. We generate a larger uniform range and reject values outside the largest multiple of our target range. Accepted values map uniformly to the target range via modulo.

### Canonical Problem: Implement Rand10() Using Rand7() (LeetCode 470)
**Statement:** Given the API `rand7()` that generates a uniform random integer in the range `[1, 7]`, write a function `rand10()` that generates a uniform random integer in the range `[1, 10]`.

```python
# The rand7() API is already defined.
def rand7():
    pass

def rand10():
    while True:
        # Generate a number in [0, 48] uniformly
        row = rand7() - 1
        col = rand7() - 1
        num = row * 7 + col  # 0 to 48
        
        # Reject numbers >= 40 to maintain uniformity
        if num < 40:
            return num % 10 + 1
```

### Variation Family

**V1: Generate Random Point in a Circle (LeetCode 478)**
- **Twist:** Uniform random point in a circle
- **Change:** Rejection sampling in unit square, or polar coordinates with `sqrt(random)` for radius.
- **Key insight:** Uniform area requires `r = sqrt(random) * radius`, not `r = random * radius`.

```python
def rand_point(radius, x_center, y_center):
    import random, math
    # Polar method for uniform distribution in circle
    r = math.sqrt(random.random()) * radius
    theta = random.random() * 2 * math.pi
    return [x_center + r * math.cos(theta), y_center + r * math.sin(theta)]
```

**V2: Insert Delete GetRandom O(1) (LeetCode 380)**
- **Twist:** Data structure supporting insert, delete, and getRandom in O(1)
- **Change:** Hash map + dynamic array. Swap with last element for deletion.
- **Key insight:** Array gives O(1) random access; hash map gives O(1) lookup. Swap-to-delete maintains contiguity.

**V3: Shuffle an Array (LeetCode 384)**
- **Twist:** Return a random shuffling of the array
- **Change:** Fisher-Yates shuffle. Iterate backwards, swap current with random index in [0, i].
- **Key insight:** Every permutation must have exactly 1/n! probability. Fisher-Yates guarantees this.

**V4: Random Pick Index (LeetCode 398)**
- **Twist:** Given array with possible duplicates, pick a random index of target value
- **Change:** Reservoir sampling. Iterate array; if nums[i] == target, pick it with probability 1/count.
- **Key insight:** Reservoir sampling handles streaming/unknown size with uniform probability.

**Near Miss: Linked List Random Node (LeetCode 382)**
- **Looks like:** Randomized
- **But:** Reservoir sampling on a stream. Different from bounded random generation.
- **Lesson:** Streaming random selection requires reservoir sampling; bounded arrays can use direct indexing.

---

## Archetype 17.7: Game Theory

### Recognition Signal (10 seconds)
Words: **"game", "nim", "win", "optimal play", "take turns", "strategy", "predict winner"**

The question: **"Two players take turns. Determine if first player can win with optimal play."**

### Core Structure
```python
def can_win_nim(n):
    # Nim game: take 1-3 stones. Last to move wins.
    return n % 4 != 0
```

### The Invariant
In Nim with max removal 3, positions where `n % 4 == 0` are losing positions (P-positions). Whatever the current player does, the opponent can always respond to return to a multiple of 4. This invariant propagates backwards from the base case.

### Canonical Problem: Nim Game (LeetCode 292)
**Statement:** You are playing a Nim Game with your friend. There is a heap of stones on the table. You and your friend will alternate taking turns, and you go first. On each turn, the person whose turn it is will remove 1 to 3 stones. The one who removes the last stone wins. Return `true` if you can win the game.

```python
def can_win_nim(n):
    # If n is a multiple of 4, you lose with optimal play from opponent
    # Otherwise, take enough stones to leave a multiple of 4
    return n % 4 != 0
```

### Variation Family

**V1: Predict the Winner (LeetCode 486)**
- **Twist:** Two players take turns picking from ends of array. Predict if first player wins.
- **Change:** DP interval game. `dp[i][j] = max(nums[i] - dp[i+1][j], nums[j] - dp[i][j-1])`.
- **Key insight:** Track score difference between current player and opponent. Positive means current player wins.

```python
def predict_the_winner(nums):
    n = len(nums)
    dp = [[0] * n for _ in range(n)]
    
    for i in range(n):
        dp[i][i] = nums[i]
    
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = max(nums[i] - dp[i + 1][j], nums[j] - dp[i][j - 1])
    
    return dp[0][n - 1] >= 0
```

**V2: Can I Win (LeetCode 464)**
- **Twist:** Choose numbers 1..maxChoosableInteger without replacement. First to reach desiredTotal wins.
- **Change:** Memoization with bitmask representing used numbers.
- **Key insight:** State space is small (up to 20 numbers). Bitmask + memoization explores all game states.

**V3: Stone Game (LeetCode 877)**
- **Twist:** Alice and Bob play stone game with even number of piles. Alice always wins.
- **Change:** DP similar to Predict the Winner. Can also prove Alice always wins by parity argument.
- **Key insight:** With even piles and sum odd, first player can always force a win by picking all even-indexed or all odd-indexed piles.

**V4: Flip Game II (LeetCode 294)**
- **Twist:** Players take turns flipping "++" to "--". First player who cannot move loses.
- **Change:** Memoization on string state. Try every valid flip; if any leads to opponent losing, current player wins.
- **Key insight:** Standard impartial game. Can use memoization or Sprague-Grundy theorem.

**Near Miss: N-Queens (LeetCode 51)**
- **Looks like:** Game / strategy
- **But:** Backtracking puzzle with no opponent. Pure combinatorial search.
- **Lesson:** Game theory requires an opponent with optimal play. Single-player puzzles use backtracking/DP.

---

## Pattern 17 Mastery Checklist

Before moving to Pattern 18, confirm you can:

- [ ] Sieve of Eratosthenes: implement and explain O(n log log n) complexity
- [ ] GCD/LCM: write Euclidean algorithm and apply Bézout's identity
- [ ] Fast power: implement binary exponentiation with modulo
- [ ] Coordinate geometry: compute slope with GCD normalization, avoid float precision issues
- [ ] Matrix operations: rotate in-place, spiral traversal, set zeroes with O(1) space
- [ ] Randomized: rejection sampling, Fisher-Yates shuffle, reservoir sampling
- [ ] Game theory: identify P-positions and N-positions, write minimax DP
- [ ] Modular arithmetic: handle large numbers with mod to prevent overflow
- [ ] Distinguish: when a geometry problem needs pure math vs when it needs data structures

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Using float for slope comparison | Precision errors on large coordinates | Use reduced integer fractions (dx/gcd, dy/gcd) |
| Not handling modulo negative numbers | Wrong answer for negative bases | Add mod and then % mod: `(a % mod + mod) % mod` |
| O(n) primality test for large n | TLE | Use sieve for multiple queries; trial division up to sqrt(n) for single query |
| Forgetting in-place constraint for matrix | Uses O(n^2) extra space | Use first row/column as markers, or layer-by-layer swap |
| Rejection sampling without uniform range | Biased distribution | Reject values >= k * target where k is largest integer such that k*target <= generated_range |
| Confusing power of 2, 3, 4 checks | Wrong bit manipulation | Power of 2: `n & (n-1) == 0`; Power of 4: also check `n & 0x55555555 != 0` |
| Not checking game base cases | Stack overflow or wrong result | Always define terminal states explicitly |

---

## Pattern Blends (What Comes Next)

Math & Geometry does not live in isolation. It blends with:

- **Bit Manipulation:** Power of two checks, counting bits, XOR properties
- **DP:** Predict the winner, stone game, optimal play with memoization
- **Binary Search:** Nth magical number, sqrt(x), finding thresholds
- **Greedy:** Decompose into 3s for maximum product, Egyptian fractions
- **Intervals:** Rectangle overlap, geometric union and intersection problems

---

*Next: Pattern 18 — Bit Manipulation*
