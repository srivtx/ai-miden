# Heap: Drills Part 3 — Near Misses + Pattern Blends + Interview Simulation

---

### Problem 16. 264. Ugly Number II
**Archetype:** 8.2 Merge K Sorted
**Type:** Near Miss
**Statement:** An ugly number is a positive integer whose prime factors are limited to 2, 3, and 5. Given an integer n, return the n-th ugly number.
**Why it fits:** The sequence of ugly numbers is formed by merging three implicit sorted sequences: `1*2, 2*2, 3*2, ...`, `1*3, 2*3, 3*3, ...`, and `1*5, 2*5, 3*5, ...`. A min-heap elegantly merges these sequences while deduplicating.
**The Twist:** Instead of merging explicit lists, you generate the next candidates by multiplying the current ugly number by 2, 3, and 5. A set prevents duplicates from being pushed repeatedly.
**Code Skeleton:**
```python
import heapq

def nthUglyNumber(n: int) -> int:
    if n <= 0:
        return 0
    heap = [1]
    seen = {1}
    factors = [2, 3, 5]
    curr = 1
    for _ in range(n):
        curr = heapq.heappop(heap)
        for f in factors:
            nxt = curr * f
            if nxt not in seen:
                seen.add(nxt)
                heapq.heappush(heap, nxt)
    return curr
```

---

### Problem 17. 313. Super Ugly Number
**Archetype:** 8.2 Merge K Sorted
**Type:** Near Miss
**Statement:** A super ugly number is a positive integer whose prime factors are in the given prime list. Given an integer n and an array of primes, return the n-th super ugly number.
**Why it fits:** It generalizes Ugly Number II from 3 implicit sequences to k implicit sequences (one per prime). The min-heap approach scales naturally, or you can use the pointer/dp approach which is more efficient.
**The Twist:** The pointer (DP) approach is preferred for large n because the heap can grow large. Each prime has its own pointer into the ugly number array, generating candidates by multiplication.
**Code Skeleton:**
```python
from typing import List

def nthSuperUglyNumber(n: int, primes: List[int]) -> int:
    ugly = [1]
    # pointers[i] tracks which ugly number primes[i] should multiply next
    pointers = [0] * len(primes)
    for _ in range(1, n):
        # Find next ugly number as the min of all prime * ugly[pointer]
        next_ugly = min(primes[i] * ugly[pointers[i]] for i in range(len(primes)))
        ugly.append(next_ugly)
        # Advance all pointers that generated this minimum (avoid duplicates)
        for i in range(len(primes)):
            if primes[i] * ugly[pointers[i]] == next_ugly:
                pointers[i] += 1
    return ugly[-1]
```

---

### Problem 18. 786. K-th Smallest Prime Fraction
**Archetype:** 8.1 Top K Elements / 8.2 Merge K Sorted
**Type:** Near Miss
**Statement:** You are given a sorted integer array arr containing 1 and prime numbers, where all integers are unique. You are also given an integer k. For every i and j where 0 <= i < j < arr.length, consider the fraction arr[i] / arr[j]. Return the k-th smallest fraction considered.
**Why it fits:** For each denominator `arr[j]`, the fractions with numerators `arr[0]...arr[j-1]` form a sorted sequence. You are merging `n` sorted sequences to find the k-th smallest.
**The Twist:** The heap stores tuples `(fraction_value, numerator_index, denominator_index)`. Python cannot directly compare tuples with floats and ints in a stable way, so you can store the pair of indices and compare cross-multiplied values lazily, or use a min-heap of `(value, i, j)`.
**Code Skeleton:**
```python
from typing import List
import heapq

def kthSmallestPrimeFraction(arr: List[int], k: int) -> List[int]:
    n = len(arr)
    # Min-heap: for each denominator j, start with the smallest numerator i=0
    # Store (value, numerator_idx, denominator_idx)
    min_heap = [(arr[i] / arr[j], i, j) for j in range(1, n) for i in [j - 1]]
    # Actually, better approach: for each j, the sequence is arr[0]/arr[j], arr[1]/arr[j], ...
    # Seed with i=0 for each j
    min_heap = [(arr[0] / arr[j], 0, j) for j in range(1, n)]
    heapq.heapify(min_heap)

    for _ in range(k - 1):
        frac, i, j = heapq.heappop(min_heap)
        if i + 1 < j:
            heapq.heappush(min_heap, (arr[i + 1] / arr[j], i + 1, j))

    _, i, j = min_heap[0]
    return [arr[i], arr[j]]
```

