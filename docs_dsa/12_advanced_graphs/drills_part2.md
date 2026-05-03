# Pattern 12: Advanced Graphs - Drills Part 2
## Warm-Ups + Core Drills (15 Problems)

---

### 1. 743. Network Delay Time
**Archetype:** 12.1 Dijkstra
**Type:** Warm-Up
**Statement:** Given a list of travel times between nodes, return the time it takes for all nodes to receive a signal sent from node k.
**Why it fits:** This is the canonical single-source shortest path problem with non-negative weights. Dijkstra's algorithm with a min-heap is the standard solution.
**The Twist:** You must check if all nodes are reachable. If any node has distance infinity, return -1.
**Code Skeleton:**
```python
import heapq

def networkDelayTime(times: list[list[int]], n: int, k: int) -> int:
    graph = [[] for _ in range(n + 1)]
    for u, v, w in times:
        graph[u].append((v, w))

    dist = [float('inf')] * (n + 1)
    dist[k] = 0
    heap = [(0, k)]

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))

    max_dist = max(dist[1:])
    return max_dist if max_dist != float('inf') else -1
```

### 2. 1584. Min Cost to Connect All Points
**Archetype:** 12.4 MST (Prim/Kruskal)
**Type:** Warm-Up
**Statement:** Given an array of points, return the minimum cost to make all points connected.
**Why it fits:** This is the canonical Minimum Spanning Tree (MST) problem on a complete graph where edge weights are Manhattan distances.
**The Twist:** The graph is implicit (complete graph with O(N^2) edges). Prim's algorithm with a min-heap is preferred because you can generate edges lazily.
**Code Skeleton:**
```python
import heapq

def minCostConnectPoints(points: list[list[int]]) -> int:
    n = len(points)
    visited = [False] * n
    min_heap = [(0, 0)]  # (cost, point)
    total_cost = 0
    edges_used = 0

    while edges_used < n:
        cost, u = heapq.heappop(min_heap)
        if visited[u]:
            continue
        visited[u] = True
        total_cost += cost
        edges_used += 1
        for v in range(n):
            if not visited[v]:
                manhattan = abs(points[u][0] - points[v][0]) + abs(points[u][1] - points[v][1])
                heapq.heappush(min_heap, (manhattan, v))
    return total_cost
```

### 3. 547. Number of Provinces
**Archetype:** 12.5 Union-Find
**Type:** Warm-Up
**Statement:** Given an adjacency matrix of friendships, find the total number of provinces.
**Why it fits:** This is a classic Union-Find problem. Each friendship is a union operation, and the final count of disjoint sets is the number of provinces.
**The Twist:** The input is an adjacency matrix, not an edge list. You must iterate over the upper triangle (or all entries) to perform unions.
**Code Skeleton:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.count = n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        self.parent[py] = px
        self.count -= 1

def findCircleNum(isConnected: list[list[int]]) -> int:
    n = len(isConnected)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j] == 1:
                uf.union(i, j)
    return uf.count
```

### 4. 684. Redundant Connection
**Archetype:** 12.5 Union-Find
**Type:** Warm-Up
**Statement:** Return an edge that can be removed so that the result is a tree of n nodes.
**Why it fits:** This is a direct application of Union-Find cycle detection. The first edge that connects two already-connected nodes creates a cycle and is the redundant connection.
**The Twist:** If there are multiple answers, return the one that appears last in the input. Union-Find naturally identifies the first edge that closes a cycle.
**Code Skeleton:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n + 1))

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        self.parent[py] = px
        return True

def findRedundantConnection(edges: list[list[int]]) -> list[int]:
    uf = UnionFind(len(edges))
    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]
    return []
```

### 5. 1631. Path With Minimum Effort
**Archetype:** 12.1 Dijkstra
**Type:** Warm-Up
**Statement:** Return the minimum effort required to travel from top-left to bottom-right, where effort is the maximum absolute difference in heights between two consecutive cells.
**Why it fits:** This is a shortest path problem where the path cost is the maximum edge weight along the path, not the sum. Modified Dijkstra works because the cost function is monotonic.
**The Twist:** The relaxation condition changes from `dist[u] + w < dist[v]` to `max(dist[u], w) < dist[v]`. You are minimizing the maximum edge weight on the path.
**Code Skeleton:**
```python
import heapq

def minimumEffortPath(heights: list[list[int]]) -> int:
    rows, cols = len(heights), len(heights[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        effort, r, c = heapq.heappop(heap)
        if r == rows - 1 and c == cols - 1:
            return effort
        if effort > dist[r][c]:
            continue
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                new_effort = max(effort, abs(heights[r][c] - heights[nr][nc]))
                if new_effort < dist[nr][nc]:
                    dist[nr][nc] = new_effort
                    heapq.heappush(heap, (new_effort, nr, nc))
    return 0
```

