# Pattern 11: Graphs - Drills Part 3
## Near Misses + Pattern Blends + Interview Simulation (15 Problems)

---

### 1. 130. Surrounded Regions
**Archetype:** 11.2 DFS Traversal
**Type:** Near Miss
**Statement:** Capture all regions surrounded by 'X' by flipping all 'O's into 'X's in the captured regions.
**Why it fits:** It looks like Number of Islands, but the goal is to identify regions that are NOT connected to the boundary. The natural instinct is to run DFS from every 'O', but that is inefficient.
**The Twist:** You must first mark all 'O's connected to the boundary as safe (using DFS from borders), then flip the remaining 'O's. This is "reverse" thinking compared to standard island counting.
**Code Skeleton:**
```python
def solve(board: list[list[str]]) -> None:
    if not board:
        return
    rows, cols = len(board), len(board[0])

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != 'O':
            return
        board[r][c] = 'S'
        dfs(r+1, c)
        dfs(r-1, c)
        dfs(r, c+1)
        dfs(r, c-1)

    for r in range(rows):
        dfs(r, 0)
        dfs(r, cols - 1)
    for c in range(cols):
        dfs(0, c)
        dfs(rows - 1, c)

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 'O':
                board[r][c] = 'X'
            elif board[r][c] == 'S':
                board[r][c] = 'O'
```

### 2. 261. Graph Valid Tree
**Archetype:** 11.3 Cycle Detection / 11.6 Connected Components
**Type:** Near Miss
**Statement:** Given n nodes and edges, determine if the graph is a valid tree.
**Why it fits:** It looks like cycle detection, but a tree requires both acyclicity AND connectivity. Missing either condition means it is not a tree.
**The Twist:** You can solve this with Union-Find (check no cycle and exactly one component) or DFS (check all nodes reachable and edge count is n-1). Both conditions are necessary.
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

def validTree(n: int, edges: list[list[int]]) -> bool:
    if len(edges) != n - 1:
        return False
    uf = UnionFind(n)
    for u, v in edges:
        if not uf.union(u, v):
            return False
    return uf.count == 1
```

### 3. 323. Number of Connected Components in an Undirected Graph
**Archetype:** 11.6 Connected Components
**Type:** Near Miss
**Statement:** Given n nodes and an edge list, return the number of connected components.
**Why it fits:** It looks like a standard DFS connected components problem. However, Union-Find is often the expected solution because it is more concise and handles dynamic connectivity.
**The Twist:** With Union-Find, the answer is simply the initial count minus successful unions. This is a good test of whether you know when to prefer Union-Find over DFS/BFS.
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

def countComponents(n: int, edges: list[list[int]]) -> int:
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count
```

### 4. 286. Walls and Gates
**Archetype:** 11.1 BFS Traversal
**Type:** Near Miss
**Statement:** Fill each empty room with the distance to its nearest gate. If impossible, fill with INF.
**Why it fits:** It looks like a standard BFS shortest path problem, but there are multiple sources (all gates). The naive approach runs BFS from every empty room.
**The Twist:** Multi-source BFS from all gates simultaneously solves this in O(mn). Running BFS from every empty room would be O((mn)^2).
**Code Skeleton:**
```python
from collections import deque

def wallsAndGates(rooms: list[list[int]]) -> None:
    if not rooms:
        return
    rows, cols = len(rooms), len(rooms[0])
    INF = 2**31 - 1
    queue = deque()

    for r in range(rows):
        for c in range(cols):
            if rooms[r][c] == 0:
                queue.append((r, c))

    while queue:
        r, c = queue.popleft()
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and rooms[nr][nc] == INF:
                rooms[nr][nc] = rooms[r][c] + 1
                queue.append((nr, nc))
```

