# Pattern 10: Tries - Drills Part 2
## Warm-Ups + Core Drills (15 Problems)

---

### 1. 208. Implement Trie (Prefix Tree)
**Archetype:** 10.1 Basic Trie Operations
**Type:** Warm-Up
**Statement:** Implement a trie with insert, search, and startsWith methods.
**Why it fits:** This is the canonical trie implementation. Every other trie problem is a variation of these three basic operations.
**The Twist:** None - this is the baseline. Master this before attempting any other trie problem.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
```

### 2. 14. Longest Common Prefix
**Archetype:** 10.3 Replace/Prefix Matching
**Type:** Warm-Up
**Statement:** Find the longest common prefix string among an array of strings.
**Why it fits:** Tries naturally store prefixes. By inserting all words and finding the deepest node with a single child path, you extract the longest common prefix.
**The Twist:** Can be solved with simple scanning, but the trie approach is O(S) where S is the sum of all characters, and scales better with many queries.
**Code Skeleton:**
```python
def longest_common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""

    root = {}
    for word in strs:
        node = root
        for char in word:
            node = node.setdefault(char, {})
        node['#'] = True

    prefix = ""
    node = root
    while len(node) == 1 and '#' not in node:
        char = next(iter(node))
        prefix += char
        node = node[char]
    return prefix
```

### 3. 648. Replace Words
**Archetype:** 10.3 Replace/Prefix Matching
**Type:** Warm-Up
**Statement:** Replace every successor in a sentence with its shortest root form from a dictionary.
**Why it fits:** The core operation is finding the shortest prefix (root) that exists in the trie for each word. This is exactly what prefix matching excels at.
**The Twist:** You must return the shortest matching prefix, not the longest. Stop at the first `is_end` encountered during traversal.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

def replace_words(dictionary: list[str], sentence: str) -> str:
    root = TrieNode()
    for word in dictionary:
        node = root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_end = True

    def find_root(word):
        node = root
        for i, char in enumerate(word):
            if char not in node.children:
                break
            node = node.children[char]
            if node.is_end:
                return word[:i+1]
        return word

    return " ".join(find_root(word) for word in sentence.split())
```

### 4. 720. Longest Word in Dictionary
**Archetype:** 10.1 Basic Trie Operations
**Type:** Warm-Up
**Statement:** Return the longest word in the dictionary that can be built one character at a time by other words.
**Why it fits:** A word is valid only if every prefix is also in the dictionary. A trie lets you verify this by checking `is_end` at every prefix node.
**The Twist:** You need the longest word, and ties broken by lexicographically smallest. BFS/DFS over the trie with lexicographic ordering handles this cleanly.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = ""

def longest_word(words: list[str]) -> str:
    root = TrieNode()
    for word in sorted(words):
        node = root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_end = True
        node.word = word

    from collections import deque
    queue = deque([root])
    ans = ""
    while queue:
        node = queue.popleft()
        for char in sorted(node.children.keys(), reverse=True):
            child = node.children[char]
            if child.is_end:
                queue.append(child)
                ans = child.word
    return ans
```

### 5. 1268. Search Suggestions System
**Archetype:** 10.1 Basic Trie Operations
**Type:** Warm-Up
**Statement:** Return the top 3 lexicographically minimum products after each character of a search word is typed.
**Why it fits:** This is a standard prefix query. After typing each prefix, you need all words in the dictionary that share that prefix, limited to 3.
**The Twist:** You need to return suggestions after every character, not just the final prefix. Precomputing suggestions at each trie node avoids repeated DFS.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.suggestions = []

class Solution:
    def suggestedProducts(self, products: list[str], searchWord: str) -> list[list[str]]:
        root = TrieNode()
        for word in sorted(products):
            node = root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
                if len(node.suggestions) < 3:
                    node.suggestions.append(word)

        ans = []
        node = root
        for char in searchWord:
            if node and char in node.children:
                node = node.children[char]
                ans.append(node.suggestions)
            else:
                node = None
                ans.append([])
        return ans
```

### 6. 211. Design Add and Search Words Data Structure
**Archetype:** 10.1 Basic Trie Operations
**Type:** Core Drill
**Statement:** Design a data structure that supports adding words and searching with literal characters or '.' wildcards.
**Why it fits:** Builds directly on the basic trie. The wildcard forces you to explore all branches at a given level, blending trie traversal with backtracking.
**The Twist:** The '.' character requires DFS at that node level instead of a single deterministic path. This changes search from O(L) to O(26^L) worst case.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_end = True

    def search(self, word: str) -> bool:
        def dfs(node, i):
            if i == len(word):
                return node.is_end
            char = word[i]
            if char == '.':
                for child in node.children.values():
                    if dfs(child, i + 1):
                        return True
                return False
            if char not in node.children:
                return False
            return dfs(node.children[char], i + 1)
        return dfs(self.root, 0)