### 6. 787. Cheapest Flights Within K Stops
**Archetype:** 12.1 Dijkstra / 12.2 Bellman-Ford
**Type:** Core Drill
**Statement:** Find the cheapest price from src to dst with at most k stops.
**Why it fits:** This is a shortest path problem with an additional constraint (number of stops). Both Bellman-Ford (K iterations) and modified Dijkstra (state includes stops) work.
**The Twist:** Standard Dijkstra fails because the shortest path in terms of cost may use too many stops. You must track the minimum cost to reach each node with exactly `s` stops.
**Code Skeleton:**
```python
from collections import deque

def findCheapestPrice(n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int:
    graph = [[] for _ in range(n)]
    for u, v, w in flights:
        graph[u].append((v, w))

    # BFS with at most k stops (Bellman-Ford style)
    dist = [float('inf')] * n
    dist[src] = 0
    queue = deque([(src, 0, 0)])  # node, cost, stops

    while queue:
        node, cost, stops = queue.popleft()
        if stops > k:
            continue
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                queue.append((neighbor, new_cost, stops + 1))

    return dist[dst] if dist[dst] != float('inf') else -1
```

### 7. 1334. Find the City With the Smallest Number of Neighbors at a Threshold Distance
**Archetype:** 12.3 Floyd-Warshall
**Type:** Core Drill
**Statement:** Return the city with the smallest number of reachable cities within a distance threshold.
**Why it fits:** This is an all-pairs shortest path problem. Floyd-Warshall is natural here because n <= 100, making O(n^3) acceptable and simpler to implement than n Dijkstra runs.
**The Twist:** You need shortest paths between every pair of cities, then count how many are within the threshold. Ties are broken by returning the city with the greatest number.
**Code Skeleton:**
```python
def findTheCity(n: int, edges: list[list[int]], distanceThreshold: int) -> int:
    dist = [[float('inf')] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = w
        dist[v][u] = w

    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    min_count = n
    ans = -1
    for i in range(n):
        count = sum(1 for j in range(n) if i != j and dist[i][j] <= distanceThreshold)
        if count <= min_count:
            min_count = count
            ans = i
    return ans
```

### 8. 1168. Optimize Water Distribution in a Village
**Archetype:** 12.4 MST (Prim/Kruskal)
**Type:** Core Drill
**Statement:** Return the minimum cost to supply water to all houses, either by building wells or laying pipes.
**Why it fits:** This is an MST problem on a graph with a virtual node. Each house can either connect to another house (pipe) or to a virtual well node (well cost).
**The Twist:** You must introduce a virtual node (node 0) connected to every house with edge weight equal to the well cost. Then run Kruskal or Prim on this augmented graph.
**Code Skeleton:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.count = n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        self.parent[py] = px
        self.count -= 1
        return True

def minCostToSupplyWater(n: int, wells: list[int], pipes: list[list[int]]) -> int:
    edges = []
    for u, v, w in pipes:
        edges.append((w, u - 1, v - 1))
    for i, cost in enumerate(wells):
        edges.append((cost, i, n))  # virtual well node

    edges.sort()
    uf = UnionFind(n + 1)
    total = 0
    for w, u, v in edges:
        if uf.union(u, v):
            total += w
        if uf.count == 1:
            break
    return total
```

### 9. 721. Accounts Merge
**Archetype:** 12.5 Union-Find
**Type:** Core Drill
**Statement:** Given a list of accounts where each account has a name and emails, merge accounts with common emails.
**Why it fits:** This is Union-Find on emails. Emails are the nodes, and accounts are the edges connecting all emails within the same account.
**The Twist:** You must map emails to indices for Union-Find, then group by root and sort emails. The name is just metadata attached to the account.
**Code Skeleton:**
```python
from collections import defaultdict

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        self.parent[self.find(x)] = self.find(y)