### 5. 490. The Maze
**Archetype:** 11.1 BFS Traversal
**Type:** Near Miss
**Statement:** Determine if a ball can stop at the destination in a maze. The ball rolls until hitting a wall.
**Why it fits:** It looks like a standard grid BFS, but the ball does not stop at every cell. It rolls in one direction until a wall is hit.
**The Twist:** The state space is not every cell, but every "stopping point." You must simulate the rolling motion to find the next valid state before enqueuing.
**Code Skeleton:**
```python
from collections import deque

def hasPath(maze: list[list[int]], start: list[int], destination: list[int]) -> bool:
    rows, cols = len(maze), len(maze[0])
    visited = set()
    queue = deque([tuple(start)])
    visited.add(tuple(start))

    while queue:
        r, c = queue.popleft()
        if [r, c] == destination:
            return True
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r, c
            while 0 <= nr + dr < rows and 0 <= nc + dc < cols and maze[nr+dr][nc+dc] == 0:
                nr += dr
                nc += dc
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False
```

### 6. 329. Longest Increasing Path in a Matrix
**Archetype:** 11.2 DFS Traversal + DP
**Type:** Pattern Blend
**Statement:** Given an m x n integers matrix, return the length of the longest increasing path.
**Why it fits:** This blends DFS traversal with memoization (DP). You explore all four directions from each cell, but cache results to avoid recomputation.
**The Twist:** The graph is a Directed Acyclic Graph (DAG) because paths are strictly increasing. This guarantees no cycles, so you do not need a visited set for cycle detection, only memoization.
**Code Skeleton:**
```python
def longestIncreasingPath(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    rows, cols = len(matrix), len(matrix[0])
    memo = [[0] * cols for _ in range(rows)]

    def dfs(r, c):
        if memo[r][c] != 0:
            return memo[r][c]
        max_len = 1
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                max_len = max(max_len, 1 + dfs(nr, nc))
        memo[r][c] = max_len
        return max_len

    return max(dfs(r, c) for r in range(rows) for c in range(cols))
```

### 7. 1091. Shortest Path in Binary Matrix
**Archetype:** 11.1 BFS Traversal + A*
**Type:** Pattern Blend
**Statement:** Return the length of the shortest clear path from top-left to bottom-right in a binary matrix.
**Why it fits:** This is BFS on a grid with 8-directional movement. It blends standard grid BFS with diagonal neighbor generation.
**The Twist:** The path can move in 8 directions, not just 4. Additionally, the start and end cells must be 0. Early exit when reaching the destination is essential for efficiency.
**Code Skeleton:**
```python
from collections import deque

def shortestPathBinaryMatrix(grid: list[list[int]]) -> int:
    n = len(grid)
    if grid[0][0] == 1 or grid[n-1][n-1] == 1:
        return -1
    if n == 1:
        return 1

    queue = deque([(0, 0, 1)])
    grid[0][0] = 1
    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    while queue:
        r, c, length = queue.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if nr == n - 1 and nc == n - 1:
                return length + 1
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                grid[nr][nc] = 1
                queue.append((nr, nc, length + 1))
    return -1
```

### 8. 310. Minimum Height Trees
**Archetype:** 11.1 BFS Traversal + Topological Sort
**Type:** Pattern Blend
**Statement:** Given a tree of n nodes, return all root labels of the minimum height trees.
**Why it fits:** This blends BFS with topological sort intuition. You iteratively remove leaf nodes layer by layer until 1 or 2 nodes remain.
**The Twist:** The naive approach tries every node as root and computes height (O(N^2)). The "peeling leaves" approach is O(N) and works because the center(s) of a tree are the roots of minimum height trees.
**Code Skeleton:**
```python
from collections import deque

def findMinHeightTrees(n: int, edges: list[list[int]]) -> list[int]:
    if n <= 2:
        return list(range(n))
    graph = [set() for _ in range(n)]
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    leaves = deque([i for i in range(n) if len(graph[i]) == 1])
    remaining = n

    while remaining > 2:
        leaf_count = len(leaves)
        remaining -= leaf_count
        for _ in range(leaf_count):
            leaf = leaves.popleft()
            neighbor = graph[leaf].pop()
            graph[neighbor].remove(leaf)
            if len(graph[neighbor]) == 1:
                leaves.append(neighbor)
    return list(leaves)
```

