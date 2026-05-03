# Pattern 11: Graphs — Practice Problems

## BFS Traversal

### 200. Number of Islands
**Statement:** Count islands in grid.
**Intuition:** BFS/DFS from each unvisited land cell. Mark visited.
**Code (BFS):**
```python
def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    islands = 0
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                islands += 1
                queue = [(r, c)]
                grid[r][c] = '0'
                while queue:
                    cr, cc = queue.pop(0)
                    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                            grid[nr][nc] = '0'
                            queue.append((nr, nc))
    return islands
```

### 695. Max Area of Island
**Statement:** Max area of island.
**Intuition:** BFS/DFS. Track area.

### 994. Rotting Oranges
**Statement:** Min minutes until no fresh oranges.
**Intuition:** Multi-source BFS. Start with all rotten oranges.

### 417. Pacific Atlantic Water Flow
**Statement:** Cells that can flow to both oceans.
**Intuition:** BFS from ocean borders. Intersection of reachable sets.

### 286. Walls and Gates
**Statement:** Fill empty rooms with distance to nearest gate.
**Intuition:** Multi-source BFS from all gates.

### 133. Clone Graph
**Statement:** Deep copy connected undirected graph.
**Intuition:** BFS/DFS. Hash map: original node -> cloned node.

---

## DFS Traversal

### 797. All Paths From Source to Target
**Statement:** All paths from 0 to n-1 in DAG.
**Intuition:** DFS. Backtrack.

### 1971. Find if Path Exists in Graph
**Statement:** Does path exist from source to destination?
**Intuition:** DFS or Union-Find.

---

## Cycle Detection

### 207. Course Schedule
**Statement:** Can finish all courses? (No cycle?)
**Intuition:** Cycle detection in directed graph.
**Code (3-color DFS):**
```python
def can_finish(num_courses, prerequisites):
    graph = [[] for _ in range(num_courses)]
    for course, prereq in prerequisites:
        graph[prereq].append(course)
    
    state = [0] * num_courses  # 0=unvisited, 1=visiting, 2=visited
    
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
    
    for i in range(num_courses):
        if state[i] == 0 and has_cycle(i):
            return False
    return True
```

### 261. Graph Valid Tree
**Statement:** Is graph a valid tree?
**Intuition:** Connected and no cycle. n nodes, n-1 edges.

---

## Topological Sort

### 210. Course Schedule II
**Statement:** Return valid ordering of courses.
**Intuition:** Topological sort. Kahn's algorithm.
**Code:**
```python
def find_order(num_courses, prerequisites):
    graph = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses
    
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1
    
    queue = [i for i in range(num_courses) if in_degree[i] == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result if len(result) == num_courses else []
```

### 269. Alien Dictionary
**Statement:** Derive order of letters from sorted words.
**Intuition:** Compare adjacent words. Build graph of character order. Topological sort.

---

## Bipartite

### 785. Is Graph Bipartite?
**Statement:** Can nodes be divided into two groups?
**Intuition:** BFS/DFS with coloring. Check no adjacent same color.

### 886. Possible Bipartition
**Statement:** Can group be divided given dislikes?
**Intuition:** Build graph from dislikes. Bipartite check.

---

## Connected Components

### 547. Number of Provinces
**Statement:** Number of connected components in adjacency matrix.
**Intuition:** DFS/BFS from each unvisited node. Or Union-Find.

### 721. Accounts Merge
**Statement:** Merge accounts with common emails.
**Intuition:** Build graph: email -> account. DFS to find connected components.

---

## Word Ladder

### 127. Word Ladder
**Statement:** Shortest transformation sequence from begin to end.
**Intuition:** BFS. One letter change at a time.
**Code:**
```python
def ladder_length(begin_word, end_word, word_list):
    word_set = set(word_list)
    if end_word not in word_set:
        return 0
    
    queue = [(begin_word, 1)]
    while queue:
        word, steps = queue.pop(0)
        if word == end_word:
            return steps
        
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word in word_set:
                    word_set.remove(next_word)
                    queue.append((next_word, steps + 1))
    return 0
```

### 126. Word Ladder II
**Statement:** All shortest transformation sequences.
**Intuition:** BFS to build graph of shortest paths. DFS to collect all paths.

---

## Mixed Drill Set

1. 200 — Number of islands
2. 207 — Course schedule (cycle detection)
3. 210 — Course schedule II (topological sort)
4. 127 — Word ladder
5. 785 — Is bipartite?
6. 133 — Clone graph
7. 994 — Rotting oranges
8. 417 — Pacific Atlantic
9. 547 — Number of provinces
10. 721 — Accounts merge
