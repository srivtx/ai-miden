# Pattern 11: Graphs — Complete Archetype Map

> **Pattern Recognition:** When you see "network", "connections", "nodes", "edges", "paths", "neighbors", "grid", "relationships" — think graph.
>
> **Fundamental Insight:** If entities have relationships, model them as nodes and edges. Traversal (BFS/DFS) turns local relationships into global insights: connectivity, cycles, ordering, colorability.

---

## Archetype 11.1: BFS Traversal

### Recognition Signal (10 seconds)
Words: **"shortest path", "level order", "nearest", "minimum steps", "unweighted", "grid traversal", "flood fill"**

The question is always: **"Find the shortest (minimum-edge) path or distance in an unweighted graph."**

### Core Structure
```python
from collections import deque

def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    distance = {start: 0}

    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                distance[neighbor] = distance[node] + 1
                queue.append(neighbor)
    return distance
```

### The Invariant
BFS explores nodes in increasing order of distance from the start. The first time we visit a node, we have found the shortest path to it in an unweighted graph.

### Canonical Problem: Number of Islands (LeetCode 200)
**Statement:** Given a grid of '1's (land) and '0's (water), count the number of islands.

```python
from collections import deque

class Solution:
    def numIslands(self, grid):
        if not grid or not grid[0]:
            return 0
        rows, cols = len(grid), len(grid[0])
        count = 0

        def bfs(r, c):
            queue = deque([(r, c)])
            grid[r][c] = '0'  # Mark visited
            while queue:
                cr, cc = queue.popleft()
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                        grid[nr][nc] = '0'
                        queue.append((nr, nc))

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == '1':
                    bfs(r, c)
                    count += 1
        return count
```

### Variation Family

**V1: 01 Matrix (LeetCode 542)**
- **Twist:** Find distance of nearest 0 for each cell
- **Change:** Multi-source BFS. Start from all 0s simultaneously.

```python
from collections import deque

def updateMatrix(mat):
    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]
    queue = deque()
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                queue.append((r, c))
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                queue.append((nr, nc))
    return dist
```

**V2: Rotting Oranges (LeetCode 994)**
- **Twist:** Minutes until no fresh oranges remain. Rotting spreads to adjacent fresh oranges each minute.
- **Change:** Multi-source BFS from all initially rotten oranges. Track minutes = levels.

**V3: Shortest Path in Binary Matrix (LeetCode 1091)**
- **Twist:** Find shortest path from top-left to bottom-right in a binary matrix (8-directional)
- **Change:** BFS with 8 neighbors. Check start and end are 0.

**V4: Flood Fill (LeetCode 733)**
- **Twist:** Replace all connected pixels of a starting color with a new color
- **Change:** BFS/DFS from starting pixel. Stop when color != original.

```python
from collections import deque

def floodFill(image, sr, sc, color):
    original = image[sr][sc]
    if original == color:
        return image
    rows, cols = len(image), len(image[0])
    queue = deque([(sr, sc)])
    image[sr][sc] = color
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and image[nr][nc] == original:
                image[nr][nc] = color
                queue.append((nr, nc))
    return image
```

**Near Miss: Minimum Path Sum (LeetCode 64)**
- **Looks like:** Grid shortest path
- **But:** Weighted grid (each cell has a cost). BFS does not work because edge weights differ.
- **Lesson:** BFS finds shortest path in unweighted graphs. For weighted grids, use Dijkstra or DP.

---

## Archetype 11.2: DFS Traversal

### Recognition Signal (10 seconds)
Words: **"explore", "connected", "paths", "deep", "recursive", "backtrack", "mark visited"**

The question is always: **"Explore as far as possible along each branch before backtracking."**

### Core Structure
```python
def dfs(graph, node, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

### The Invariant
DFS fully explores one branch before moving to the next. This makes it ideal for detecting cycles (via recursion stack), exploring connected components, and pathfinding where any valid path suffices.

### Canonical Problem: Max Area of Island (LeetCode 695)
**Statement:** Given a grid, find the maximum area of an island.

```python
class Solution:
    def maxAreaOfIsland(self, grid):
        if not grid or not grid[0]:
            return 0
        rows, cols = len(grid), len(grid[0])
        max_area = 0

        def dfs(r, c):
            if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == 0:
                return 0
            grid[r][c] = 0  # Mark visited
            return 1 + dfs(r+1, c) + dfs(r-1, c) + dfs(r, c+1) + dfs(r, c-1)

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 1:
                    max_area = max(max_area, dfs(r, c))
        return max_area
