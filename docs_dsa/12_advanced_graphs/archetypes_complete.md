# Pattern 12: Advanced Graphs — Complete Archetype Map

> **Pattern Recognition:** When you see "shortest path weighted", "minimum spanning tree", "all pairs shortest", "negative edges", "strongly connected", "disjoint sets" — think advanced graphs.
>
> **Fundamental Insight:** Different edge constraints (weights, negatives, density) demand different algorithms. Picking the wrong one means TLE or wrong answers. Know the cost model and graph properties before coding.

---

## Archetype 12.1: Dijkstra (Shortest Path)

### Recognition Signal (10 seconds)
Words: **"shortest path", "minimum cost", "network delay", "weighted", "non-negative", "reach destination", "cheapest flight"**

The question is always: **"Find the minimum cost/distance/time from a source to one or all nodes in a graph with non-negative edge weights."**

### Core Structure
```python
import heapq

def dijkstra(graph, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    heap = [(0, start)]  # (distance, node)

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue  # Stale entry
        for neighbor, weight in graph[node]:
            nd = d + weight
            if nd < dist[neighbor]:
                dist[neighbor] = nd
                heapq.heappush(heap, (nd, neighbor))
    return dist
```

### The Invariant
Once a node is popped from the priority queue, its shortest distance from the source is finalized. This holds because all edge weights are non-negative, so no future path can be shorter.

### Canonical Problem: Network Delay Time (LeetCode 743)
**Statement:** Given times[i] = (u, v, w), send signal from node k. Return time for all nodes to receive it.

```python
import heapq
from collections import defaultdict

class Solution:
    def networkDelayTime(self, times, n, k):
        graph = defaultdict(list)
        for u, v, w in times:
            graph[u].append((v, w))

        dist = {i: float('inf') for i in range(1, n+1)}
        dist[k] = 0
        heap = [(0, k)]

        while heap:
            d, node = heapq.heappop(heap)
            if d > dist[node]:
                continue
            for neighbor, weight in graph[node]:
                nd = d + weight
                if nd < dist[neighbor]:
                    dist[neighbor] = nd
                    heapq.heappush(heap, (nd, neighbor))

        max_dist = max(dist.values())
        return max_dist if max_dist != float('inf') else -1
```

### Variation Family

**V1: Path With Maximum Minimum Value (LeetCode 1102)**
- **Twist:** Find path from top-left to bottom-right maximizing the minimum cell value
- **Change:** Max-heap Dijkstra variant. Track path "score" as max of minima.

**V2: Cheapest Flights Within K Stops (LeetCode 787)**
- **Twist:** Shortest path with at most K edges
- **Change:** Dijkstra with state (node, stops). Or Bellman-Ford for K iterations. See Archetype 12.2.

**V3: Swim in Rising Water (LeetCode 778)**
- **Twist:** Grid where water level rises. Find minimum time to reach bottom-right.
- **Change:** Dijkstra on grid. Cost to enter cell = max(current_cost, cell_value).

```python
import heapq

def swimInWater(grid):
    n = len(grid)
    visited = [[False] * n for _ in range(n)]
    heap = [(grid[0][0], 0, 0)]  # (max elevation so far, r, c)
    while heap:
        t, r, c = heapq.heappop(heap)
        if r == n - 1 and c == n - 1:
            return t
        if visited[r][c]:
            continue
        visited[r][c] = True
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc]:
                heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))
```

**V4: Reachable Nodes In Subdivided Graph (LeetCode 882)**
- **Twist:** Edges can be subdivided into smaller edges with intermediate nodes
- **Change:** Dijkstra to find shortest paths. Then count reachable original + new nodes.

**Near Miss: Shortest Path with Negative Weights**
- **Looks like:** Shortest path
- **But:** Dijkstra fails with negative edges. Use Bellman-Ford instead.
- **Lesson:** Dijkstra requires non-negative weights. Always verify edge constraints.

---

## Archetype 12.2: Bellman-Ford

### Recognition Signal (10 seconds)
Words: **"negative edge", "shortest path with negative weights", "detect negative cycle", "at most K edges"**

The question is always: **"Find shortest paths when edge weights can be negative, or when we are limited to at most K edges."**

