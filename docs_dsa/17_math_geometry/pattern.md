# Pattern 17: Math & Geometry

> **Pattern Recognition:** When you see "GCD", "LCM", "prime", "power", "modulo", "matrix", "rotate", "area", "coordinates" — think math & geometry.
>
> **Fundamental Insight:** These problems test mathematical intuition and spatial reasoning. Knowing number theory properties (divisibility, primes, modular arithmetic) and geometric formulas saves time.

---

## Archetype 17.1: Prime & Factors

### Recognition Signal
Words: **"prime", "count primes", "factors", "divisible", "ugly number"**

### Sieve of Eratosthenes
```python
def count_primes(n):
    if n <= 2:
        return 0
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n, i):
                is_prime[j] = False
    return sum(is_prime)
```

### Problems
- Count Primes (LeetCode 204)
- Ugly Number (LeetCode 263)
- Ugly Number II (LeetCode 264)
- Super Ugly Number (LeetCode 313)

---

## Archetype 17.2: GCD / LCM

### Recognition Signal
Words: **"GCD", "LCM", "greatest common divisor", "fraction", "repeating decimal"**

### Euclidean Algorithm
```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
```

### Problems
- Fraction to Recurring Decimal (LeetCode 166)
- Max Points on a Line (LeetCode 149)

---

## Archetype 17.3: Power / Modulo

### Recognition Signal
Words: **"power", "modulo", "exponentiation", "super pow"**

### Fast Power (Modular Exponentiation)
```python
def fast_power(base, exp, mod):
    result = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result
```

### Problems
- Pow(x, n) (LeetCode 50)
- Super Pow (LeetCode 372)

---

## Archetype 17.4: Coordinate Geometry

### Recognition Signal
Words: **"points", "line", "area", "rectangle", "overlap", "convex hull"**

### Problems
- Max Points on a Line (LeetCode 149)
- Rectangle Area (LeetCode 223)
- Valid Square (LeetCode 593)
- Convex Polygon (LeetCode 469)

---

## Archetype 17.5: Matrix Operations

### Recognition Signal
Words: **"matrix", "rotate", "spiral", "set zeroes", "transpose"**

### Problems
- Spiral Matrix (LeetCode 54)
- Rotate Image (LeetCode 48)
- Set Matrix Zeroes (LeetCode 73)
- Search a 2D Matrix II (LeetCode 240) — also binary search

**Rotate 90 clockwise:**
```python
def rotate(matrix):
    n = len(matrix)
    # Transpose
    for i in range(n):
        for j in range(i, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    # Reverse each row
    for i in range(n):
        matrix[i].reverse()
```

---

## Archetype 17.6: Randomized / Simulation

### Recognition Signal
Words: **"random", "shuffle", "pick", "reservoir sampling", "simulation"**

### Problems
- Shuffle an Array (LeetCode 384)
- Random Pick with Weight (LeetCode 528)
- Implement Rand10() Using Rand7() (LeetCode 470)
- Fraction Addition and Subtraction (LeetCode 592)
- Multiply Strings (LeetCode 43)

---

## Archetype 17.7: Game Theory

### Recognition Signal
Words: **"Nim", "game", "can win", "optimal play", "take turns"**

### Problems
- Nim Game (LeetCode 292)
- Can I Win (LeetCode 464)
- Predict the Winner (LeetCode 486)

---

## Mastery Checklist
- [ ] Sieve of Eratosthenes
- [ ] Euclidean algorithm for GCD
- [ ] Fast modular exponentiation
- [ ] Matrix transpose and rotate in-place
- [ ] Spiral matrix traversal
- [ ] Random pick with prefix sums
- [ ] Game theory: Nim, winning/losing states

---

## Common Math Properties

**Divisibility:**
- If sum of digits divisible by 3, number divisible by 3
- If last digit 0 or 5, divisible by 5
- If last two digits divisible by 4, number divisible by 4

**Modular Arithmetic:**
- (a + b) % m = ((a % m) + (b % m)) % m
- (a * b) % m = ((a % m) * (b % m)) % m

**Geometry:**
- Area of overlap: overlap_width * overlap_height
- Check if point inside rectangle
- Distance between points
- Slope of line (watch for division by zero)

---

## Common Traps

**Trap:** Integer overflow in multiplication.
- Fix: Use modulo after each operation.

**Trap:** Floating point precision.
- Fix: Use cross product for collinearity, not slope comparison.

**Trap:** Off-by-one in spiral traversal.
- Fix: Carefully manage boundaries (top, bottom, left, right).

**Near Miss: Matrix Exponentiation**
- Used for Fibonacci in O(log n)
- Advanced technique for linear recurrences