def accountsMerge(accounts: list[list[str]]) -> list[list[str]]:
    email_to_id = {}
    email_to_name = {}
    id_counter = 0

    for acc in accounts:
        name = acc[0]
        for email in acc[1:]:
            if email not in email_to_id:
                email_to_id[email] = id_counter
                email_to_name[email] = name
                id_counter += 1

    uf = UnionFind(id_counter)
    for acc in accounts:
        first_id = email_to_id[acc[1]]
        for email in acc[2:]:
            uf.union(first_id, email_to_id[email])

    groups = defaultdict(list)
    for email, idx in email_to_id.items():
        groups[uf.find(idx)].append(email)

    ans = []
    for emails in groups.values():
        ans.append([email_to_name[emails[0]]] + sorted(emails))
    return ans
```

### 10. 1319. Number of Operations to Make Network Connected
**Archetype:** 12.5 Union-Find
**Type:** Core Drill
**Statement:** Return the minimum number of times you need to move an edge to make the graph connected.
**Why it fits:** This is a connectivity problem. A connected graph with n nodes needs at least n-1 edges. The number of redundant edges must be at least the number of disjoint components minus one.
**The Twist:** If there are fewer than n-1 edges total, it is impossible. Otherwise, the answer is the number of connected components minus one.
**Code Skeleton:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.count = n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        self.parent[py] = px
        self.count -= 1
        return True

def makeConnected(n: int, connections: list[list[int]]) -> int:
    if len(connections) < n - 1:
        return -1
    uf = UnionFind(n)
    for u, v in connections:
        uf.union(u, v)
    return uf.count - 1
```

### 11. 1192. Critical Connections in a Network
**Archetype:** 12.6 Tarjan (SCC/Bridges)
**Type:** Core Drill
**Statement:** Given a network of n servers, return all critical connections (bridges).
**Why it fits:** This is the canonical bridges problem solved by Tarjan's algorithm. A bridge is an edge that, if removed, increases the number of connected components.
**The Twist:** You must track discovery times and low-link values. An edge (u, v) is a bridge if `low[v] > disc[u]`, meaning v cannot reach back to u or any ancestor of u without using the edge (u, v).
**Code Skeleton:**
```python
def criticalConnections(n: int, connections: list[list[int]]) -> list[list[int]]:
    graph = [[] for _ in range(n)]
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)

    disc = [-1] * n
    low = [0] * n
    time = 0
    bridges = []

    def dfs(node, parent):
        nonlocal time
        disc[node] = low[node] = time
        time += 1
        for neighbor in graph[node]:
            if neighbor == parent:
                continue
            if disc[neighbor] == -1:
                dfs(neighbor, node)
                low[node] = min(low[node], low[neighbor])
                if low[neighbor] > disc[node]:
                    bridges.append([node, neighbor])
            else:
                low[node] = min(low[node], disc[neighbor])

    dfs(0, -1)
    return bridges
```

### 12. 1489. Find Critical and Pseudo-Critical Edges in MST
**Archetype:** 12.4 MST (Prim/Kruskal)
**Type:** Core Drill
**Statement:** Given a weighted undirected graph, classify edges as critical (appear in all MSTs) or pseudo-critical (appear in some MSTs).
**Why it fits:** This is an advanced MST problem. You must understand that an edge is critical if excluding it increases the MST weight, and pseudo-critical if including it in the MST does not increase the weight beyond the optimal.
**The Twist:** You must run Kruskal multiple times: once for the baseline MST, once excluding each edge, and once forcing each edge to be included.
**Code Skeleton:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

class Solution:
    def findCriticalAndPseudoCriticalEdges(self, n: int, edges: list[list[int]]) -> list[list[int]]:
        # Add original index to edges
        edges = [(u, v, w, i) for i, (u, v, w) in enumerate(edges)]
        edges.sort(key=lambda x: x[2])

        def mst_weight(skip_edge=-1, force_edge=-1):
            uf = UnionFind(n)
            weight = 0
            edges_used = 0
            if force_edge != -1:
                u, v, w, _ = edges[force_edge]
                uf.union(u, v)
                weight += w
                edges_used += 1
            for i, (u, v, w, _) in enumerate(edges):
                if i == skip_edge:
                    continue
                if uf.union(u, v):
                    weight += w
                    edges_used += 1
            return weight if edges_used == n - 1 else float('inf')

        baseline = mst_weight()
        critical = []
        pseudo = []
        for i in range(len(edges)):
            if mst_weight(skip_edge=i) > baseline:
                critical.append(edges[i][3])
            elif mst_weight(force_edge=i) == baseline:
                pseudo.append(edges[i][3])
        return [critical, pseudo]