---

### Problem 19. 1753. Maximum Score From Removing Stones
**Archetype:** 8.1 Top K Elements
**Type:** Near Miss
**Statement:** You are playing a game with three piles of stones. On each turn you choose two different non-empty piles, take one stone from each, and add 1 point to your score. Return the maximum score you can get.
**Why it fits:** A game theory problem disguised as a heap problem. On each turn, you should always pick the two largest remaining piles to maximize the number of turns. A max-heap makes this greedy choice trivial.
**The Twist:** The greedy strategy (always take from two largest) is optimal, but proving it requires an insight. The heap simply simulates the optimal strategy efficiently.
**Code Skeleton:**
```python
import heapq

def maximumScore(a: int, b: int, c: int) -> int:
    max_heap = [-a, -b, -c]
    heapq.heapify(max_heap)
    score = 0
    while True:
        first = -heapq.heappop(max_heap)
        second = -heapq.heappop(max_heap)
        if first == 0 or second == 0:
            break
        first -= 1
        second -= 1
        score += 1
        heapq.heappush(max_heap, -first)
        heapq.heappush(max_heap, -second)
    return score
```

---

### Problem 20. 2462. Total Cost to Hire K Workers
**Archetype:** 8.1 Top K Elements
**Type:** Near Miss
**Statement:** You are given a 0-indexed integer array costs where costs[i] is the cost of hiring the i-th worker. You must hire exactly k workers according to specific rules involving the first and last candidates. Return the total cost to hire exactly k workers.
**Why it fits:** The pool of available candidates is the first `candidates` and the last `candidates` workers. As you hire, new workers become available from the center. Two min-heaps (or one heap with indexing) elegantly track the cheapest available worker.
**The Twist:** The available pool shrinks from both ends inward. You must manage two pointers and two heaps (or one heap with a marker) to know which workers are currently eligible for hiring.
**Code Skeleton:**
```python
from typing import List
import heapq

def totalCost(costs: List[int], k: int, candidates: int) -> int:
    n = len(costs)
    left, right = 0, n - 1
    min_heap = []

    # Initial pool from left and right ends
    while left <= right and left < candidates:
        heapq.heappush(min_heap, (costs[left], left))
        left += 1
    while left <= right and n - 1 - right < candidates:
        heapq.heappush(min_heap, (costs[right], right))
        right -= 1

    total = 0
    for _ in range(k):
        cost, idx = heapq.heappop(min_heap)
        total += cost
        # Replenish from the side the hired worker came from
        if left <= right:
            if idx < left:
                heapq.heappush(min_heap, (costs[left], left))
                left += 1
            else:
                heapq.heappush(min_heap, (costs[right], right))
                right -= 1
    return total
```

---

### Problem 21. 621. Task Scheduler
**Archetype:** 8.3 Scheduling/Intervals (Blended with Greedy / Counting)
**Type:** Pattern Blend
**Statement:** You are given an array of CPU tasks, each represented by letters A to Z, and a cooling time n. Return the least number of units of time that the CPU will take to finish all the given tasks.
**Why it fits:** It blends frequency counting with greedy scheduling. The most frequent task dictates the schedule's backbone. A max-heap tracks remaining task counts, and a queue tracks tasks in cooldown.
**The Twist:** It is not purely a heap problem; the heap handles the "what to do next" greedy choice, while a queue (or simulation) enforces the cooling interval. This teaches pairing heaps with other data structures.
**Code Skeleton:**
```python
from typing import List
import heapq
from collections import deque

def leastInterval(tasks: List[str], n: int) -> int:
    count = {}
    for t in tasks:
        count[t] = count.get(t, 0) + 1

    max_heap = [-cnt for cnt in count.values()]
    heapq.heapify(max_heap)
    queue = deque()  # pairs of [-cnt, idleTime]
    time = 0

    while max_heap or queue:
        time += 1
        if max_heap:
            cnt = 1 + heapq.heappop(max_heap)  # increment because values are negative
            if cnt:
                queue.append([cnt, time + n])
        if queue and queue[0][1] == time:
            heapq.heappush(max_heap, queue.popleft()[0])

    return time
```

---