### Core Structure
```python
def bellman_ford(edges, n, start):
    dist = [float('inf')] * n
    dist[start] = 0

    # Relax all edges n-1 times
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break

    # Check for negative cycles
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None  # Negative cycle detected
    return dist
```

### The Invariant
After i iterations of relaxation, the shortest path using at most i edges is found. After n-1 iterations, all shortest paths are found (unless a negative cycle exists, which can be detected in the nth iteration).

### Canonical Problem: Cheapest Flights Within K Stops (LeetCode 787)
**Statement:** Find cheapest price from src to dst with at most k stops (k+1 edges).

```python
class Solution:
    def findCheapestPrice(self, n, flights, src, dst, k):
        dist = [float('inf')] * n
        dist[src] = 0

        # Relax at most k+1 times (k stops = k+1 edges)
        for _ in range(k + 1):
            new_dist = dist[:]  # Snapshot to prevent using same iteration's updates
            for u, v, w in flights:
                if dist[u] != float('inf') and dist[u] + w < new_dist[v]:
                    new_dist[v] = dist[u] + w
            dist = new_dist

        return dist[dst] if dist[dst] != float('inf') else -1
```

### Variation Family

**V1: Network Delay Time (with Bellman-Ford)**
- **Twist:** Same as Dijkstra canonical, but can be solved with Bellman-Ford for dense graphs or when negatives exist
- **Change:** O(VE) vs O((V+E) log V). Simpler code, worse complexity.

**V2: Find the City With the Smallest Number of Neighbors at a Threshold Distance (LeetCode 1334)**
- **Twist:** For each city, count neighbors within distance threshold. Return city with minimum count.
- **Change:** Run Bellman-Ford (or Dijkstra) from every node. O(V * E log V) or O(V^2 E).

**V3: Single-Source Shortest Path with Negative Cycle Detection**
- **Twist:** Return shortest paths or detect if any negative cycle is reachable
- **Change:** Run the nth relaxation. If any distance updates, negative cycle exists.

```python
def shortestPathWithNegativeCycle(n, edges, start):
    dist = [float('inf')] * n
    dist[start] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    # Check negative cycle
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None  # Negative cycle reachable
    return dist
```

**Near Miss: Dijkstra with Negative Weights (wrong approach)**
- **Looks like:** Same shortest path
- **But:** Dijkstra greedily finalizes nodes. Negative edges can provide shorter paths later.
- **Lesson:** Bellman-Ford handles negatives. Dijkstra does not.

---

## Archetype 12.3: Floyd-Warshall

### Recognition Signal (10 seconds)
Words: **"all pairs shortest path", "distance between every pair", "transitive closure", "shortest path for every node", "dense graph"**

The question is always: **"Find shortest paths between ALL pairs of nodes."**

### Core Structure
```python
def floyd_warshall(n, edges):
    # Initialize distance matrix
    dist = [[float('inf')] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)

    # Main triple loop
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist
```

### The Invariant
After the k-th iteration of the outer loop, `dist[i][j]` contains the shortest path from i to j using only intermediate nodes from the set {0, 1, ..., k-1}. Gradually allowing more intermediates refines the shortest paths.

### Canonical Problem: Find the City With the Smallest Number of Neighbors at a Threshold Distance (LeetCode 1334)
**Statement:** Given n cities and edges, find city with fewest reachable cities within distanceThreshold.

```python
class Solution:
    def findTheCity(self, n, edges, distanceThreshold):
        dist = [[float('inf')] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
        for u, v, w in edges:
            dist[u][v] = w
            dist[v][u] = w

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

        min_count = n
        result = -1
        for i in range(n):
            count = sum(1 for j in range(n) if i != j and dist[i][j] <= distanceThreshold)
            if count <= min_count:
                min_count = count
                result = i
        return result
```

### Variation Family

**V1: Find the Shortest Superstring (LeetCode 943)**
- **Twist:** Find shortest string containing all given strings as substrings
- **Change:** Precompute overlap between every pair. TSP DP on overlap graph (not pure Floyd-Warshall, but uses all-pairs preprocessing).

**V2: Course Schedule IV (LeetCode 1462)**
- **Twist:** Given prerequisites, answer queries whether course u is a prerequisite of course v
- **Change:** Transitive closure of DAG. Floyd-Warshall on adjacency matrix (boolean version).

