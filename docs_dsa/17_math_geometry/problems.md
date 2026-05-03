# Pattern 17: Math & Geometry — Practice Problems

## Primes

### 204. Count Primes
**Statement:** Count primes less than n.
**Code (Sieve):**
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

### 264. Ugly Number II
**Statement:** Nth ugly number (factors only 2, 3, 5).
**Intuition:** Three pointers for multiples of 2, 3, 5.

---

## GCD / Fractions

### 149. Max Points on a Line
**Statement:** Max points on same line.
**Intuition:** For each point, count slopes to other points. Use GCD to normalize slope.

### 166. Fraction to Recurring Decimal
**Statement:** Convert fraction to decimal string.
**Intuition:** Long division. Track remainders. If remainder repeats, decimal repeats.

---

## Power

### 50. Pow(x, n)
**Statement:** Compute x^n.
**Code (Fast power):**
```python
def my_pow(x, n):
    if n < 0:
        x = 1 / x
        n = -n
    result = 1
    while n > 0:
        if n % 2 == 1:
            result *= x
        x *= x
        n //= 2
    return result
```

### 372. Super Pow
**Statement:** a^b mod 1337 where b is a large array.
**Intuition:** Use Euler's theorem or iterative mod.

---

## Matrix

### 54. Spiral Matrix
**Statement:** Return elements in spiral order.
**Intuition:** Four boundaries. Traverse right, down, left, up. Shrink boundaries.

### 48. Rotate Image
**Statement:** Rotate matrix 90 degrees clockwise in-place.
**Code:**
```python
def rotate(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for i in range(n):
        matrix[i].reverse()
```

### 73. Set Matrix Zeroes
**Statement:** If element is 0, set entire row and column to 0.
**Intuition:** Use first row/column as markers. Handle first row/column separately.

---

## Random / Simulation

### 384. Shuffle an Array
**Statement:** Uniform shuffle.
**Intuition:** Fisher-Yates. Swap each element with random element from i to end.

### 528. Random Pick with Weight
**Statement:** Pick index with probability proportional to weight.
**Intuition:** Prefix sums + binary search.

### 43. Multiply Strings
**Statement:** Multiply two numbers represented as strings.
**Intuition:** Grade school multiplication. Result[i+j+1] += num1[i] * num2[j].

---

## Game Theory

### 292. Nim Game
**Statement:** Can win Nim with n stones?
**Intuition:** If n % 4 == 0, lose. Else win.

### 486. Predict the Winner
**Statement:** Can first player win if both play optimally?
**Intuition:** DP[i][j] = max score player can get from nums[i:j+1].

---

## Mixed Drill Set

1. 204 — Count primes
2. 50 — Pow(x, n)
3. 54 — Spiral matrix
4. 48 — Rotate image
5. 149 — Max points on line
6. 384 — Shuffle array
7. 264 — Ugly number II
8. 73 — Set matrix zeroes
9. 292 — Nim game
10. 166 — Fraction to decimal
11. 528 — Random pick with weight
12. 43 — Multiply strings