### Problem 22. 1439. Find the Kth Smallest Sum of a Matrix With Sorted Rows
**Archetype:** 8.2 Merge K Sorted (Blended with DP)
**Type:** Pattern Blend
**Statement:** You are given an m x n matrix mat that has its rows sorted in non-decreasing order. You are allowed to choose exactly one element from each row to form an array. Return the k-th smallest array sum among all the arrays.
**Why it fits:** It generalizes "Find K Pairs with Smallest Sums" to multiple dimensions (rows). The heap stores partial sums and the index tuple representing which column was chosen from each processed row.
**The Twist:** The state space grows exponentially with rows, so a visited set is essential to avoid pushing duplicate states. You iteratively build sums row by row, merging the result with the next row at each step.
**Code Skeleton:**
```python
from typing import List
import heapq

def kthSmallest(mat: List[List[int]], k: int) -> int:
    m, n = len(mat), len(mat[0])

    # Start with the sum of the first column of each row
    initial_sum = sum(mat[i][0] for i in range(m))
    # State: (current_sum, tuple of column indices)
    min_heap = [(initial_sum, tuple([0] * m))]
    visited = {tuple([0] * m)}

    for _ in range(k):
        curr_sum, indices = heapq.heappop(min_heap)
        # Try advancing each row's pointer
        for r in range(m):
            if indices[r] + 1 < n:
                new_indices = list(indices)
                new_indices[r] += 1
                new_indices = tuple(new_indices)
                if new_indices not in visited:
                    visited.add(new_indices)
                    new_sum = curr_sum - mat[r][indices[r]] + mat[r][new_indices[r]]
                    heapq.heappush(min_heap, (new_sum, new_indices))

    return curr_sum
```

---

### Problem 23. 378. Kth Smallest Element in a Sorted Matrix
**Archetype:** 8.2 Merge K Sorted (Blended with Binary Search)
**Type:** Pattern Blend
**Statement:** Given an n x n matrix where each row and column is sorted in ascending order, return the k-th smallest element in the matrix.
**Why it fits:** Each row is a sorted list, so the problem is structurally a merge-K problem. However, the matrix structure allows a clever binary search solution as well. The heap approach is more intuitive and generalizable.
**The Twist:** The heap approach treats the first column as initial seeds. Because columns are also sorted, advancing a pointer within its row guarantees the next candidate is larger. A visited set prevents duplicates.
**Code Skeleton:**
```python
from typing import List
import heapq

def kthSmallest(matrix: List[List[int]], k: int) -> int:
    n = len(matrix)
    # Min-heap of (value, row, col)
    min_heap = [(matrix[i][0], i, 0) for i in range(n)]
    heapq.heapify(min_heap)

    for _ in range(k - 1):
        val, r, c = heapq.heappop(min_heap)
        if c + 1 < n:
            heapq.heappush(min_heap, (matrix[r][c + 1], r, c + 1))

    return min_heap[0][0]
```

---

### Problem 24. 2402. Meeting Rooms III
**Archetype:** 8.3 Scheduling/Intervals (Blended with Simulation)
**Type:** Pattern Blend
**Statement:** You are given an integer n representing the number of rooms in a hotel, and a 2D array meetings where meetings[i] = [start_i, end_i]. Return the number of the room that held the most meetings. If there are multiple rooms, return the room with the smallest number.
**Why it fits:** It combines interval scheduling with room assignment simulation. You need two heaps: one for available rooms (min-heap by room number) and one for occupied rooms (min-heap by end time) to know when rooms free up.
**The Twist:** When a meeting starts, you must free all rooms that have finished before or at the start time. If no room is available, the meeting is delayed until the earliest room frees up.
**Code Skeleton:**
```python
from typing import List
import heapq

def mostBooked(n: int, meetings: List[List[int]]) -> int:
    meetings.sort()
    available = list(range(n))  # min-heap of room numbers
    heapq.heapify(available)
    busy = []  # min-heap of (end_time, room_number)
    count = [0] * n

    for start, end in meetings:
        # Free up rooms that have finished by start time
        while busy and busy[0][0] <= start:
            _, room = heapq.heappop(busy)
            heapq.heappush(available, room)

        if available:
            room = heapq.heappop(available)
            heapq.heappush(busy, (end, room))
        else:
            # Wait until the earliest room frees up
            free_time, room = heapq.heappop(busy)
            new_end = free_time + (end - start)
            heapq.heappush(busy, (new_end, room))
        count[room] += 1

    return count.index(max(count))
```

---