```

### 13. 778. Swim in Rising Water
**Archetype:** 12.1 Dijkstra
**Type:** Core Drill
**Statement:** Return the least time until you can reach the bottom-right square from the top-left square, where the water level in each square is given.
**Why it fits:** This is a modified Dijkstra where the cost to reach a cell is the maximum elevation encountered along the path. You are minimizing the maximum elevation.
**The Twist:** The cost function is the maximum, not the sum. The relaxation condition is `max(dist[u], elevation[v]) < dist[v]`. This is sometimes called "widest path" or "minimax path."
**Code Skeleton:**
```python
import heapq

def swimInWater(grid: list[list[int]]) -> int:
    n = len(grid)
    dist = [[float('inf')] * n for _ in range(n)]
    dist[0][0] = grid[0][0]
    heap = [(grid[0][0], 0, 0)]

    while heap:
        time, r, c = heapq.heappop(heap)
        if r == n - 1 and c == n - 1:
            return time
        if time > dist[r][c]:
            continue
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                new_time = max(time, grid[nr][nc])
                if new_time < dist[nr][nc]:
                    dist[nr][nc] = new_time
                    heapq.heappush(heap, (new_time, nr, nc))
    return -1
```

### 14. 1368. Minimum Cost to Make at Least One Valid Path
**Archetype:** 12.1 Dijkstra
**Type:** Core Drill
**Statement:** Given a grid with arrow signs, return the minimum cost to make at least one valid path from top-left to bottom-right.
**Why it fits:** This is a 0-1 BFS problem (or Dijkstra with weights 0 and 1). Moving along the arrow costs 0; modifying the arrow costs 1.
**The Twist:** Standard BFS does not work because edges have weights. Dijkstra or 0-1 BFS (deque) is needed because the graph is weighted, even though weights are only 0 or 1.
**Code Skeleton:**
```python
from collections import deque

def minCost(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    # right=1, left=2, down=3, up=4
    dirs = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}

    while dq:
        r, c = dq.popleft()
        for sign, (dr, dc) in dirs.items():
            nr, nc = r + dr, c + dc
            cost = 0 if grid[r][c] == sign else 1
            if 0 <= nr < rows and 0 <= nc < cols and dist[r][c] + cost < dist[nr][nc]:
                dist[nr][nc] = dist[r][c] + cost
                if cost == 0:
                    dq.appendleft((nr, nc))
                else:
                    dq.append((nr, nc))
    return dist[rows-1][cols-1]
```

### 15. 1928. Minimum Cost to Reach Destination in Time
**Archetype:** 12.1 Dijkstra
**Type:** Core Drill
**Statement:** Return the minimum cost to reach the destination within maxTime, where passing fees are paid at each node.
**Why it fits:** This is a constrained shortest path problem. The state must include both the current node and the time spent so far, because the same node may be reached with different times and costs.
**The Twist:** You cannot simply track the minimum cost to each node. You must track the minimum cost to reach each node at each possible time (or prune dominated states).
**Code Skeleton:**
```python
import heapq

def minCost(maxTime: int, edges: list[list[int]], passingFees: list[int]) -> int:
    n = len(passingFees)
    graph = [[] for _ in range(n)]
    for u, v, t in edges:
        graph[u].append((v, t))
        graph[v].append((u, t))

    # dist[node] = min cost to reach node with time <= maxTime
    # state: (cost, time, node)
    heap = [(passingFees[0], 0, 0)]
    min_time = [float('inf')] * n
    min_time[0] = 0

    while heap:
        cost, time, node = heapq.heappop(heap)
        if node == n - 1:
            return cost
        for neighbor, travel in graph[node]:
            new_time = time + travel
            if new_time <= maxTime and new_time < min_time[neighbor]:
                min_time[neighbor] = new_time
                heapq.heappush(heap, (cost + passingFees[neighbor], new_time, neighbor))
    return -1
```
