# Pattern 12: Advanced Graphs - Drills Part 3
## Near Misses + Pattern Blends + Interview Simulation (15 Problems)

---

### 1. 1293. Shortest Path in a Grid with Obstacles Elimination
**Archetype:** 12.1 Dijkstra
**Type:** Near Miss
**Statement:** Return the shortest path from top-left to bottom-right where you can eliminate at most k obstacles.
**Why it fits:** It looks like a shortest path problem requiring Dijkstra because of the obstacle constraint. However, since every move has unit cost, BFS with state (row, col, k_remaining) is sufficient.
**The Twist:** The state space includes the number of eliminations remaining. Standard Dijkstra works but is overkill; BFS on a 3D visited array is simpler and optimal because all edges have weight 1.
**Code Skeleton:**
```python
from collections import deque

def shortestPath(grid: list[list[int]], k: int) -> int:
    rows, cols = len(grid), len(grid[0])
    if k >= rows + cols - 2:
        return rows + cols - 2

    visited = [[-1] * cols for _ in range(rows)]
    queue = deque([(0, 0, 0, k)])  # r, c, steps, k_left
    visited[0][0] = k

    while queue:
        r, c, steps, k_left = queue.popleft()
        if r == rows - 1 and c == cols - 1:
            return steps
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                new_k = k_left - grid[nr][nc]
                if new_k >= 0 and new_k > visited[nr][nc]:
                    visited[nr][nc] = new_k
                    queue.append((nr, nc, steps + 1, new_k))
    return -1
```

### 2. 847. Shortest Path Visiting All Nodes
**Archetype:** 12.1 Dijkstra
**Type:** Near Miss
**Statement:** Return the length of the shortest path that visits every node in an undirected graph.
**Why it fits:** It looks like an all-pairs shortest path problem, but it is actually a Traveling Salesman Problem (TSP) on a graph. The state must include which nodes have been visited.
**The Twist:** You must use BFS with a state of (current_node, visited_mask). The visited mask turns this into a state-space search with 2^n * n states, not a standard shortest path algorithm.
**Code Skeleton:**
```python
from collections import deque

def shortestPathLength(graph: list[list[int]]) -> int:
    n = len(graph)
    if n == 1:
        return 0
    all_visited = (1 << n) - 1
    queue = deque()
    visited = set()
    for i in range(n):
        queue.append((i, 1 << i, 0))
        visited.add((i, 1 << i))

    while queue:
        node, mask, dist = queue.popleft()
        if mask == all_visited:
            return dist
        for neighbor in graph[node]:
            new_mask = mask | (1 << neighbor)
            if (neighbor, new_mask) not in visited:
                visited.add((neighbor, new_mask))
                queue.append((neighbor, new_mask, dist + 1))
    return -1
```

### 3. 1514. Path with Maximum Probability
**Archetype:** 12.1 Dijkstra
**Type:** Near Miss
**Statement:** Return the path with the maximum probability of success from start to end.
**Why it fits:** It looks like Dijkstra, but you are maximizing probability instead of minimizing distance. The greedy choice must be adjusted.
**The Twist:** Instead of a min-heap, you use a max-heap (or negate probabilities). The relaxation updates the probability if the product of probabilities is higher than the current best.
**Code Skeleton:**
```python
import heapq

def maxProbability(n: int, edges: list[list[int]], succProb: list[float], start: int, end: int) -> float:
    graph = [[] for _ in range(n)]
    for (u, v), prob in zip(edges, succProb):
        graph[u].append((v, prob))
        graph[v].append((u, prob))

    prob = [0.0] * n
    prob[start] = 1.0
    heap = [(-1.0, start)]

    while heap:
        curr_prob, node = heapq.heappop(heap)
        curr_prob = -curr_prob
        if node == end:
            return curr_prob
        if curr_prob < prob[node]:
            continue
        for neighbor, edge_prob in graph[node]:
            new_prob = curr_prob * edge_prob
            if new_prob > prob[neighbor]:
                prob[neighbor] = new_prob
                heapq.heappush(heap, (-new_prob, neighbor))
    return 0.0
```