### Problem 25. 1962. Remove Stones to Minimize the Total
**Archetype:** 8.1 Top K Elements (Blended with Greedy / Math)
**Type:** Pattern Blend
**Statement:** You are given a 0-indexed integer array piles, where piles[i] represents the number of stones in the i-th pile, and an integer k. Apply k operations where in each operation you choose any pile and remove floor(piles[i] / 2) stones from it. Return the minimum possible total number of stones remaining.
**Why it fits:** It applies the top-K / max-heap pattern to a greedy optimization problem. The optimal strategy is always to halve the current largest pile, which a max-heap provides in O(log n) time per operation.
**The Twist:** The greedy choice is intuitive but must be rigorously applied. The max-heap ensures you never miss a larger pile that became available after a previous halving operation.
**Code Skeleton:**
```python
from typing import List
import heapq

def minStoneSum(piles: List[int], k: int) -> int:
    max_heap = [-p for p in piles]
    heapq.heapify(max_heap)

    for _ in range(k):
        largest = -heapq.heappop(max_heap)
        reduced = largest - (largest // 2)
        heapq.heappush(max_heap, -reduced)

    return -sum(max_heap)
```

---

### Problem 26. 502. IPO
**Archetype:** 8.1 Top K Elements (Blended with Greedy)
**Type:** Interview Sim
**Statement:** Suppose LeetCode will start its IPO soon. In order to sell a good price of its shares to Venture Capital, LeetCode would like to work on some projects to increase its capital. You can complete at most k distinct projects. Return the final maximized capital.
**Why it fits:** A high-frequency interview problem that combines sorting with a max-heap. You sort projects by minimum required capital, then use a max-heap to select the most profitable available project at each step.
**The Twist:** The available project pool changes dynamically as your capital increases. A two-pass approach (sort by capital, then heap by profit) models the dynamic eligibility perfectly.
**Code Skeleton:**
```python
from typing import List
import heapq

def findMaximizedCapital(k: int, w: int, profits: List[int], capital: List[int]) -> int:
    projects = sorted(zip(capital, profits))
    max_heap = []
    idx = 0
    n = len(projects)

    for _ in range(k):
        # Add all projects that can be afforded with current capital
        while idx < n and projects[idx][0] <= w:
            heapq.heappush(max_heap, -projects[idx][1])
            idx += 1
        if not max_heap:
            break
        w += -heapq.heappop(max_heap)

    return w
```

---

### Problem 27. 1705. Maximum Number of Eaten Apples
**Archetype:** 8.3 Scheduling/Intervals (Blended with Greedy / Expiration)
**Type:** Interview Sim
**Statement:** There is a special kind of apple tree that grows apples every day for n days. On the i-th day, the tree grows apples[i] apples that will rot after days[i] days. You can eat at most one apple a day. Return the maximum number of apples you can eat.
**Why it fits:** A greedy scheduling problem where apples have expiration dates. A min-heap ordered by expiration date ensures you always eat the apple that rots soonest, minimizing waste.
**The Twist:** Apples rot. You must discard expired apples before deciding what to eat each day. The heap's top is the most urgent apple, but it might already be rotten.
**Code Skeleton:**
```python
from typing import List
import heapq

def eatenApples(apples: List[int], days: List[int]) -> int:
    min_heap = []  # (rotten_day, apples_count)
    eaten = 0
    n = len(apples)

    for i in range(n):
        if apples[i] > 0:
            heapq.heappush(min_heap, (i + days[i], apples[i]))
        # Eat one apple today if possible
        while min_heap:
            rot_day, count = min_heap[0]
            if rot_day <= i:
                heapq.heappop(min_heap)
            elif count > 0:
                eaten += 1
                if count == 1:
                    heapq.heappop(min_heap)
                else:
                    min_heap[0] = (rot_day, count - 1)
                break
            else:
                heapq.heappop(min_heap)

    # Continue eating remaining apples after growing stops
    day = n
    while min_heap:
        rot_day, count = heapq.heappop(min_heap)
        if rot_day <= day:
            continue
        can_eat = min(count, rot_day - day)
        eaten += can_eat
        day += can_eat

    return eaten
```

---