### 9. 1306. Jump Game III
**Archetype:** 11.1 BFS Traversal + Greedy/DP
**Type:** Pattern Blend
**Statement:** Given an array and a start index, determine if you can reach any index with value 0 by jumping left or right by arr[i] steps.
**Why it fits:** This blends BFS/DFS with array traversal. Each index is a node connected to i + arr[i] and i - arr[i].
**The Twist:** Unlike standard jump game problems, you can jump both left and right. This creates an undirected graph, and BFS/DFS is more natural than the greedy approach used in Jump Game II.
**Code Skeleton:**
```python
from collections import deque

def canReach(arr: list[int], start: int) -> bool:
    n = len(arr)
    visited = [False] * n
    queue = deque([start])
    visited[start] = True

    while queue:
        i = queue.popleft()
        if arr[i] == 0:
            return True
        for j in [i + arr[i], i - arr[i]]:
            if 0 <= j < n and not visited[j]:
                visited[j] = True
                queue.append(j)
    return False
```

### 10. 815. Bus Routes
**Archetype:** 11.1 BFS Traversal + Hash Map
**Type:** Pattern Blend
**Statement:** Given a list of bus routes, return the minimum number of buses you must take to reach the target.
**Why it fits:** This is BFS on a bipartite graph of buses and stops. You can model it as BFS where states are stops, but edges are buses.
**The Twist:** The naive approach builds a graph of stops, but stop-to-stop edges are dense. Instead, build a map from stop to buses, and BFS on buses taken, which is much sparser.
**Code Skeleton:**
```python
from collections import deque, defaultdict

def numBusesToDestination(routes: list[list[int]], source: int, target: int) -> int:
    if source == target:
        return 0
    stop_to_buses = defaultdict(list)
    for i, route in enumerate(routes):
        for stop in route:
            stop_to_buses[stop].append(i)

    visited_buses = set()
    visited_stops = {source}
    queue = deque([(source, 0)])

    while queue:
        stop, buses = queue.popleft()
        for bus in stop_to_buses[stop]:
            if bus in visited_buses:
                continue
            visited_buses.add(bus)
            for next_stop in routes[bus]:
                if next_stop == target:
                    return buses + 1
                if next_stop not in visited_stops:
                    visited_stops.add(next_stop)
                    queue.append((next_stop, buses + 1))
    return -1
```

### 11. 126. Word Ladder II
**Archetype:** 11.7 Word Ladder
**Type:** Interview Sim
**Statement:** Return all shortest transformation sequences from beginWord to endWord.
**Why it fits:** This is a classic interview follow-up to Word Ladder. The interviewer expects you to first find the shortest distance using BFS, then use DFS to reconstruct all paths.
**The Twist:** You must find ALL shortest paths, not just one. This requires building a parent map during BFS and then backtracking from endWord to beginWord.
**Code Skeleton:**
```python
from collections import deque, defaultdict

def findLadders(beginWord: str, endWord: str, wordList: list[str]) -> list[list[str]]:
    wordSet = set(wordList)
    if endWord not in wordSet:
        return []

    # BFS to build parent map
    parents = defaultdict(list)
    visited = {beginWord}
    found = False
    queue = deque([beginWord])

    while queue and not found:
        local_visited = set()
        for _ in range(len(queue)):
            word = queue.popleft()
            for i in range(len(word)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    next_word = word[:i] + c + word[i+1:]
                    if next_word in wordSet and next_word not in visited:
                        parents[next_word].append(word)
                        local_visited.add(next_word)
                        if next_word == endWord:
                            found = True
        for w in local_visited:
            visited.add(w)
            queue.append(w)

    # Backtrack to find all paths
    ans = []
    def backtrack(word, path):
        if word == beginWord:
            ans.append(path[::-1])
            return
        for parent in parents[word]:
            backtrack(parent, path + [parent])
    backtrack(endWord, [endWord])
    return ans
```

### 12. 444. Sequence Reconstruction
**Archetype:** 11.4 Topological Sort
**Type:** Interview Sim
**Statement:** Determine if the original sequence can be uniquely reconstructed from a list of subsequences.
**Why it fits:** This is a topological sort interview problem. The interviewer wants to see if you understand that a unique topological order requires exactly one node with in-degree 0 at every step.
**The Twist:** You must verify that the topological sort is unique. If at any point there are multiple nodes with in-degree 0, the original sequence cannot be uniquely reconstructed.
**Code Skeleton:**
```python
from collections import deque, defaultdict

def sequenceReconstruction(nums: list[int], sequences: list[list[int]]) -> bool:
    n = len(nums)
    graph = defaultdict(list)
    in_degree = {i: 0 for i in range(1, n + 1)}

    for seq in sequences:
        for i in range(len(seq) - 1):
            graph[seq[i]].append(seq[i+1])
            in_degree[seq[i+1]] += 1

    queue = deque([node for node in range(1, n + 1) if in_degree[node] == 0])
    reconstructed = []

    while queue:
        if len(queue) > 1:
            return False
        node = queue.popleft()
        reconstructed.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return reconstructed == nums
```

