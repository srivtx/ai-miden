# Pattern 11: Graphs - Drills Part 2
## Warm-Ups + Core Drills (15 Problems)

---

### 1. 1971. Find if Path Exists in Graph
**Archetype:** 11.2 DFS Traversal
**Type:** Warm-Up
**Statement:** Given a bi-directional graph and source/destination nodes, determine if a valid path exists.
**Why it fits:** This is the most basic graph connectivity question. It tests whether you can build an adjacency list and run DFS or BFS without getting lost in implementation details.
**The Twist:** The graph is undirected and unweighted. Either DFS or BFS works; the key is correctly building the adjacency list in both directions.
**Code Skeleton:**
```python
from collections import deque

def validPath(n: int, edges: list[list[int]], source: int, destination: int) -> bool:
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited = [False] * n
    queue = deque([source])
    visited[source] = True

    while queue:
        node = queue.popleft()
        if node == destination:
            return True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                visited[neighbor] = True
                queue.append(neighbor)
    return False
```

### 2. 200. Number of Islands
**Archetype:** 11.1 BFS Traversal / 11.2 DFS Traversal
**Type:** Warm-Up
**Statement:** Given a 2D grid of '1's (land) and '0's (water), count the number of islands.
**Why it fits:** This is the canonical grid-as-graph problem. Each land cell is a node connected to its 4 neighbors. It teaches you to traverse a grid using graph algorithms.
**The Twist:** The grid is implicit; you do not have an explicit adjacency list. You must generate neighbors on the fly with boundary checks.
**Code Skeleton:**
```python
def numIslands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0':
            return
        grid[r][c] = '0'
        dfs(r+1, c)
        dfs(r-1, c)
        dfs(r, c+1)
        dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1
    return count
```

### 3. 695. Max Area of Island
**Archetype:** 11.2 DFS Traversal
**Type:** Warm-Up
**Statement:** Given a 2D grid, return the maximum area of an island.
**Why it fits:** This is a direct extension of Number of Islands. Instead of just counting islands, you measure their size by accumulating cell counts during DFS.
**The Twist:** You must return the maximum area, not just the count. This requires tracking a running sum during traversal and comparing it to a global maximum.
**Code Skeleton:**
```python
def maxAreaOfIsland(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    max_area = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == 0:
            return 0
        grid[r][c] = 0
        return 1 + dfs(r+1, c) + dfs(r-1, c) + dfs(r, c+1) + dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                max_area = max(max_area, dfs(r, c))
    return max_area
```

### 4. 733. Flood Fill
**Archetype:** 11.2 DFS Traversal
**Type:** Warm-Up
**Statement:** Perform a flood fill starting from a given pixel and replacing its color and all connected same-colored pixels.
**Why it fits:** This is DFS on an implicit grid graph. It teaches you to avoid infinite loops by checking if the neighbor already has the target color.
**The Twist:** If the starting pixel already has the new color, you must return immediately to avoid an infinite loop.
**Code Skeleton:**
```python
def floodFill(image: list[list[int]], sr: int, sc: int, color: int) -> list[list[int]]:
    rows, cols = len(image), len(image[0])
    original = image[sr][sc]
    if original == color:
        return image

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or image[r][c] != original:
            return
        image[r][c] = color
        dfs(r+1, c)
        dfs(r-1, c)
        dfs(r, c+1)
        dfs(r, c-1)

    dfs(sr, sc)
    return image
```

### 5. 841. Keys and Rooms
**Archetype:** 11.2 DFS Traversal
**Type:** Warm-Up
**Statement:** Given a list of rooms where each room contains keys to other rooms, determine if you can visit all rooms starting from room 0.
**Why it fits:** This is a directed graph reachability problem disguised as a rooms-and-keys puzzle. It tests basic DFS/BFS on an explicit adjacency list.
**The Twist:** The graph is directed (keys are one-way). You must not assume rooms are bidirectionally connected.
**Code Skeleton:**
```python
from collections import deque

def canVisitAllRooms(rooms: list[list[int]]) -> bool:
    n = len(rooms)
    visited = [False] * n
    queue = deque([0])
    visited[0] = True
    count = 1

    while queue:
        room = queue.popleft()
        for key in rooms[room]:
            if not visited[key]:
                visited[key] = True
                count += 1
                queue.append(key)

    return count == n
```