```python
def checkIfPrerequisite(n, prerequisites, queries):
    reachable = [[False] * n for _ in range(n)]
    for u, v in prerequisites:
        reachable[u][v] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reachable[i][k] and reachable[k][j]:
                    reachable[i][j] = True
    return [reachable[u][v] for u, v in queries]
```

**V3: Odd Even Jump (LeetCode 975)**
- **Twist:** Can you reach the end with alternating odd/even jump rules?
- **Change:** Precompute next odd/even jump targets using monotonic stacks + sorting. Then DP.

**Near Miss: Dijkstra from Every Node**
- **Looks like:** All-pairs shortest path
- **But:** Running Dijkstra V times is O(V * (E log V)), which beats Floyd-Warshall O(V^3) on sparse graphs.
- **Lesson:** Floyd-Warshall wins on dense graphs or very small V. For sparse graphs, V * Dijkstra is faster.

---

## Archetype 12.4: MST (Prim / Kruskal)

### Recognition Signal (10 seconds)
Words: **"minimum spanning tree", "connect all points", "minimum cost", "cable company", "network", "MST", "Prim", "Kruskal"**

The question is always: **"Connect all nodes with minimum total edge weight, forming a tree with no cycles."**

### Core Structure (Prim)
```python
import heapq

def prim(graph, n, start=0):
    visited = [False] * n
    min_heap = [(0, start)]  # (weight, node)
    total_cost = 0
    edges_used = 0

    while min_heap and edges_used < n:
        weight, node = heapq.heappop(min_heap)
        if visited[node]:
            continue
        visited[node] = True
        total_cost += weight
        edges_used += 1
        for neighbor, w in graph[node]:
            if not visited[neighbor]:
                heapq.heappush(min_heap, (w, neighbor))
    return total_cost
```

### Core Structure (Kruskal)
```python
def kruskal(edges, n):
    edges.sort(key=lambda x: x[2])  # Sort by weight
    uf = UnionFind(n)
    total_cost = 0
    edges_used = 0
    for u, v, w in edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            total_cost += w
            edges_used += 1
            if edges_used == n - 1:
                break
    return total_cost
```

### The Invariant
Prim grows a single tree from a starting node, always adding the cheapest edge connecting the tree to a new node. Kruskal sorts all edges globally and adds the cheapest edge that connects two disjoint components. Both are greedy and correct by the cut property.

### Canonical Problem: Min Cost to Connect All Points (LeetCode 1584)
**Statement:** Connect all points with minimum total Manhattan distance.

```python
import heapq

class Solution:
    def minCostConnectPoints(self, points):
        n = len(points)
        visited = [False] * n
        heap = [(0, 0)]  # (cost, point_index)
        total = 0
        edges = 0

        while edges < n:
            cost, i = heapq.heappop(heap)
            if visited[i]:
                continue
            visited[i] = True
            total += cost
            edges += 1
            for j in range(n):
                if not visited[j]:
                    manhattan = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
                    heapq.heappush(heap, (manhattan, j))
        return total
```

### Variation Family

**V1: Optimize Water Distribution in a Village (LeetCode 1168)**
- **Twist:** Build wells at houses OR connect houses with pipes
- **Change:** Add a virtual node 0. Edge from 0 to house i = cost to build well. Run MST.

**V2: Find Critical and Pseudo-Critical Edges in MST (LeetCode 1489)**
- **Twist:** Classify edges as critical (must be in every MST), pseudo-critical (in some MST), or neither
- **Change:** For each edge, test if excluding it increases MST weight (critical), or if forcing it yields same MST weight (pseudo-critical).

**V3: Connecting Cities With Minimum Cost (LeetCode 1135)**
- **Twist:** Standard MST on explicit edge list
- **Change:** Kruskal with Union-Find is simplest.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n+1))
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py:
            self.parent[px] = py

def minimumCost(n, connections):
    connections.sort(key=lambda x: x[2])
    uf = UnionFind(n)
    cost = 0
    edges = 0
    for u, v, w in connections:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            cost += w
            edges += 1
            if edges == n - 1:
                return cost
    return -1