### 13. 1129. Shortest Path with Alternating Colors
**Archetype:** 11.1 BFS Traversal
**Type:** Interview Sim
**Statement:** Return the shortest path from node 0 to each node such that edge colors alternate.
**Why it fits:** This is a BFS interview problem where the state includes not just the node, but also the color of the edge you arrived on.
**The Twist:** The state space is (node, last_edge_color). You must track visited as a 2D array [node][color] to avoid revisiting the same node with the same last color.
**Code Skeleton:**
```python
from collections import deque

def shortestAlternatingPaths(n: int, redEdges: list[list[int]], blueEdges: list[list[int]]) -> list[int]:
    red_graph = [[] for _ in range(n)]
    blue_graph = [[] for _ in range(n)]
    for u, v in redEdges:
        red_graph[u].append(v)
    for u, v in blueEdges:
        blue_graph[u].append(v)

    ans = [-1] * n
    # (node, color) where 0=red, 1=blue
    visited = [[False, False] for _ in range(n)]
    queue = deque([(0, 0, 0), (0, 1, 0)])  # node, color, length
    visited[0][0] = True
    visited[0][1] = True

    while queue:
        node, color, length = queue.popleft()
        if ans[node] == -1:
            ans[node] = length
        if color == 0:
            for neighbor in blue_graph[node]:
                if not visited[neighbor][1]:
                    visited[neighbor][1] = True
                    queue.append((neighbor, 1, length + 1))
        else:
            for neighbor in red_graph[node]:
                if not visited[neighbor][0]:
                    visited[neighbor][0] = True
                    queue.append((neighbor, 0, length + 1))
    return ans
```

### 14. 1059. All Paths from Source Lead to Destination
**Archetype:** 11.3 Cycle Detection / 11.2 DFS Traversal
**Type:** Interview Sim
**Statement:** Given a directed acyclic graph (or not), determine if all paths from source lead to destination.
**Why it fits:** This blends cycle detection with reachability. The interviewer tests whether you know how to detect cycles and verify that all paths terminate at the destination.
**The Twist:** The graph may have cycles. You must detect cycles and reject the graph if any cycle is reachable from the source. Additionally, any dead-end node (except destination) makes the answer false.
**Code Skeleton:**
```python
def leadsToDestination(n: int, edges: list[list[int]], source: int, destination: int) -> bool:
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)

    # 0=unvisited, 1=visiting, 2=visited
    state = [0] * n

    def dfs(node):
        if state[node] == 1:
            return False
        if state[node] == 2:
            return True
        if not graph[node]:
            return node == destination
        state[node] = 1
        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False
        state[node] = 2
        return True

    return dfs(source)
```

### 15. 851. Loud and Rich
**Archetype:** 11.4 Topological Sort + DP
**Type:** Interview Sim
**Statement:** For each person, return the least quiet person among all people who are definitely equal or richer.
**Why it fits:** This is a topological sort / DFS with memoization problem. The graph is a DAG of "richer than" relationships.
**The Twist:** The naive approach runs DFS from every node. Memoization is essential because the quietest person for a node is the minimum of the quietest persons of all richer neighbors, plus itself.
**Code Skeleton:**
```python
from collections import defaultdict

def loudAndRich(richer: list[list[int]], quiet: list[int]) -> list[int]:
    n = len(quiet)
    graph = defaultdict(list)
    for a, b in richer:
        graph[b].append(a)

    memo = {}

    def dfs(node):
        if node in memo:
            return memo[node]
        quietest = node
        for neighbor in graph[node]:
            candidate = dfs(neighbor)
            if quiet[candidate] < quiet[quietest]:
                quietest = candidate
        memo[node] = quietest
        return quietest

    return [dfs(i) for i in range(n)]
```