```

### Variation Family

**V1: Clone Graph (LeetCode 133)**
- **Twist:** Deep copy a connected undirected graph
- **Change:** DFS/BFS with a hash map from original node to cloned node to avoid cycles.

```python
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def cloneGraph(node):
    if not node:
        return None
    old_to_new = {}
    def dfs(n):
        if n in old_to_new:
            return old_to_new[n]
        copy = Node(n.val)
        old_to_new[n] = copy
        for neighbor in n.neighbors:
            copy.neighbors.append(dfs(neighbor))
        return copy
    return dfs(node)
```

**V2: Pacific Atlantic Water Flow (LeetCode 417)**
- **Twist:** Find cells that can flow to both Pacific and Atlantic oceans
- **Change:** DFS from oceans inward. Intersection of reachable sets.

**V3: Surrounded Regions (LeetCode 130)**
- **Twist:** Capture all regions surrounded by 'X'. Do not capture regions on the border.
- **Change:** DFS from border 'O's to mark safe cells. Flip unmarked 'O's.

**V4: Number of Provinces (LeetCode 547)**
- **Twist:** Given adjacency matrix, count connected components
- **Change:** DFS from each unvisited node. Each DFS launch = one province.

```python
def findCircleNum(isConnected):
    n = len(isConnected)
    visited = [False] * n
    def dfs(i):
        for j in range(n):
            if isConnected[i][j] == 1 and not visited[j]:
                visited[j] = True
                dfs(j)
    provinces = 0
    for i in range(n):
        if not visited[i]:
            visited[i] = True
            dfs(i)
            provinces += 1
    return provinces
```

**Near Miss: Word Ladder (LeetCode 127)**
- **Looks like:** Pathfinding in a graph of words
- **But:** Shortest path in an unweighted graph => BFS, not DFS.
- **Lesson:** DFS explores depth; BFS explores breadth. Shortest path = BFS.

---

## Archetype 11.3: Cycle Detection

### Recognition Signal (10 seconds)
Words: **"cycle", "loop", "circular dependency", "deadlock", "valid tree", "course schedule"**

The question is always: **"Does this graph contain a cycle?"** or **"Can tasks be completed without circular dependencies?"**

### Core Structure
```python
def has_cycle(graph, n):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(node):
        color[node] = GRAY  # Currently in recursion stack
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return True  # Back edge -> cycle
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK  # Fully processed
        return False

    for i in range(n):
        if color[i] == WHITE and dfs(i):
            return True
    return False
```

### The Invariant
A directed graph has a cycle if and only if DFS encounters a back edge (an edge to a GRAY node). For undirected graphs, we avoid immediately revisiting the parent to prevent false cycles.

### Canonical Problem: Course Schedule (LeetCode 207)
**Statement:** Given numCourses and prerequisites, determine if all courses can be finished.

```python
from collections import defaultdict

class Solution:
    def canFinish(self, numCourses, prerequisites):
        graph = defaultdict(list)
        for a, b in prerequisites:
            graph[b].append(a)

        WHITE, GRAY, BLACK = 0, 1, 2
        state = [WHITE] * numCourses

        def dfs(node):
            state[node] = GRAY
            for neighbor in graph[node]:
                if state[neighbor] == GRAY:
                    return False  # Cycle detected
                if state[neighbor] == WHITE and not dfs(neighbor):
                    return False
            state[node] = BLACK
            return True

        for i in range(numCourses):
            if state[i] == WHITE and not dfs(i):
                return False
        return True