### 6. 133. Clone Graph
**Archetype:** 11.1 BFS Traversal
**Type:** Core Drill
**Statement:** Return a deep copy of a connected undirected graph.
**Why it fits:** This is the canonical graph cloning problem. It requires traversing the graph while maintaining a mapping from original nodes to copied nodes.
**The Twist:** You cannot simply traverse; you must create new node objects and wire their neighbors correctly. A hash map from original to clone is essential.
**Code Skeleton:**
```python
from collections import deque

class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

class Solution:
    def cloneGraph(self, node: 'Node') -> 'Node':
        if not node:
            return None
        old_to_new = {}
        queue = deque([node])
        old_to_new[node] = Node(node.val)

        while queue:
            current = queue.popleft()
            for neighbor in current.neighbors:
                if neighbor not in old_to_new:
                    old_to_new[neighbor] = Node(neighbor.val)
                    queue.append(neighbor)
                old_to_new[current].neighbors.append(old_to_new[neighbor])

        return old_to_new[node]
```

### 7. 994. Rotting Oranges
**Archetype:** 11.1 BFS Traversal
**Type:** Core Drill
**Statement:** Return the minimum number of minutes until no cell has a fresh orange, or -1 if impossible.
**Why it fits:** This is multi-source BFS. All initially rotten oranges spread simultaneously level by level, which is exactly how BFS explores an unweighted graph.
**The Twist:** You must enqueue all initially rotten oranges before starting BFS. Processing them one by one inside the main loop would simulate sequential rotting, not simultaneous.
**Code Skeleton:**
```python
from collections import deque

def orangesRotting(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    while queue:
        r, c, minutes = queue.popleft()
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                fresh -= 1
                queue.append((nr, nc, minutes + 1))

    return minutes if fresh == 0 else -1
```

### 8. 417. Pacific Atlantic Water Flow
**Archetype:** 11.1 BFS Traversal
**Type:** Core Drill
**Statement:** Find grid coordinates where water can flow to both the Pacific and Atlantic oceans.
**Why it fits:** This is reverse BFS/DFS. Instead of flowing from cells to oceans, you start from ocean boundaries and flow inland to cells of equal or greater height.
**The Twist:** Running BFS from every cell independently is too slow. The reverse approach (ocean to cells) reduces the problem to two BFS traversals from the borders.
**Code Skeleton:**
```python
def pacificAtlantic(heights: list[list[int]]) -> list[list[int]]:
    rows, cols = len(heights), len(heights[0])
    pacific = [[False] * cols for _ in range(rows)]
    atlantic = [[False] * cols for _ in range(rows)]

    def dfs(r, c, visited, prev_height):
        if r < 0 or r >= rows or c < 0 or c >= cols or visited[r][c] or heights[r][c] < prev_height:
            return
        visited[r][c] = True
        dfs(r+1, c, visited, heights[r][c])
        dfs(r-1, c, visited, heights[r][c])
        dfs(r, c+1, visited, heights[r][c])
        dfs(r, c-1, visited, heights[r][c])

    for c in range(cols):
        dfs(0, c, pacific, heights[0][c])
        dfs(rows-1, c, atlantic, heights[rows-1][c])
    for r in range(rows):
        dfs(r, 0, pacific, heights[r][0])
        dfs(r, cols-1, atlantic, heights[r][cols-1])

    ans = []
    for r in range(rows):
        for c in range(cols):
            if pacific[r][c] and atlantic[r][c]:
                ans.append([r, c])
    return ans
```

### 9. 542. 01 Matrix
**Archetype:** 11.1 BFS Traversal
**Type:** Core Drill
**Statement:** Given a binary matrix, return the distance of the nearest 0 for each cell.
**Why it fits:** This is multi-source BFS from all 0 cells simultaneously. Each level of BFS represents cells at distance 1, 2, 3, etc.
**The Twist:** Starting BFS from every 1 independently is O((MN)^2). Starting from all 0s at once guarantees the first time you reach a 1, it is via the shortest path.
**Code Skeleton:**
```python
from collections import deque

def updateMatrix(mat: list[list[int]]) -> list[list[int]]:
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
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                queue.append((nr, nc))
    return dist
```

### 10. 207. Course Schedule
**Archetype:** 11.3 Cycle Detection
**Type:** Core Drill
**Statement:** Given prerequisites, determine if you can finish all courses.
**Why it fits:** This is the canonical cycle detection in a directed graph. If there is a cycle, some courses have circular dependencies and cannot be completed.
**The Twist:** You must detect a cycle in a directed graph. The 3-color state DFS (unvisited, visiting, visited) is the cleanest way to do this.
**Code Skeleton:**
```python
def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    graph = [[] for _ in range(numCourses)]
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    state = [0] * numCourses  # 0=unvisited, 1=visiting, 2=visited

    def has_cycle(node):
        if state[node] == 1:
            return True
        if state[node] == 2:
            return False
        state[node] = 1
        for neighbor in graph[node]:
            if has_cycle(neighbor):
                return True
        state[node] = 2
        return False

    for i in range(numCourses):
        if state[i] == 0 and has_cycle(i):
            return False
    return True
```