```

### 7. 677. Map Sum Pairs
**Archetype:** 10.1 Basic Trie Operations
**Type:** Core Drill
**Statement:** Implement a MapSum class that supports inserting key-val pairs and querying the sum of all values for keys with a given prefix.
**Why it fits:** Each trie node must store the cumulative sum of all words passing through it. This requires updating sums along the insertion path.
**The Twist:** If a key is inserted again, it overrides the previous value. You must handle this by tracking previous values in a hash map.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.value = 0

class MapSum:
    def __init__(self):
        self.root = TrieNode()
        self.key_map = {}

    def insert(self, key: str, val: int) -> None:
        delta = val - self.key_map.get(key, 0)
        self.key_map[key] = val
        node = self.root
        for char in key:
            node = node.children.setdefault(char, TrieNode())
            node.value += delta

    def sum(self, prefix: str) -> int:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return 0
            node = node.children[char]
        return node.value
```

### 8. 1032. Stream of Characters
**Archetype:** 10.1 Basic Trie Operations
**Type:** Core Drill
**Statement:** Design a class that receives a stream of characters and reports if any suffix forms a word in the dictionary.
**Why it fits:** Instead of querying prefixes, you query suffixes. This is solved by building the trie with reversed words and traversing backwards through the stream.
**The Twist:** The query arrives character-by-character in a stream. You cannot see the future, so you maintain a rolling pointer into the trie walking backwards through history.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class StreamChecker:
    def __init__(self, words: list[str]):
        self.root = TrieNode()
        self.stream = []
        for word in words:
            node = self.root
            for char in reversed(word):
                node = node.children.setdefault(char, TrieNode())
            node.is_end = True

    def query(self, letter: str) -> bool:
        self.stream.append(letter)
        node = self.root
        for i in range(len(self.stream) - 1, -1, -1):
            char = self.stream[i]
            if char not in node.children:
                return False
            node = node.children[char]
            if node.is_end:
                return True
        return False
```

### 9. 676. Implement Magic Dictionary
**Archetype:** 10.1 Basic Trie Operations
**Type:** Core Drill
**Statement:** Build a dictionary and answer queries asking if there is any word exactly one character different from the search word.
**Why it fits:** The trie stores the dictionary. For each query, you must explore paths where exactly one character deviates from the search word.
**The Twist:** You need exactly one mismatch, not zero and not more. This requires tracking a "used_change" boolean through the DFS traversal.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class MagicDictionary:
    def __init__(self):
        self.root = TrieNode()

    def buildDict(self, dictionary: list[str]) -> None:
        for word in dictionary:
            node = self.root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
            node.is_end = True

    def search(self, searchWord: str) -> bool:
        def dfs(node, i, changed):
            if i == len(searchWord):
                return changed and node.is_end
            char = searchWord[i]
            if char in node.children and dfs(node.children[char], i + 1, changed):
                return True
            if not changed:
                for c, child in node.children.items():
                    if c != char and dfs(child, i + 1, True):
                        return True
            return False
        return dfs(self.root, 0, False)
```

### 10. 79. Word Search
**Archetype:** 10.2 Word Search in Grid
**Type:** Core Drill
**Statement:** Given an m x n grid of characters and a word, return true if the word exists in the grid.
**Why it fits:** This is the foundational grid search problem. Understanding DFS on a grid is essential before optimizing with a trie for multiple words.
**The Twist:** Only a single word is queried. DFS with backtracking is sufficient; a trie is unnecessary overhead here. This builds intuition for why Word Search II needs a trie.
**Code Skeleton:**
```python
def exist(board: list[list[str]], word: str) -> bool:
    rows, cols = len(board), len(board[0])

    def dfs(r, c, i):
        if i == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[i]:
            return False
        temp = board[r][c]
        board[r][c] = '#'
        found = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1) or
                 dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
        board[r][c] = temp
        return found

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == word[0] and dfs(r, c, 0):
                return True
    return False
```

### 11. 212. Word Search II
**Archetype:** 10.2 Word Search in Grid
**Type:** Core Drill
**Statement:** Given an m x n grid and a list of words, find all words in the grid.
**Why it fits:** This is the canonical trie + DFS problem. Building a trie from the word list lets you terminate DFS early when no words share the current prefix.
**The Twist:** Pruning matched words from the trie is critical to avoid duplicate work and TLE. Without pruning, you re-explore the same paths for overlapping prefixes.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None

class Solution:
    def findWords(self, board: list[list[str]], words: list[str]) -> list[str]:
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
            node.word = word

        rows, cols = len(board), len(board[0])
        ans = []

        def dfs(r, c, node):
            char = board[r][c]
            if char not in node.children:
                return
            child = node.children[char]
            if child.word:
                ans.append(child.word)
                child.word = None
            board[r][c] = '#'
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                    dfs(nr, nc, child)
            board[r][c] = char
            if not child.children:
                del node.children[char]

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root)
        return ans