### Problem 28. 871. Minimum Number of Refueling Stops
**Archetype:** 8.1 Top K Elements (Blended with Greedy / DP)
**Type:** Interview Sim
**Statement:** A car travels from a starting position to a destination which is target miles east of the starting position. Along the way, there are gas stations. Return the minimum number of refueling stops the car must make in order to reach its destination.
**Why it fits:** It is a classic greedy problem solvable with a max-heap. As you pass stations, you add their fuel to a max-heap. When you run out of fuel, you "retroactively" refuel at the station with the most fuel you have passed.
**The Twist:** The decision to refuel is not made at the station; instead, stations are collected in a max-heap, and refueling only happens when necessary. This "lazy greedy" approach is counterintuitive but optimal.
**Code Skeleton:**
```python
from typing import List
import heapq

def minRefuelStops(target: int, startFuel: int, stations: List[List[int]]) -> int:
    # Add destination as a station with 0 fuel to simplify logic
    stations.append([target, 0])
    max_heap = []
    fuel = startFuel
    stops = 0
    prev = 0

    for position, gas in stations:
        distance = position - prev
        fuel -= distance
        # Refuel from past stations if we run out
        while fuel < 0 and max_heap:
            fuel += -heapq.heappop(max_heap)
            stops += 1
        if fuel < 0:
            return -1
        heapq.heappush(max_heap, -gas)
        prev = position

    return stops
```

---

### Problem 29. 1167. Minimum Cost to Connect Sticks
**Archetype:** 8.3 Scheduling/Intervals (Blended with Greedy / Huffman)
**Type:** Interview Sim
**Statement:** You have some number of sticks with positive integer lengths. You can connect any two sticks into one stick by paying a cost equal to the sum of their lengths. Return the minimum cost to connect all the sticks into one stick.
**Why it fits:** This is the classic Huffman coding problem in disguise. The greedy strategy is always to combine the two smallest sticks, which a min-heap facilitates. It tests understanding of optimal merge patterns.
**The Twist:** The cost accumulates multiplicatively in terms of how many times a stick is merged. Always combining the two smallest minimizes the total cost, which is exactly the Huffman algorithm.
**Code Skeleton:**
```python
from typing import List
import heapq

def connectSticks(sticks: List[int]) -> int:
    if len(sticks) <= 1:
        return 0
    heapq.heapify(sticks)
    total_cost = 0
    while len(sticks) > 1:
        first = heapq.heappop(sticks)
        second = heapq.heappop(sticks)
        cost = first + second
        total_cost += cost
        heapq.heappush(sticks, cost)
    return total_cost
```

---

### Problem 30. 1801. Number of Orders in the Backlog
**Archetype:** 8.3 Scheduling/Intervals (Blended with Simulation)
**Type:** Interview Sim
**Statement:** You are given a 2D integer array orders where each orders[i] = [price_i, amount_i, orderType_i]. The backlog contains orders that have not been executed. Return the total amount of orders in the backlog after placing all the orders.
**Why it fits:** A complex simulation problem requiring two heaps: a min-heap for sell orders (backlog asks) and a max-heap for buy orders (backlog bids). Orders are matched immediately if prices overlap.
**The Twist:** You must manage two separate order books and match greedily. The heap tops represent the best available prices. A sell order matches with the highest buy price >= sell price, and vice versa.
**Code Skeleton:**
```python
from typing import List
import heapq

def getNumberOfBacklogOrders(orders: List[List[int]]) -> int:
    MOD = 10**9 + 7
    buy_heap = []  # max-heap of [-price, amount]
    sell_heap = []  # min-heap of [price, amount]

    for price, amount, order_type in orders:
        if order_type == 0:  # Buy order
            while amount > 0 and sell_heap and sell_heap[0][0] <= price:
                sell_price, sell_amount = heapq.heappop(sell_heap)
                trade = min(amount, sell_amount)
                amount -= trade
                sell_amount -= trade
                if sell_amount > 0:
                    heapq.heappush(sell_heap, [sell_price, sell_amount])
            if amount > 0:
                heapq.heappush(buy_heap, [-price, amount])
        else:  # Sell order
            while amount > 0 and buy_heap and -buy_heap[0][0] >= price:
                buy_price, buy_amount = heapq.heappop(buy_heap)
                buy_price = -buy_price
                trade = min(amount, buy_amount)
                amount -= trade
                buy_amount -= trade
                if buy_amount > 0:
                    heapq.heappush(buy_heap, [-buy_price, buy_amount])
            if amount > 0:
                heapq.heappush(sell_heap, [price, amount])

    total = 0
    for _, amount in buy_heap:
        total = (total + amount) % MOD
    for _, amount in sell_heap:
        total = (total + amount) % MOD
    return total
```

---