```

### Variation Family

**V1: Course Schedule II (LeetCode 210)**
- **Twist:** Return a valid ordering of courses to finish all courses
- **Change:** Topological sort (DFS post-order reverse, or Kahn's BFS). Covered in Archetype 11.4.

**V2: Graph Valid Tree (LeetCode 261)**
- **Twist:** Check if graph is a valid tree (connected and no cycles)
- **Change:** Undirected graph. Use Union-Find or DFS counting edges: a tree on n nodes has exactly n-1 edges and is connected.

```python
def validTree(n, edges):
    if len(edges) != n - 1:
        return False
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    visited = set()
    def dfs(node, parent):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor == parent:
                continue
            if neighbor in visited:
                return False
            if not dfs(neighbor, node):
                return False
        return True
    return dfs(0, -1) and len(visited) == n
```

**V3: Find Eventual Safe States (LeetCode 802)**
- **Twist:** A node is safe if every possible path from it leads to a terminal node. Find all safe nodes.
- **Change:** Reverse the logic: nodes in cycles or leading to cycles are unsafe. DFS with three colors.

```python
def eventualSafeNodes(graph):
    n = len(graph)
    NOT_VISITED, VISITING, SAFE = 0, 1, 2
    state = [NOT_VISITED] * n

    def dfs(node):
        if state[node] == VISITING:
            return False
        if state[node] == SAFE:
            return True
        state[node] = VISITING
        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False
        state[node] = SAFE
        return True

    return [i for i in range(n) if dfs(i)]
```

**V4: Redundant Connection (LeetCode 684)**
- **Twist:** An undirected graph that started as a tree gained one extra edge. Find that edge.
- **Change:** Union-Find is easiest. The first edge connecting two already-connected nodes is the redundant one.

**Near Miss: Detect Cycle in a Linked List (LeetCode 141)**
- **Looks like:** Cycle detection
- **But:** Linked list cycle uses Floyd's Tortoise and Hare (two pointers), not graph DFS.
- **Lesson:** Cycle detection depends on the data structure. Linked lists have a unique O(1) space solution.

---

## Archetype 11.4: Topological Sort

### Recognition Signal (10 seconds)
Words: **"order", "prerequisites", "dependencies", "schedule", "before", "topological", "compilation order"**

The question is always: **"Given dependencies, find a valid linear ordering."**

### Core Structure (Kahn's Algorithm — BFS)
```python
from collections import deque, defaultdict

