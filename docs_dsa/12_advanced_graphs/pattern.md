# Pattern 12: Advanced Graphs

> **Pattern Recognition:** When you see "shortest path", "minimum cost", "network delay", "MST", "minimum spanning", "Dijkstra", "Bellman-Ford" — think advanced graph algorithms.
>
> **Fundamental Insight:** When edges have weights, BFS is no longer sufficient. We need algorithms that account for weights: Dijkstra (non-negative), Bellman-Ford (negative weights), Floyd-Warshall (all pairs), Prim/Kruskal (MST).

---

## Archetype 12.1: Dijkstra (Shortest Path)

### Recognition Signal
Words: **"shortest path", "minimum cost", "network delay", "cheapest flights", "non-negative weights"**

### Template
```python
import heapq

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    heap = [(0, start)]
    
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return dist
```

### Problems
- Network Delay Time (LeetCode 743)
- Path With Minimum Effort (LeetCode 1631)
- Cheapest Flights Within K Stops (LeetCode 787) — modified Dijkstra
- Minimum Cost to Make at Least One Valid Path (LeetCode 1368)

---

## Archetype 12.2: Bellman-Ford

### Recognition Signal
Words: **"negative weights", "shortest path with negative edges", "detect negative cycle"**

### Template
```python
def bellman_ford(edges, n, start):
    dist = [float('inf')] * n
    dist[start] = 0
    
    # Relax n-1 times
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    
    # Check for negative cycle
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return None  # Negative cycle
    
    return dist
```

### Problems
- Cheapest Flights Within K Stops (LeetCode 787)

---

## Archetype 12.3: Floyd-Warshall (All Pairs Shortest Path)

### Recognition Signal
Words: **"all pairs shortest path", "transitive closure", "shortest between every pair"**

### Template
```python
def floyd_warshall(graph, n):
    dist = [[float('inf')] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in graph:
        dist[u][v] = w
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist
```

### Problems
- Find the City With the Smallest Number of Neighbors at a Threshold Distance (LeetCode 1334)

---

## Archetype 12.4: Minimum Spanning Tree (MST)

### Recognition Signal
Words: **"minimum spanning tree", "connect all points", "minimum cost to connect", "MST"**

### Prim's Algorithm
```python
import heapq

def prim(graph, n):
    visited = [False] * n
    min_heap = [(0, 0)]  # (weight, node)
    total_weight = 0
    
    while min_heap:
        weight, node = heapq.heappop(min_heap)
        if visited[node]:
            continue
        visited[node] = True
        total_weight += weight
        
        for neighbor, w in graph[node]:
            if not visited[neighbor]:
                heapq.heappush(min_heap, (w, neighbor))
    
    return total_weight
```

### Problems
- Min Cost to Connect All Points (LeetCode 1584)
- Optimize Water Distribution in a Village (LeetCode 1168)

---

## Archetype 12.5: Union-Find (Disjoint Set)

### Recognition Signal
Words: **"connected components", "redundant connection", "number of provinces", "union find"**

### Template
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n
    
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
        self.count -= 1
        return True
```

### Problems
- Number of Provinces (LeetCode 547)
- Redundant Connection (LeetCode 684)
- Accounts Merge (LeetCode 721)
- Number of Operations to Make Network Connected (LeetCode 1319)
- Longest Consecutive Sequence (LeetCode 128) — can use Union-Find

---

## Archetype 12.6: Tarjan's Algorithm (SCC / Bridges)

### Recognition Signal
Words: **"critical connections", "bridges", "articulation points", "strongly connected components"**

### Problems
- Critical Connections in a Network (LeetCode 1192)

---

## Mastery Checklist
- [ ] Dijkstra with min heap
- [ ] Bellman-Ford with negative weights
- [ ] Floyd-Warshall all pairs
- [ ] Prim's MST
- [ ] Union-Find with path compression and union by rank
- [ ] Detect negative cycle
- [ ] Find bridges in graph

---

## Algorithm Selection Guide

| Problem Type | Algorithm | Time | Handles Negative? |
|---|---|---|---|
| Shortest path (single, non-negative) | Dijkstra | O((V+E) log V) | No |
| Shortest path (single, negative) | Bellman-Ford | O(VE) | Yes |
| Shortest path (all pairs) | Floyd-Warshall | O(V^3) | Yes |
| Minimum spanning tree | Prim / Kruskal | O(E log V) | N/A |
| Connected components | Union-Find | O(α(V)) | N/A |
| Cycle detection | Union-Find or DFS | O(E α(V)) or O(V+E) | N/A |

---

## Common Traps

**Trap:** Using Dijkstra with negative weights.
- Fix: Use Bellman-Ford instead.

**Trap:** Union-Find without path compression.
- Fix: Always implement path compression for near-O(1) find.

**Trap:** Forgetting to check if all nodes are reachable in Dijkstra.
- Fix: `if dist[node] == inf: return -1`

**Near Miss: BFS for Shortest Path**
- BFS only works for unweighted graphs or uniform weights
- For weighted graphs, use Dijkstra