### 4. 1976. Number of Ways to Arrive at Destination
**Archetype:** 12.1 Dijkstra
**Type:** Near Miss
**Statement:** Return the number of ways you can arrive at your destination in the shortest amount of time.
**Why it fits:** It looks like standard Dijkstra, but you must count the number of shortest paths, not just find the shortest distance.
**The Twist:** Whenever you find a shorter path to a node, reset its count to 1. When you find an equal-length path, add to its count. You must do this modulo 10^9 + 7.
**Code Skeleton:**
```python
import heapq

def countPaths(n: int, roads: list[list[int]]) -> int:
    MOD = 10**9 + 7
    graph = [[] for _ in range(n)]
    for u, v, t in roads:
        graph[u].append((v, t))
        graph[v].append((u, t))

    dist = [float('inf')] * n
    ways = [0] * n
    dist[0] = 0
    ways[0] = 1
    heap = [(0, 0)]

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for neighbor, time in graph[node]:
            new_dist = d + time
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                ways[neighbor] = ways[node]
                heapq.heappush(heap, (new_dist, neighbor))
            elif new_dist == dist[neighbor]:
                ways[neighbor] = (ways[neighbor] + ways[node]) % MOD
    return ways[n - 1]
```

### 5. 2045. Second Minimum Time to Reach Destination
**Archetype:** 12.1 Dijkstra
**Type:** Near Miss
**Statement:** Return the second minimum time to reach node n from node 1, where edges take a fixed time and you may have to wait at nodes due to traffic signals.
**Why it fits:** It looks like Dijkstra, but you need the strictly second shortest path, not just the shortest. This requires tracking the two best distances to each node.
**The Twist:** The traffic signal adds a waiting time that depends on when you arrive. The state includes arrival time, and you must compute wait time based on the signal period.
**Code Skeleton:**
```python
import heapq

def secondMinimum(n: int, edges: list[list[int]], time: int, change: int) -> int:
    graph = [[] for _ in range(n + 1)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    # dist[node] = [shortest, second_shortest]
    dist = [[float('inf'), float('inf')] for _ in range(n + 1)]
    dist[1][0] = 0
    heap = [(0, 1)]

    while heap:
        curr_time, node = heapq.heappop(heap)
        if node == n and curr_time > dist[n][0]:
            return curr_time
        # Calculate wait time at current node before leaving
        if (curr_time // change) % 2 == 1:
            curr_time += change - (curr_time % change)
        for neighbor in graph[node]:
            new_time = curr_time + time
            if new_time < dist[neighbor][0]:
                dist[neighbor][1] = dist[neighbor][0]
                dist[neighbor][0] = new_time
                heapq.heappush(heap, (new_time, neighbor))
            elif dist[neighbor][0] < new_time < dist[neighbor][1]:
                dist[neighbor][1] = new_time
                heapq.heappush(heap, (new_time, neighbor))
    return -1
```

### 6. 1579. Remove Max Number of Edges to Keep Graph Fully Traversable
**Archetype:** 12.5 Union-Find + Greedy
**Type:** Pattern Blend
**Statement:** Return the maximum number of edges you can remove so that Alice and Bob can still fully traverse the graph separately.
**Why it fits:** This blends Union-Find with greedy edge selection. Type 3 edges (usable by both) are most valuable and should be used first.
**The Twist:** You need two Union-Find structures (one for Alice, one for Bob). Process type 3 edges first, then type 1 and type 2 separately. Any redundant edge can be removed.
**Code Skeleton:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n + 1))
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

def maxNumEdgesToRemove(n: int, edges: list[list[int]]) -> int:
    alice = UnionFind(n)
    bob = UnionFind(n)
    removed = 0

    # Type 3 edges first
    for t, u, v in edges:
        if t == 3:
            a = alice.union(u, v)
            b = bob.union(u, v)
            if not a and not b:
                removed += 1

    # Type 1 and 2
    for t, u, v in edges:
        if t == 1:
            if not alice.union(u, v):
                removed += 1
        elif t == 2:
            if not bob.union(u, v):
                removed += 1

    if alice.count != 1 or bob.count != 1:
        return -1
    return removed