def topological_sort(num_nodes, edges):
    graph = defaultdict(list)
    in_degree = [0] * num_nodes
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1

    queue = deque([i for i in range(num_nodes) if in_degree[i] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result if len(result) == num_nodes else []
```

### The Invariant
Kahn's algorithm repeatedly removes nodes with zero in-degree. Any valid topological ordering must place such nodes before their dependents. If fewer than n nodes are processed, a cycle exists.

### Canonical Problem: Course Schedule II (LeetCode 210)
**Statement:** Return the ordering of courses to finish all courses.

```python
from collections import deque, defaultdict

class Solution:
    def findOrder(self, numCourses, prerequisites):
        graph = defaultdict(list)
        in_degree = [0] * numCourses
        for a, b in prerequisites:
            graph[b].append(a)
            in_degree[a] += 1

        queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
        order = []

        while queue:
            course = queue.popleft()
            order.append(course)
            for nxt in graph[course]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        return order if len(order) == numCourses else []
```

### Variation Family

**V1: Alien Dictionary (LeetCode 269)**
- **Twist:** Derive character order from a sorted list of words
- **Change:** Compare adjacent words to infer edges between differing characters. Then topological sort.

**V2: Sequence Reconstruction (LeetCode 444)**
- **Twist:** Check if original sequence is the only valid topological order
- **Change:** At each step, exactly one node must have in-degree 0. If ever > 1, order is not unique.

**V3: Parallel Courses (LeetCode 1136)**
- **Twist:** Minimum semesters to finish all courses
- **Change:** Topological sort level by level (BFS). Count semesters = number of BFS layers.

```python
def minimumSemesters(n, relations):
    graph = [[] for _ in range(n)]
    in_degree = [0] * n
    for u, v in relations:
        graph[u-1].append(v-1)
        in_degree[v-1] += 1
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    semesters = 0
    studied = 0
    while queue:
        semesters += 1
        for _ in range(len(queue)):
            node = queue.popleft()
            studied += 1
            for nxt in graph[node]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)
    return semesters if studied == n else -1
```

**V4: Longest Path in a Directed Acyclic Graph**
- **Twist:** Find longest path in a DAG
- **Change:** Process nodes in topological order. Relax edges to update longest distance.

**Near Miss: Reconstruct Itinerary (LeetCode 332)**
- **Looks like:** Ordering with constraints
- **But:** Requires Hierholzer's algorithm for Eulerian path, not topological sort.
- **Lesson:** Topological sort handles dependency ordering. Eulerian paths require traversing every edge exactly once.

---

## Archetype 11.5: Bipartite Check

### Recognition Signal (10 seconds)
Words: **"bipartite", "two groups", "two colors", "divide", "conflict", "possible bipartition"**

The question is always: **"Can we color the graph with two colors such that no adjacent nodes share the same color?"**

### Core Structure
```python
from collections import deque

def is_bipartite(graph):
    n = len(graph)
    color = [-1] * n  # -1 = uncolored, 0/1 = colors

    for i in range(n):
        if color[i] != -1:
            continue
        queue = deque([i])
        color[i] = 0
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if color[neighbor] == -1:
                    color[neighbor] = color[node] ^ 1
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:
                    return False
    return True
```

### The Invariant
BFS assigns alternating colors. If we ever try to assign a neighbor the same color as the current node, the graph contains an odd-length cycle and is not bipartite.

### Canonical Problem: Is Graph Bipartite? (LeetCode 785)
**Statement:** Determine if a graph is bipartite.

```python
from collections import deque

class Solution:
    def isBipartite(self, graph):
        n = len(graph)
        color = [-1] * n

        for start in range(n):
            if color[start] != -1:
                continue
            queue = deque([start])
            color[start] = 0
            while queue:
                node = queue.popleft()
                for neighbor in graph[node]:
                    if color[neighbor] == -1:
                        color[neighbor] = color[node] ^ 1
                        queue.append(neighbor)
                    elif color[neighbor] == color[node]:
                        return False
        return True
```

### Variation Family

**V1: Possible Bipartition (LeetCode 886)**
- **Twist:** Given dislike pairs (edges), can we split people into two groups?
- **Change:** Build graph from dislike pairs, then standard bipartite check.

```python
def possibleBipartition(n, dislikes):
    graph = [[] for _ in range(n)]
    for u, v in dislikes:
        graph[u-1].append(v-1)
        graph[v-1].append(u-1)
    color = [-1] * n
    for i in range(n):
        if color[i] != -1:
            continue
        stack = [i]
        color[i] = 0
        while stack:
            node = stack.pop()
            for nei in graph[node]:
                if color[nei] == -1:
                    color[nei] = color[node] ^ 1
                    stack.append(nei)
                elif color[nei] == color[node]:
                    return False
    return True
```

**V2: Coloring A Border (LeetCode 1034)**
- **Twist:** Color the border of a connected component
- **Change:** DFS/BFS to find component. Color cells on the border (adjacent to different color or grid edge).

**V3: Flower Planting With No Adjacent (LeetCode 1042)**
- **Twist:** Plant flowers in gardens so adjacent gardens have different types
- **Change:** Graph is very sparse (at most 3 neighbors). Greedy coloring with 4 colors always works.

**Near Miss: Course Schedule (LeetCode 207)**
- **Looks like:** Dividing into groups with constraints
- **But:** Directed dependencies, not mutual exclusion. Requires topological sort or cycle detection, not bipartite check.
- **Lesson:** Bipartite = mutual exclusion edges (undirected). Prerequisites = directed ordering.

---

## Archetype 11.6: Connected Components

### Recognition Signal (10 seconds)
Words: **"connected components", "provinces", "friend circles", "groups", "networks", "clusters"**

The question is always: **"How many disjoint groups of connected nodes are there?"** or **"Which nodes belong to the same component?"**

### Core Structure
```python
def count_components(n, graph):
    visited = [False] * n
    components = 0

    def dfs(node):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor)

    for i in range(n):
        if not visited[i]:
            dfs(i)
            components += 1
    return components