```

### 12. 425. Word Squares
**Archetype:** 10.2 Word Search in Grid
**Type:** Core Drill
**Statement:** Given a set of words, find all word squares you can build from them.
**Why it fits:** A word square requires that the k-th prefix of every row matches the k-th prefix of the corresponding column. A trie accelerates prefix lookups during backtracking.
**The Twist:** You are not searching a fixed grid; you are constructing the square. The constraint creates a self-referential prefix relationship.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word_list = []

class Solution:
    def wordSquares(self, words: list[str]) -> list[list[str]]:
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
                node.word_list.append(word)

        def get_words(prefix):
            node = root
            for char in prefix:
                if char not in node.children:
                    return []
                node = node.children[char]
            return node.word_list

        n = len(words[0])
        ans = []

        def backtrack(step, square):
            if step == n:
                ans.append(square[:])
                return
            prefix = "".join(square[i][step] for i in range(step))
            for candidate in get_words(prefix):
                square.append(candidate)
                backtrack(step + 1, square)
                square.pop()

        for word in words:
            backtrack(1, [word])
        return ans
```

### 13. 421. Maximum XOR of Two Numbers in an Array
**Archetype:** 10.4 XOR/Bit Trie
**Type:** Core Drill
**Statement:** Given an integer array, return the maximum result of nums[i] XOR nums[j].
**Why it fits:** This introduces the bit trie. Each number is treated as a 32-bit string, and you greedily match the opposite bit at each level to maximize XOR.
**The Twist:** The greedy choice (always try opposite bit) is guaranteed to be optimal because bits are processed from most significant to least significant.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}

class Solution:
    def findMaximumXOR(self, nums: list[int]) -> int:
        root = TrieNode()
        max_xor = 0
        for num in nums:
            node = root
            xor_node = root
            current_xor = 0
            for i in range(31, -1, -1):
                bit = (num >> i) & 1
                if bit not in node.children:
                    node.children[bit] = TrieNode()
                node = node.children[bit]
                toggled = 1 - bit
                if toggled in xor_node.children:
                    current_xor |= (1 << i)
                    xor_node = xor_node.children[toggled]
                else:
                    xor_node = xor_node.children[bit]
            max_xor = max(max_xor, current_xor)
        return max_xor
```

### 14. 1707. Maximum XOR With an Element From Array
**Archetype:** 10.4 XOR/Bit Trie
**Type:** Core Drill
**Statement:** For each query [xi, mi], find the maximum XOR of xi with any element in nums that does not exceed mi.
**Why it fits:** This extends the bit trie with offline queries. By sorting both nums and queries by their limit, you ensure the trie only contains valid candidates.
**The Twist:** The constraint `element <= mi` means you cannot simply insert all numbers beforehand. You must process queries in sorted order and insert numbers incrementally.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}

class Solution:
    def maximizeXor(self, nums: list[int], queries: list[list[int]]) -> list[int]:
        nums.sort()
        sorted_queries = sorted(enumerate(queries), key=lambda x: x[1][1])
        root = TrieNode()
        ans = [-1] * len(queries)
        num_idx = 0

        for original_idx, (x, m) in sorted_queries:
            while num_idx < len(nums) and nums[num_idx] <= m:
                num = nums[num_idx]
                node = root
                for i in range(31, -1, -1):
                    bit = (num >> i) & 1
                    node = node.children.setdefault(bit, TrieNode())
                num_idx += 1
            if num_idx == 0:
                continue
            node = root
            current_xor = 0
            for i in range(31, -1, -1):
                bit = (x >> i) & 1
                toggled = 1 - bit
                if toggled in node.children:
                    current_xor |= (1 << i)
                    node = node.children[toggled]
                else:
                    node = node.children[bit]
            ans[original_idx] = current_xor
        return ans
```

### 15. 1938. Maximum Genetic Difference Query
**Archetype:** 10.4 XOR/Bit Trie
**Type:** Core Drill
**Statement:** Given a rooted tree and queries [node, val], find the maximum XOR of val with any node on the path from root to the given node.
**Why it fits:** You maintain a bit trie representing the current root-to-node path during a DFS traversal. Each query at a node is answered against the live trie.
**The Twist:** The trie must support insert and delete because you backtrack up the tree. A simple insert-only trie will include nodes from sibling subtrees.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.count = 0

class Solution:
    def maxGeneticDifference(self, parents: list[int], queries: list[list[int]]) -> list[int]:
        n = len(parents)
        tree = [[] for _ in range(n)]
        root = -1
        for child, p in enumerate(parents):
            if p == -1:
                root = child
            else:
                tree[p].append(child)

        query_map = [[] for _ in range(n)]
        for i, (node, val) in enumerate(queries):
            query_map[node].append((i, val))

        ans = [0] * len(queries)
        trie_root = TrieNode()

        def add(num, delta):
            node = trie_root
            for i in range(20, -1, -1):
                bit = (num >> i) & 1
                node = node.children.setdefault(bit, TrieNode())
                node.count += delta

        def query_max(xor_val):
            node = trie_root
            res = 0
            for i in range(20, -1, -1):
                bit = (xor_val >> i) & 1
                toggled = 1 - bit
                if toggled in node.children and node.children[toggled].count > 0:
                    res |= (1 << i)
                    node = node.children[toggled]
                else:
                    node = node.children[bit]
            return res

        def dfs(node):
            add(node, 1)
            for idx, val in query_map[node]:
                ans[idx] = query_max(val)
            for child in tree[node]:
                dfs(child)
            add(node, -1)

        dfs(root)
        return ans
```