```

### 7. 2503. Maximum Number of Points From Grid Queries
**Archetype:** 12.1 Dijkstra + Union-Find
**Type:** Pattern Blend
**Statement:** For each query, return the maximum number of points you can visit in a grid if you can only visit cells with value strictly less than the query.
**Why it fits:** This blends Dijkstra's expansion order with offline query processing. You process queries in sorted order and expand the reachable region as the threshold increases.
**The Twist:** Instead of running BFS/Dijkstra for each query, you sort queries and the grid cells together. As you increase the threshold, you union adjacent cells that have become reachable.
**Code Skeleton:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.size[px] < self.size[py]:
            px, py = py, px
        self.parent[py] = px
        self.size[px] += self.size[py]

class Solution:
    def maxPoints(self, grid: list[list[int]], queries: list[int]) -> list[int]:
        rows, cols = len(grid), len(grid[0])
        n = rows * cols
        uf = UnionFind(n)
        cells = []
        for r in range(rows):
            for c in range(cols):
                cells.append((grid[r][c], r, c))
        cells.sort()

        sorted_queries = sorted(enumerate(queries), key=lambda x: x[1])
        ans = [0] * len(queries)
        idx = 0
        visited = [[False] * cols for _ in range(rows)]

        for q_idx, q in sorted_queries:
            while idx < len(cells) and cells[idx][0] < q:
                val, r, c = cells[idx]
                visited[r][c] = True
                for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and visited[nr][nc]:
                        uf.union(r * cols + c, nr * cols + nc)
                idx += 1
            if visited[0][0]:
                ans[q_idx] = uf.size[uf.find(0)]
        return ans
```

### 8. 1203. Sort Items by Groups Respecting Dependencies
**Archetype:** 12.4 MST + Topological Sort
**Type:** Pattern Blend
**Statement:** Given n items with group assignments and dependencies, return any sorted list of items respecting group and item dependencies.
**Why it fits:** This blends topological sort with graph construction. You must topologically sort both groups and items within groups, then merge them.
**The Twist:** Items in the same group must appear contiguously. This requires two levels of topological sort: one for groups, one for items within each group. Unassigned items (-1 group) get unique groups.
**Code Skeleton:**
```python
from collections import deque, defaultdict

def sortItems(n: int, m: int, group: list[int], beforeItems: list[list[int]]) -> list[int]:
    # Assign unique groups to ungrouped items
    for i in range(n):
        if group[i] == -1:
            group[i] = m
            m += 1

    group_graph = defaultdict(list)
    group_indeg = [0] * m
    item_graph = defaultdict(list)
    item_indeg = [0] * n

    for i in range(n):
        for pre in beforeItems[i]:
            item_graph[pre].append(i)
            item_indeg[i] += 1
            if group[pre] != group[i]:
                group_graph[group[pre]].append(group[i])
                group_indeg[group[i]] += 1

    def topo_sort(graph, indeg, nodes):
        queue = deque([n for n in nodes if indeg[n] == 0])
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in graph[node]:
                indeg[neighbor] -= 1
                if indeg[neighbor] == 0:
                    queue.append(neighbor)
        return result if len(result) == len(nodes) else []

    group_order = topo_sort(group_graph, group_indeg, list(range(m)))
    if not group_order:
        return []

    group_to_items = defaultdict(list)
    for i in range(n):
        group_to_items[group[i]].append(i)

    item_order = topo_sort(item_graph, item_indeg, list(range(n)))
    if not item_order:
        return []

    # Reorder items by group order
    group_item_order = {g: [] for g in range(m)}
    for item in item_order:
        group_item_order[group[item]].append(item)

    ans = []
    for g in group_order:
        ans.extend(group_item_order[g])
    return ans
```

### 9. 1102. Path With Maximum Minimum Value
**Archetype:** 12.1 Dijkstra + Binary Search
**Type:** Pattern Blend
**Statement:** Return the maximum score of a path from top-left to bottom-right, where the score is the minimum value in that path.
**Why it fits:** This blends modified Dijkstra (maximizing the minimum) with binary search + BFS as an alternative solution. It is a "widest path" problem.
**The Twist:** The score is the minimum cell value along the path, not the sum. You can solve this with a max-heap (modified Dijkstra) or binary search on the answer with BFS verification.
**Code Skeleton:**
```python
import heapq

def maximumMinimumPath(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    # max-heap: we want to maximize the minimum seen so far
    heap = [(-grid[0][0], 0, 0)]
    visited = [[False] * cols for _ in range(rows)]
    visited[0][0] = True

    while heap:
        score, r, c = heapq.heappop(heap)
        score = -score
        if r == rows - 1 and c == cols - 1:
            return score
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                visited[nr][nc] = True
                new_score = min(score, grid[nr][nc])
                heapq.heappush(heap, (-new_score, nr, nc))
    return -1
```