```

### The Invariant
Each DFS/BFS launch from an unvisited node discovers exactly one connected component. Every node in that component is marked visited, so it will not be counted again.

### Canonical Problem: Number of Provinces (LeetCode 547)
**Statement:** Given adjacency matrix of friendships, find total friend circles.

```python
class Solution:
    def findCircleNum(self, isConnected):
        n = len(isConnected)
        visited = [False] * n

        def dfs(i):
            visited[i] = True
            for j in range(n):
                if isConnected[i][j] == 1 and not visited[j]:
                    dfs(j)

        provinces = 0
        for i in range(n):
            if not visited[i]:
                dfs(i)
                provinces += 1
        return provinces
```

### Variation Family

**V1: Number of Operations to Make Network Connected (LeetCode 1319)**
- **Twist:** Find minimum cables to connect all computers
- **Change:** If graph has n nodes and enough edges, answer = number of components - 1. Check edge count first.

```python
def makeConnected(n, connections):
    if len(connections) < n - 1:
        return -1
    graph = [[] for _ in range(n)]
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)
    visited = [False] * n
    def dfs(i):
        visited[i] = True
        for j in graph[i]:
            if not visited[j]:
                dfs(j)
    components = 0
    for i in range(n):
        if not visited[i]:
            dfs(i)
            components += 1
    return components - 1
```

**V2: Count Unreachable Pairs of Nodes in an Undirected Graph (LeetCode 2316)**
- **Twist:** Count number of unreachable pairs
- **Change:** Find component sizes. For each component of size s, add s * (n - s) unreachable pairs. Divide by 2 to avoid double counting.

**V3: Critical Connections in a Network (LeetCode 1192)**
- **Twist:** Find bridges (edges whose removal increases component count)
- **Change:** Tarjan's algorithm (DFS low-link values). Covered in Pattern 12.

**Near Miss: Accounts Merge (LeetCode 721)**
- **Looks like:** Connected components
- **But:** Nodes are email addresses linked by shared names. Requires building a graph of emails + name mapping, then extracting components.
- **Lesson:** Sometimes nodes aren't explicitly given; you must construct the graph first.

---

## Archetype 11.7: Word Ladder

### Recognition Signal (10 seconds)
Words: **"word ladder", "transformation", "one letter change", "shortest sequence", "beginWord", "endWord"**

The question is always: **"Find the shortest sequence of single-character transformations from a start word to an end word, where every intermediate word is in a dictionary."**

### Core Structure
```python
from collections import deque

def ladder_length(beginWord, endWord, wordList):
    word_set = set(wordList)
    if endWord not in wordSet:
        return 0

    queue = deque([(beginWord, 1)])
    while queue:
        word, steps = queue.popleft()
        if word == endWord:
            return steps
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word in word_set:
                    word_set.remove(next_word)
                    queue.append((next_word, steps + 1))
    return 0
```

### The Invariant
Each BFS level represents one transformation step. Removing words from the set as we visit them guarantees we don't revisit and ensures the first time we reach endWord is via the shortest path.

### Canonical Problem: Word Ladder (LeetCode 127)
**Statement:** Return the length of the shortest transformation sequence from beginWord to endWord.

```python
from collections import deque