### 11. 210. Course Schedule II
**Archetype:** 11.4 Topological Sort
**Type:** Core Drill
**Statement:** Return a valid ordering of courses you should take to finish all courses.
**Why it fits:** This is the canonical topological sort problem. If no valid ordering exists (cycle), return an empty array.
**The Twist:** Kahn's algorithm (in-degree BFS) is usually preferred here because it naturally produces a valid order. You must verify the result length equals numCourses to detect cycles.
**Code Skeleton:**
```python
from collections import deque

def findOrder(numCourses: int, prerequisites: list[list[int]]) -> list[int]:
    graph = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result if len(result) == numCourses else []
```

### 12. 785. Is Graph Bipartite?
**Archetype:** 11.5 Bipartite Check
**Type:** Core Drill
**Statement:** Determine if a graph is bipartite: can nodes be split into two independent sets such that every edge connects a node in one set to the other.
**Why it fits:** This is the canonical bipartite check. You color nodes with two colors; if you ever find an edge connecting two nodes of the same color, the graph is not bipartite.
**The Twist:** The graph may be disconnected. You must loop through all nodes and start a new BFS/DFS if an uncolored node is found.
**Code Skeleton:**
```python
from collections import deque

def isBipartite(graph: list[list[int]]) -> bool:
    color = {}
    for node in range(len(graph)):
        if node not in color:
            color[node] = 0
            queue = deque([node])
            while queue:
                current = queue.popleft()
                for neighbor in graph[current]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[current]
                        queue.append(neighbor)
                    elif color[neighbor] == color[current]:
                        return False
    return True
```

### 13. 886. Possible Bipartition
**Archetype:** 11.5 Bipartite Check
**Type:** Core Drill
**Statement:** Given a set of people and their dislikes, determine if you can split everyone into two groups so that no two people in the same group dislike each other.
**Why it fits:** This is bipartite check on an implicit graph. Each dislike is an undirected edge. You need to check if the dislike graph is bipartite.
**The Twist:** The graph is given as an edge list of dislikes, not an adjacency list. You must build the adjacency list first, then run the bipartite check.
**Code Skeleton:**
```python
from collections import deque

def possibleBipartition(n: int, dislikes: list[list[int]]) -> bool:
    graph = [[] for _ in range(n + 1)]
    for u, v in dislikes:
        graph[u].append(v)
        graph[v].append(u)

    color = {}
    for node in range(1, n + 1):
        if node not in color:
            color[node] = 0
            queue = deque([node])
            while queue:
                current = queue.popleft()
                for neighbor in graph[current]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[current]
                        queue.append(neighbor)
                    elif color[neighbor] == color[current]:
                        return False
    return True
```

### 14. 547. Number of Provinces
**Archetype:** 11.6 Connected Components
**Type:** Core Drill
**Statement:** Given an adjacency matrix of friendships, find the total number of provinces (connected components).
**Why it fits:** This is the canonical connected components problem. Each province is a connected component in the undirected graph.
**The Twist:** The input is an adjacency matrix, not an edge list. You must iterate over the row of a node to find its neighbors, or convert to an adjacency list first.
**Code Skeleton:**
```python
def findCircleNum(isConnected: list[list[int]]) -> int:
    n = len(isConnected)
    visited = [False] * n
    provinces = 0

    def dfs(node):
        visited[node] = True
        for neighbor in range(n):
            if isConnected[node][neighbor] == 1 and not visited[neighbor]:
                dfs(neighbor)

    for i in range(n):
        if not visited[i]:
            dfs(i)
            provinces += 1
    return provinces
```

### 15. 127. Word Ladder
**Archetype:** 11.7 Word Ladder
**Type:** Core Drill
**Statement:** Return the length of the shortest transformation sequence from beginWord to endWord, changing one letter at a time.
**Why it fits:** This is the canonical BFS shortest path problem on an implicit graph. Each word is a node; edges exist between words differing by one letter.
**The Twist:** The graph is implicit and massive. You cannot build it upfront. Instead, generate all 26 possible one-letter mutations and check membership in the word list.
**Code Skeleton:**
```python
from collections import deque

def ladderLength(beginWord: str, endWord: str, wordList: list[str]) -> int:
    wordSet = set(wordList)
    if endWord not in wordSet:
        return 0

    queue = deque([(beginWord, 1)])
    visited = {beginWord}

    while queue:
        word, length = queue.popleft()
        if word == endWord:
            return length
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word in wordSet and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, length + 1))
    return 0
```