### 10. 407. Trapping Rain Water II
**Archetype:** 12.1 Dijkstra + Heap
**Type:** Pattern Blend
**Statement:** Given an m x n matrix of heightMap, return the volume of water it can trap after raining.
**Why it fits:** This blends Dijkstra's expansion with a priority queue (min-heap). Water trapped at a cell depends on the lowest boundary around it.
**The Twist:** You start from the boundary (which cannot trap water) and expand inward. The water level at an interior cell is determined by the maximum of its own height and the lowest boundary height encountered so far.
**Code Skeleton:**
```python
import heapq

def trapRainWater(heightMap: list[list[int]]) -> int:
    if not heightMap or not heightMap[0]:
        return 0
    rows, cols = len(heightMap), len(heightMap[0])
    heap = []
    visited = [[False] * cols for _ in range(rows)]

    for r in range(rows):
        for c in [0, cols - 1]:
            heapq.heappush(heap, (heightMap[r][c], r, c))
            visited[r][c] = True
    for c in range(cols):
        for r in [0, rows - 1]:
            if not visited[r][c]:
                heapq.heappush(heap, (heightMap[r][c], r, c))
                visited[r][c] = True

    water = 0
    while heap:
        height, r, c = heapq.heappop(heap)
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                visited[nr][nc] = True
                # Water trapped is the difference between boundary height and cell height
                trapped = max(0, height - heightMap[nr][nc])
                water += trapped
                heapq.heappush(heap, (max(height, heightMap[nr][nc]), nr, nc))
    return water
```

### 11. 499. The Maze III
**Archetype:** 12.1 Dijkstra
**Type:** Interview Sim
**Statement:** Return the shortest distance for the ball to stop at the destination and the lexicographically smallest path among all shortest paths.
**Why it fits:** This is a classic interview hard problem combining Dijkstra with path reconstruction and lexicographic ordering.
**The Twist:** The ball rolls until hitting a wall, so states are stopping points, not every cell. Additionally, among equal distances, you must choose the lexicographically smallest direction sequence (d, l, r, u).
**Code Skeleton:**
```python
import heapq

def findShortestWay(maze: list[list[int]], ball: list[int], hole: list[int]) -> str:
    rows, cols = len(maze), len(maze[0])
    # (distance, path, r, c)
    heap = [(0, "", ball[0], ball[1])]
    visited = {}
    directions = [('d', 1, 0), ('l', 0, -1), ('r', 0, 1), ('u', -1, 0)]

    while heap:
        dist, path, r, c = heapq.heappop(heap)
        if [r, c] == hole:
            return path
        if (r, c) in visited and visited[(r, c)] <= dist:
            continue
        visited[(r, c)] = dist
        for d, dr, dc in directions:
            nr, nc, steps = r, c, 0
            while 0 <= nr + dr < rows and 0 <= nc + dc < cols and maze[nr+dr][nc+dc] == 0:
                nr += dr
                nc += dc
                steps += 1
                if [nr, nc] == hole:
                    break
            if (nr, nc) not in visited or visited.get((nr, nc), float('inf')) > dist + steps:
                heapq.heappush(heap, (dist + steps, path + d, nr, nc))
    return "impossible"
```

### 12. 505. The Maze II
**Archetype:** 12.1 Dijkstra
**Type:** Interview Sim
**Statement:** Return the shortest distance for the ball to stop at the destination in a maze.
**Why it fits:** This is the standard Maze interview problem. The ball rolls until hitting a wall, and you need the shortest path in terms of distance rolled.
**The Twist:** The edge weights are the number of cells rolled, not 1 per move. Standard BFS does not work because different paths to the same cell may have different costs. Dijkstra is required.
**Code Skeleton:**
```python
import heapq

def shortestDistance(maze: list[list[int]], start: list[int], destination: list[int]) -> int:
    rows, cols = len(maze), len(maze[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[start[0]][start[1]] = 0
    heap = [(0, start[0], start[1])]

    while heap:
        d, r, c = heapq.heappop(heap)
        if [r, c] == destination:
            return d
        if d > dist[r][c]:
            continue
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc, steps = r, c, 0
            while 0 <= nr + dr < rows and 0 <= nc + dc < cols and maze[nr+dr][nc+dc] == 0:
                nr += dr
                nc += dc
                steps += 1
            if d + steps < dist[nr][nc]:
                dist[nr][nc] = d + steps
                heapq.heappush(heap, (dist[nr][nc], nr, nc))
    return -1
```