```

**Near Miss: Number of Islands (LeetCode 200)**
- **Looks like:** Connecting components
- **But:** Counting components, not minimizing connection cost. Simple DFS/BFS.
- **Lesson:** MST is about minimum cost spanning. Connected components is about reachability.

---

## Archetype 12.5: Union-Find

### Recognition Signal (10 seconds)
Words: **"connected components", "union", "find", "disjoint set", "equations possible", "redundant connection", "grouping"**

The question is always: **"Track connectivity of elements as edges are added dynamically, and answer whether two elements are in the same set."**

### Core Structure
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n  # Or size array

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
```

### The Invariant
Path compression keeps the tree flat, making future queries nearly O(1). Union by rank/size keeps tree height logarithmic. Combined, amortized time per operation is O(alpha(n)), effectively constant.

### Canonical Problem: Redundant Connection (LeetCode 684)
**Statement:** An undirected graph that started as a tree has one extra edge. Find that edge.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n+1))
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        self.parent[px] = py
        return True

class Solution:
    def findRedundantConnection(self, edges):
        uf = UnionFind(len(edges))
        for u, v in edges:
            if not uf.union(u, v):
                return [u, v]
        return []
```

### Variation Family

**V1: Number of Provinces (Union-Find version) (LeetCode 547)**
- **Twist:** Count connected components using UF instead of DFS
- **Change:** Union all edges. Count unique parents at the end.

```python
def findCircleNum(isConnected):
    n = len(isConnected)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i+1, n):
            if isConnected[i][j] == 1:
                uf.union(i, j)
    return len(set(uf.find(i) for i in range(n)))
```

**V2: Satisfiability of Equality Equations (LeetCode 990)**
- **Twist:** Equations of form a==b or a!=b. Determine if all can be satisfied.
- **Change:** Union all '==' equations first. Then verify all '!=' equations don't share a root.

**V3: Longest Consecutive Sequence (LeetCode 128)**
- **Twist:** Find longest consecutive elements sequence in unsorted array
- **Change:** Union-Find on value graph: union x with x+1 if both exist. Find max component size.

```python
def longestConsecutive(nums):
    if not nums:
        return 0
    uf = UnionFind(len(nums))
    index = {num: i for i, num in enumerate(nums)}
    for num in index:
        if num + 1 in index:
            uf.union(index[num], index[num+1])
    from collections import Counter
    count = Counter(uf.find(i) for i in range(len(nums)))
    return max(count.values())
```

**V4: Accounts Merge (LeetCode 721)**
- **Twist:** Merge accounts with shared emails
- **Change:** Map emails to indices. Union accounts sharing emails. Then group by root.

**Near Miss: Course Schedule (LeetCode 207)**
- **Looks like:** Connectivity and cycles
- **But:** Directed graph. Union-Find only handles undirected connectivity. Use topological sort or DFS cycle detection.
- **Lesson:** Union-Find is for undirected equivalence classes, not directed dependencies.

---

## Archetype 12.6: Tarjan (SCC / Bridges)

### Recognition Signal (10 seconds)
Words: **"critical connections", "bridges", "articulation points", "strongly connected components", "cut edges", "remove edge disconnects"**

The question is always: **"Find edges or nodes whose removal increases the number of connected components."** or **"Find maximal strongly connected subgraphs."**

### Core Structure (Bridges)
```python
def find_bridges(n, connections):
    graph = [[] for _ in range(n)]
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)

    disc = [-1] * n  # Discovery time
    low = [-1] * n   # Lowest reachable discovery time
    time = [0]
    bridges = []

    def dfs(node, parent):
        disc[node] = low[node] = time[0]
        time[0] += 1
        for neighbor in graph[node]:
            if neighbor == parent:
                continue
            if disc[neighbor] == -1:
                dfs(neighbor, node)
                low[node] = min(low[node], low[neighbor])
                if low[neighbor] > disc[node]:
                    bridges.append([node, neighbor])
            else:
                # Back edge
                low[node] = min(low[node], disc[neighbor])

    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)
    return bridges
