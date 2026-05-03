# Pattern 12: Advanced Graphs — Practice Problems

## Dijkstra

### 743. Network Delay Time
**Statement:** Time for all nodes to receive signal from node k.
**Intuition:** Dijkstra from k. Return max distance. If any unreachable, return -1.
**Code:**
```python
import heapq

def network_delay_time(times, n, k):
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
        for neighbor, w in graph[node]:
            new_dist = d + w
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    
    max_dist = max(dist[1:])
    return max_dist if max_dist != float('inf') else -1
```

### 1631. Path With Minimum Effort
**Statement:** Minimum effort path from top-left to bottom-right.
**Intuition:** Dijkstra where edge weight = absolute difference. Minimize max edge on path.

### 1368. Minimum Cost to Make at Least One Valid Path
**Statement:** Change arrow directions to reach destination.
**Intuition:** 0-1 BFS (deque). Cost 0 if follow arrow, 1 if change.

---

## Bellman-Ford

### 787. Cheapest Flights Within K Stops
**Statement:** Cheapest price from src to dst with at most k stops.
**Intuition:** Bellman-Ford with at most k+1 relaxations.
**Code:**
```python
def find_cheapest_price(n, flights, src, dst, k):
    dist = [float('inf')] * n
    dist[src] = 0
    
    for _ in range(k + 1):
        new_dist = dist[:]
        for u, v, w in flights:
            if dist[u] != float('inf') and dist[u] + w < new_dist[v]:
                new_dist[v] = dist[u] + w
        dist = new_dist
    
    return dist[dst] if dist[dst] != float('inf') else -1
```

---

## Floyd-Warshall

### 1334. Find the City With the Smallest Number of Neighbors at a Threshold Distance
**Statement:** City with fewest neighbors within distance threshold.
**Intuition:** Floyd-Warshall all pairs shortest path. Count neighbors within threshold.

---

## MST

### 1584. Min Cost to Connect All Points
**Statement:** Connect all points with minimum cost (Manhattan distance).
**Intuition:** Prim's or Kruskal's. Build MST on complete graph.
**Code (Prim's):**
```python
import heapq

def min_cost_connect_points(points):
    n = len(points)
    visited = [False] * n
    heap = [(0, 0)]  # (cost, point)
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
                dist = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
                heapq.heappush(heap, (dist, j))
    
    return total
```

---

## Union-Find

### 547. Number of Provinces
**Statement:** Number of connected components.
**Intuition:** Union-Find on adjacency matrix.

### 684. Redundant Connection
**Statement:** Find edge that creates cycle.
**Intuition:** Union-Find. First edge where find(u) == find(v) is redundant.

### 1319. Number of Operations to Make Network Connected
**Statement:** Min operations to connect all computers.
**Intuition:** Need n-1 edges for n nodes. If edges < n-1, impossible. Else, components - 1 operations.

---

## Bridges / Advanced

### 1192. Critical Connections in a Network
**Statement:** Bridges in undirected graph.
**Intuition:** Tarjan's algorithm. Track discovery time and low time.

---

## Mixed Drill Set

1. 743 — Network delay time (Dijkstra)
2. 787 — Cheapest flights K stops (Bellman-Ford)
3. 1584 — Min cost connect points (Prim's)
4. 547 — Number of provinces (Union-Find)
5. 684 — Redundant connection (Union-Find)
6. 1631 — Path with minimum effort (Dijkstra variant)
7. 1334 — City with smallest neighbors (Floyd-Warshall)
8. 1192 — Critical connections (Tarjan)
9. 1319 — Connect network (Union-Find)
10. 1368 — Minimum cost valid path (0-1 BFS)