### 13. 1697. Checking Existence of Edge Length Limited Paths
**Archetype:** 12.5 Union-Find + Offline Queries
**Type:** Interview Sim
**Statement:** For each query, determine if there exists a path between two nodes such that every edge on the path has distance strictly less than a limit.
**Why it fits:** This is a classic offline query interview problem. You sort edges and queries by weight, then incrementally add edges to a Union-Find structure.
**The Twist:** The queries are offline, meaning you can reorder them. By processing queries in increasing order of limit, you only need to union edges with weight less than the current limit.
**Code Skeleton:**
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        self.parent[self.find(x)] = self.find(y)

class Solution:
    def distanceLimitedPathsExist(self, n: int, edgeList: list[list[int]], queries: list[list[int]]) -> list[bool]:
        edges = sorted((w, u, v) for u, v, w in edgeList)
        sorted_queries = sorted(enumerate(queries), key=lambda x: x[1][2])
        ans = [False] * len(queries)
        uf = UnionFind(n)
        idx = 0

        for q_idx, (u, v, limit) in sorted_queries:
            while idx < len(edges) and edges[idx][0] < limit:
                _, a, b = edges[idx]
                uf.union(a, b)
                idx += 1
            ans[q_idx] = uf.find(u) == uf.find(v)
        return ans
```

### 14. 2290. Minimum Obstacle Removal to Reach Corner
**Archetype:** 12.1 Dijkstra
**Type:** Interview Sim
**Statement:** Return the minimum number of obstacles to remove so you can move from the upper left to the lower right corner.
**Why it fits:** This is a 0-1 BFS / Dijkstra interview problem. Empty cells cost 0, obstacles cost 1. The interviewer tests if you know 0-1 BFS or if you default to full Dijkstra.
**The Twist:** Since weights are only 0 and 1, you can use a deque and push to the front for 0-cost moves and to the back for 1-cost moves, achieving O(V+E) instead of O(E log V).
**Code Skeleton:**
```python
from collections import deque

def minimumObstacles(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = 0
    dq = deque([(0, 0)])

    while dq:
        r, c = dq.popleft()
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                cost = grid[nr][nc]
                if dist[r][c] + cost < dist[nr][nc]:
                    dist[nr][nc] = dist[r][c] + cost
                    if cost == 0:
                        dq.appendleft((nr, nc))
                    else:
                        dq.append((nr, nc))
    return dist[rows-1][cols-1]
```

### 15. 2642. Design Graph With Shortest Path Calculator
**Archetype:** 12.1 Dijkstra + Design
**Type:** Interview Sim
**Statement:** Design a graph class that supports adding edges and calculating shortest path between two nodes.
**Why it fits:** This is a design interview problem testing your ability to implement Dijkstra on demand. The graph is dynamic (edges can be added).
**The Twist:** Because edges are only added (not removed), you can run Dijkstra from scratch on each shortestPath query. The interviewer may ask how to optimize if queries are frequent (precompute all-pairs, cache results, etc.).
**Code Skeleton:**
```python
import heapq

class Graph:
    def __init__(self, n: int, edges: list[list[int]]):
        self.n = n
        self.graph = [[] for _ in range(n)]
        for u, v, w in edges:
            self.graph[u].append((v, w))

    def addEdge(self, edge: list[int]) -> None:
        u, v, w = edge
        self.graph[u].append((v, w))

    def shortestPath(self, node1: int, node2: int) -> int:
        dist = [float('inf')] * self.n
        dist[node1] = 0
        heap = [(0, node1)]
        while heap:
            d, node = heapq.heappop(heap)
            if d > dist[node]:
                continue
            if node == node2:
                return d
            for neighbor, weight in self.graph[node]:
                new_dist = d + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor))
        return -1
```