```

### The Invariant
`disc[node]` is the discovery time in DFS. `low[node]` is the lowest discovery time reachable from `node` using zero or more tree edges and at most one back edge. If `low[child] > disc[node]`, no back edge from child's subtree reaches above `node`, so the edge (node, child) is a bridge.

### Canonical Problem: Critical Connections in a Network (LeetCode 1192)
**Statement:** Find all critical connections (bridges) in a network.

```python
class Solution:
    def criticalConnections(self, n, connections):
        graph = [[] for _ in range(n)]
        for u, v in connections:
            graph[u].append(v)
            graph[v].append(u)

        disc = [-1] * n
        low = [-1] * n
        time = [0]
        res = []

        def dfs(node, parent):
            disc[node] = low[node] = time[0]
            time[0] += 1
            for neighbor in graph[node]:
                if neighbor == parent:
                    continue
                if disc[neighbor] == -1:
                    dfs(neighbor, node)
                    low[node] = min(low[node], low[neighbor])
                    if low[neighbor] > disc[node]:
                        res.append([node, neighbor])
                else:
                    low[node] = min(low[node], disc[neighbor])

        dfs(0, -1)
        return res
```

### Variation Family

**V1: Articulation Points (similar to bridges)**
- **Twist:** Find nodes whose removal disconnects the graph
- **Change:** A node is an articulation point if it has a child with `low[child] >= disc[node]` (for root, needs at least two children in DFS tree).

**V2: Strongly Connected Components (Kosaraju / Tarjan)**
- **Twist:** Find all SCCs in a directed graph
- **Change:** Tarjan's SCC algorithm uses a stack and `lowlink` values. Or use Kosaraju: DFS order, reverse graph, DFS again.

```python
def kosaraju_scc(n, edges):
    graph = [[] for _ in range(n)]
    rev = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        rev[v].append(u)

    visited = [False] * n
    order = []
    def dfs1(u):
        visited[u] = True
        for v in graph[u]:
            if not visited[v]:
                dfs1(v)
        order.append(u)

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    visited = [False] * n
    sccs = []
    def dfs2(u, comp):
        visited[u] = True
        comp.append(u)
        for v in rev[u]:
            if not visited[v]:
                dfs2(v, comp)

    for i in reversed(order):
        if not visited[i]:
            comp = []
            dfs2(i, comp)
            sccs.append(comp)
    return sccs
```

**V3: Minimize Malware Spread (LeetCode 924)**
- **Twist:** Remove one infected node to minimize total infected. Nodes in same component share infection.
- **Change:** Find connected components. Count component sizes. If a component has exactly one initially infected node, removing it saves the whole component.

**Near Miss: Number of Islands (LeetCode 200)**
- **Looks like:** Connectivity analysis
- **But:** Just counting components, not finding critical edges/nodes.
- **Lesson:** Tarjan finds structural vulnerabilities. Basic DFS just finds components.

---

## Pattern 12 Mastery Checklist

Before moving to Pattern 13, confirm you can:

- [ ] Implement Dijkstra with a min-heap and explain why it fails on negative edges
- [ ] Write Bellman-Ford and detect negative cycles
- [ ] Write Floyd-Warshall and know when it beats V * Dijkstra
- [ ] Implement both Prim and Kruskal for MST
- [ ] Implement Union-Find with path compression and union by rank
- [ ] Use Tarjan's algorithm to find bridges in an undirected graph
- [ ] Choose the right shortest-path algorithm based on graph properties (weighted, negative, dense, all-pairs)

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Using Dijkstra with negative weights | Incorrect shortest paths | Use Bellman-Ford or SPFA |
| Using BFS for weighted shortest path | Wrong answer (ignores weights) | Use Dijkstra or 0-1 BFS if weights are 0/1 |
| Forgetting path compression in Union-Find | O(log n) per operation instead of amortized O(1) | Always compress in find() |
| Running Floyd-Warshall on sparse large graphs | O(V^3) TLE | Use Dijkstra from each node |
| Off-by-one in Bellman-Ford iterations | May miss longest shortest paths | Relax n-1 times (or k+1 for K stops) |
| Not handling disconnected graphs in Tarjan | Only finds bridges in one component | Launch DFS from every unvisited node |

---

## Pattern Blends (What Comes Next)

Advanced graphs do not live in isolation. They blend with:

- **Greedy:** Kruskal's MST sorts edges greedily
- **Bitmask + Dijkstra:** Shortest path with collected keys (state-space search)
- **Dynamic Programming:** Floyd-Warshall is itself a DP on intermediate nodes
- **Binary Search on answer + SP:** Check if path exists with cost <= mid
- **Segment Tree + Dijkstra:** When edge weights change dynamically

---

*Next: Pattern 13 — 1-D DP*
