# Pattern 11: Graphs (BFS/DFS)

> **Pattern Recognition:** When you see "network", "connected", "path", "shortest", "dependencies", "islands", "friend circles" — think graph traversal.
>
> **Fundamental Insight:** Graphs model relationships. BFS explores level by level (good for shortest path in unweighted graphs). DFS explores deep first (good for connectivity, cycles, topological sort).

---

## Archetype 11.1: BFS Traversal

### Recognition Signal
Words: **"level order", "shortest path", "minimum steps", "unweighted"**

### Template
```python
from collections import deque

def bfs(start):
    visited = set([start])
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

### Problems
- Number of Islands (LeetCode 200)
- Clone Graph (LeetCode 133)
- Pacific Atlantic Water Flow (LeetCode 417)
- Rotting Oranges (LeetCode 994)
- Walls and Gates (LeetCode 286)

---

## Archetype 11.2: DFS Traversal

### Recognition Signal
Words: **"connected components", "find path", "exists path", "deep"**

### Template
```python
def dfs(node, visited):
    if node in visited:
        return
    visited.add(node)
    for neighbor in graph[node]:
        dfs(neighbor, visited)
```

### Problems
- Number of Islands (LeetCode 200) — BFS or DFS
- Max Area of Island (LeetCode 695)
- Find if Path Exists in Graph (LeetCode 1971)
- All Paths From Source to Target (LeetCode 797)

---

## Archetype 11.3: Cycle Detection

### Recognition Signal
Words: **"course schedule", "prerequisites", "detect cycle", "valid tree"**

### Template: DFS with states
```python
def has_cycle(graph, n):
    # 0 = unvisited, 1 = visiting, 2 = visited
    state = [0] * n
    
    def dfs(node):
        if state[node] == 1:
            return True  # Cycle!
        if state[node] == 2:
            return False
        state[node] = 1
        for neighbor in graph[node]:
            if dfs(neighbor):
                return True
        state[node] = 2
        return False
    
    for i in range(n):
        if state[i] == 0 and dfs(i):
            return True
    return False
```

### Problems
- Course Schedule (LeetCode 207)
- Course Schedule II (LeetCode 210)
- Graph Valid Tree (LeetCode 261)

---

## Archetype 11.4: Topological Sort

### Recognition Signal
Words: **"order", "prerequisites", "schedule", "sequence", "dependencies"**

### Template: Kahn's Algorithm (BFS)
```python
def topological_sort(num_courses, prerequisites):
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

### Problems
- Course Schedule II (LeetCode 210)
- Alien Dictionary (LeetCode 269)
- Sequence Reconstruction (LeetCode 444)

---

## Archetype 11.5: Bipartite Check

### Recognition Signal
Words: **"bipartite", "two groups", "color", "possible bipartition"**

### Template
```python
def is_bipartite(graph):
    color = {}
    for node in range(len(graph)):
        if node not in color:
            color[node] = 0
            queue = [node]
            while queue:
                current = queue.pop(0)
                for neighbor in graph[current]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[current]
                        queue.append(neighbor)
                    elif color[neighbor] == color[current]:
                        return False
    return True
```

### Problems
- Is Graph Bipartite? (LeetCode 785)
- Possible Bipartition (LeetCode 886)

---

## Archetype 11.6: Connected Components

### Recognition Signal
Words: **"number of provinces", "friend circles", "connected", "components"**

### Problems
- Number of Provinces (LeetCode 547)
- Number of Connected Components in Undirected Graph (LeetCode 323)
- Friend Circles (LeetCode 547 same)
- Accounts Merge (LeetCode 721) — Union-Find or DFS

---

## Archetype 11.7: Word Ladder

### Recognition Signal
Words: **"word ladder", "transformation", "one letter change", "shortest sequence"**

### Problems
- Word Ladder (LeetCode 127)
- Word Ladder II (LeetCode 126)

**Word Ladder is classic BFS.**

---

## Mastery Checklist
- [ ] BFS level order with queue
- [ ] DFS recursively and iteratively (with stack)
- [ ] Cycle detection with 3-color state
- [ ] Topological sort with Kahn's (in-degree) and DFS
- [ ] Bipartite check with coloring
- [ ] Connected components (DFS or Union-Find)
- [ ] Word ladder BFS
- [ ] Clone graph (BFS/DFS with visited map)

---

## BFS vs DFS Decision Tree

```
Shortest path in unweighted graph? → BFS
Cycle detection? → DFS with states
Topological sort? → Kahn's BFS or DFS
Connected components? → Either
All paths? → DFS
Level by level processing? → BFS
Deep exploration? → DFS
```

---

## Common Traps

**Trap:** BFS without marking visited before adding to queue.
- Fix: `visited.add(neighbor)` before `queue.append(neighbor)` to avoid duplicates.

**Trap:** DFS recursion depth exceeded.
- Fix: Use iterative DFS with explicit stack, or increase recursion limit.

**Trap:** Topological sort not checking cycle.
- Fix: Result length must equal number of nodes. Otherwise, cycle exists.

**Trap:** Bipartite check on disconnected graph.
- Fix: Loop through all nodes, start BFS/DFS if uncolored.

**Near Miss: Shortest Path in Weighted Graph**
- BFS only works for unweighted
- Weighted needs Dijkstra (Advanced Graphs)