class Solution:
    def ladderLength(self, beginWord, endWord, wordList):
        word_set = set(wordList)
        if endWord not in word_set:
            return 0

        queue = deque([(beginWord, 1)])
        while queue:
            word, length = queue.popleft()
            if word == endWord:
                return length
            for i in range(len(word)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    next_word = word[:i] + c + word[i+1:]
                    if next_word in word_set:
                        word_set.remove(next_word)
                        queue.append((next_word, length + 1))
        return 0
```

### Variation Family

**V1: Word Ladder II (LeetCode 126)**
- **Twist:** Return ALL shortest transformation sequences
- **Change:** BFS to build parent map of shortest paths, then DFS backtrack from endWord to beginWord.

```python
from collections import deque, defaultdict

def findLadders(beginWord, endWord, wordList):
    word_set = set(wordList)
    if endWord not in word_set:
        return []

    # BFS to build adjacency of shortest paths
    parents = defaultdict(list)
    visited = {beginWord}
    found = False
    queue = deque([beginWord])

    while queue and not found:
        level_visited = set()
        for _ in range(len(queue)):
            word = queue.popleft()
            for i in range(len(word)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    nxt = word[:i] + c + word[i+1:]
                    if nxt in word_set:
                        if nxt not in visited:
                            parents[nxt].append(word)
                            level_visited.add(nxt)
                            if nxt == endWord:
                                found = True
                        elif nxt in level_visited:
                            parents[nxt].append(word)
        for w in level_visited:
            visited.add(w)
            queue.append(w)

    # Backtrack from endWord
    res = []
    def backtrack(word, path):
        if word == beginWord:
            res.append(path[::-1])
            return
        for p in parents[word]:
            backtrack(p, path + [p])
    backtrack(endWord, [endWord])
    return res
```

**V2: Minimum Genetic Mutation (LeetCode 433)**
- **Twist:** DNA strings, mutations change one character to A/C/G/T
- **Change:** Exact same BFS pattern with DNA alphabet.

**V3: Open the Lock (LeetCode 752)**
- **Twist:** 4-digit lock, turn one wheel at a time, avoid deadends
- **Change:** BFS on state space. Each state is a string. Neighbors are +1/-1 on each wheel.

```python
from collections import deque

def openLock(deadends, target):
    dead = set(deadends)
    if '0000' in dead:
        return -1
    queue = deque([('0000', 0)])
    visited = {'0000'}
    while queue:
        state, steps = queue.popleft()
        if state == target:
            return steps
        for i in range(4):
            digit = int(state[i])
            for move in (-1, 1):
                new_digit = (digit + move) % 10
                new_state = state[:i] + str(new_digit) + state[i+1:]
                if new_state not in visited and new_state not in dead:
                    visited.add(new_state)
                    queue.append((new_state, steps + 1))
    return -1
```

**Near Miss: Minimum Path Sum (LeetCode 64)**
- **Looks like:** Grid shortest path
- **But:** Each step has a weight (grid cell value). BFS assumes uniform edge weights.
- **Lesson:** Word Ladder assumes each transformation costs 1. If costs vary, use Dijkstra (Pattern 12).

---

## Pattern 11 Mastery Checklist

Before moving to Pattern 12, confirm you can:

- [ ] Implement BFS and DFS from scratch for both adjacency lists and grids
- [ ] Detect cycles in directed graphs using three-color DFS
- [ ] Generate a topological ordering using Kahn's algorithm
- [ ] Check bipartiteness with BFS coloring
- [ ] Count connected components by launching DFS from each unvisited node
- [ ] Solve Word Ladder with BFS on implicit graph of one-letter mutations
- [ ] Distinguish when to use BFS (shortest unweighted) vs DFS (exploration, cycles)

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Reusing visited set across components | Only finds one component | Reset or use per-component visited |
| Forgetting to mark visited before enqueue | Nodes queued multiple times, exponential blowup | Mark visited immediately on discovery |
| Treating undirected edge as two directed edges in cycle detection | False cycle between parent and child | Pass parent to DFS and skip it |
| Using DFS for shortest path in unweighted graph | May find a longer path first | Always use BFS for shortest path (unweighted) |
| Not removing words from word_set in Word Ladder | Infinite loops or revisiting states | Remove (or use a separate visited set) immediately |
| Off-by-one in BFS level counting | Wrong distance returned | Initialize start distance correctly (usually 1 for node count) |

---

## Pattern Blends (What Comes Next)

Graphs do not live in isolation. They blend with:

- **BFS + Bitmask:** Shortest path problems with state compression (e.g., shortest path to collect all keys)
- **DFS + Backtracking:** Hamiltonian paths, permutations on graph nodes
- **Topological Sort + Dynamic Programming:** Longest path in a DAG
- **Graph + Union-Find:** Connected components, redundant connections (Pattern 12)
- **Graph + Trie:** Word search on a board (Pattern 10)

---

*Next: Pattern 12 — Advanced Graphs*
