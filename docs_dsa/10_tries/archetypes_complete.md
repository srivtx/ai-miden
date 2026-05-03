# Pattern 10: Tries — Complete Archetype Map

> **Pattern Recognition:** When you see "prefix", "autocomplete", "word search", "dictionary", "replace words", "longest common prefix", "XOR maximum pair" — think trie.
>
> **Fundamental Insight:** A trie is a tree where each edge represents a character. Paths from root to node spell prefixes. It turns string-prefix queries from O(n * m) into O(m) where m is the length of the query string.

---

## Archetype 10.1: Basic Trie Operations

### Recognition Signal (10 seconds)
Words: **"implement trie", "insert", "search", "startsWith", "prefix tree"**

The question is always: **"Build a data structure that supports inserting words and querying by exact match or prefix."**

### Core Structure
```python
class TrieNode:
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end = False  # Marks end of a complete word

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def startsWith(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True
```

### The Invariant
Every node along the insertion path represents a prefix of the inserted word. `is_end` guarantees that the path spells a complete word, not just a prefix of a longer word.

### Canonical Problem: Implement Trie (Prefix Tree) (LeetCode 208)
**Statement:** Implement a trie with insert, search, and startsWith.

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
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None

    def _find_node(self, word: str):
        node = self.root
        for ch in word:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

### Variation Family

**V1: Add and Search Word — Data Structure Design (LeetCode 211)**
- **Twist:** Search supports '.' as a wildcard matching any single character
- **Change:** DFS from the node matching the prefix before the wildcard. Try all children for '.'.

```python
class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        def dfs(node, i):
            if i == len(word):
                return node.is_end
            ch = word[i]
            if ch == '.':
                for child in node.children.values():
                    if dfs(child, i + 1):
                        return True
                return False
            else:
                if ch not in node.children:
                    return False
                return dfs(node.children[ch], i + 1)
        return dfs(self.root, 0)
```

**V2: Design Search Autocomplete System (LeetCode 642)**
- **Twist:** Return top 3 historical sentences matching the prefix typed so far
- **Change:** Trie node stores a list of sentence IDs/hot degrees. Sort and cache.

**V3: Concatenated Words (LeetCode 472)**
- **Twist:** Find all words that can be formed by concatenating other words in the list
- **Change:** Build trie with all words. For each word, DFS to see if it can be split into >= 2 words from the trie.

```python
def findAllConcatenatedWordsInADict(words):
    root = TrieNode()
    for w in words:
        if w:
            node = root
            for ch in w:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.is_end = True

    def dfs(word, start):
        if start == len(word):
            return True
        node = root
        for i in range(start, len(word)):
            ch = word[i]
            if ch not in node.children:
                return False
            node = node.children[ch]
            if node.is_end and dfs(word, i + 1):
                return True
        return False

    res = []
    for w in words:
        if w and dfs(w, 0):
            res.append(w)
    return res
```

**V4: Prefix and Suffix Search (LeetCode 745)**
- **Twist:** Search words by prefix AND suffix simultaneously
- **Change:** Store reversed suffixes in a trie, or insert every possible suffix of each word with the word attached (e.g., for "apple", insert "#apple", "e#apple", "le#apple", etc.).

**Near Miss: Group Anagrams (LeetCode 49)**
- **Looks like:** String dictionary / grouping
- **But:** Uses hash map of sorted strings. No prefix structure needed.
- **Lesson:** Trie solves prefix problems. Anagrams need canonical forms (sorted signatures or character counts).

---

## Archetype 10.2: Word Search in Grid (Trie + DFS)

### Recognition Signal (10 seconds)
Words: **"word search", "find words", "board", "grid", "boggle", "multiple words"**

The question is always: **"Given a grid of characters and a list of words, find all words that can be formed by adjacent cells (no reuse)."**

### Core Structure
```python
def find_words(board, words):
    # Build trie from words
    root = TrieNode()
    for word in words:
        node = root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True
        node.word = word  # Store full word at terminal node

    found = []
    for r in range(len(board)):
        for c in range(len(board[0])):
            dfs(board, r, c, root, found)
    return found

def dfs(board, r, c, node, found):
    ch = board[r][c]
    if ch not in node.children:
        return
    next_node = node.children[ch]
    if getattr(next_node, 'word', None):
        found.append(next_node.word)
        next_node.word = None  # Avoid duplicates

    board[r][c] = '#'  # Mark visited
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
            dfs(board, nr, nc, next_node, found)
    board[r][c] = ch  # Unmark (backtrack)

    # Optimization: prune trie leaf if empty
    if not next_node.children:
        del node.children[ch]
```

### The Invariant
The trie stores all target words. DFS walks the board, following trie edges. Pruning dead branches (removing empty nodes) prevents re-exploring impossible paths. Marking visited cells ensures no cell is reused within a single word path.

### Canonical Problem: Word Search II (LeetCode 212)
**Statement:** Given an m x n board and a list of words, find all words on the board.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None  # Store full word here when terminal

class Solution:
    def findWords(self, board, words):
        # Build trie
        root = TrieNode()
        for word in words:
            node = root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.word = word

        res = []
        rows, cols = len(board), len(board[0])

        def dfs(r, c, parent):
            ch = board[r][c]
            if ch not in parent.children:
                return
            node = parent.children[ch]
            if node.word:
                res.append(node.word)
                node.word = None  # De-duplicate

            board[r][c] = '#'  # Mark visited
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                    dfs(nr, nc, node)
            board[r][c] = ch  # Backtrack

            # Prune empty leaves to speed up subsequent searches
            if not node.children:
                del parent.children[ch]

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root)
        return res
```

### Variation Family

**V1: Word Search (LeetCode 79)**
- **Twist:** Search for a SINGLE word in the board
- **Change:** No trie needed. Simple DFS with backtracking. But the DFS template is identical.

```python
def exist(board, word):
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
            if dfs(r, c, 0):
                return True
    return False
```

**V2: Unique Paths III (LeetCode 980)**
- **Twist:** Walk over every non-obstacle square exactly once
- **Change:** DFS with visited tracking, count paths that visit all empty squares.
- **Key insight:** Backtracking template with global count and visit-all condition.

**V3: Number of Islands (LeetCode 200)**
- **Twist:** Count connected components of 1s
- **Change:** DFS/BFS flood fill. No word matching, just component labeling.
- **Lesson:** Grid DFS is the base pattern. Trie adds multi-word optimization.

**Near Miss: N-Queens (LeetCode 51)**
- **Looks like:** Backtracking on a grid/board
- **But:** Constraint propagation across rows, columns, diagonals. Not character paths.
- **Lesson:** Board backtracking != trie DFS. Different constraint domains.

---

## Archetype 10.3: Replace / Prefix Matching

### Recognition Signal (10 seconds)
Words: **"replace words", "replace", "successor", "root", "dictionary", "shortest prefix", "autocomplete"**

The question is always: **"Replace each word in a sentence with its shortest prefix found in a dictionary."** or **"Find all words that match a given prefix."**

### Core Structure
```python
def replace_words(dictionary, sentence):
    root = TrieNode()
    for word in dictionary:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def shortest_prefix(word):
        node = root
        for i, ch in enumerate(word):
            if ch not in node.children:
                return word
            node = node.children[ch]
            if node.is_end:
                return word[:i+1]
        return word

    return ' '.join(shortest_prefix(w) for w in sentence.split())
```

### The Invariant
When traversing a word character-by-character, the first trie node marked `is_end` represents the shortest prefix in the dictionary. If no such node exists, the original word is retained.

### Canonical Problem: Replace Words (LeetCode 648)
**Statement:** In a sentence, replace each word with its shortest root from the dictionary.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Solution:
    def replaceWords(self, dictionary, sentence):
        root = TrieNode()
        for word in dictionary:
            node = root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.is_end = True

        def replace(word):
            node = root
            for i, ch in enumerate(word):
                if ch not in node.children:
                    return word
                node = node.children[ch]
                if node.is_end:
                    return word[:i+1]
            return word

        return ' '.join(replace(w) for w in sentence.split())
```

### Variation Family

**V1: Search Suggestions System (LeetCode 1268)**
- **Twist:** After typing each character, return up to 3 lexicographically smallest suggestions
- **Change:** Build trie. At each node, keep a sorted list of up to 3 words (or DFS from node). For each prefix, walk trie and collect.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.suggestions = []  # Keep at most 3 sorted words

class Solution:
    def suggestedProducts(self, products, searchWord):
        root = TrieNode()
        for w in sorted(products):
            node = root
            for ch in w:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
                if len(node.suggestions) < 3:
                    node.suggestions.append(w)

        res = []
        node = root
        for ch in searchWord:
            if node and ch in node.children:
                node = node.children[ch]
                res.append(node.suggestions)
            else:
                node = None
                res.append([])
        return res
```

**V2: Longest Word in Dictionary (LeetCode 720)**
- **Twist:** Find longest word that can be built one character at a time by other words in the dictionary
- **Change:** Sort words by length. Insert into trie only if all prefixes exist. Track longest valid.

```python
def longestWord(words):
    words.sort()
    root = TrieNode()
    longest = ""
    for w in words:
        node = root
        valid = True
        for i, ch in enumerate(w):
            if ch not in node.children:
                if i != len(w) - 1:
                    valid = False
                    break
                node.children[ch] = TrieNode()
            node = node.children[ch]
        if valid and len(w) > len(longest):
            longest = w
    return longest
```

**V3: Map Sum Pairs (LeetCode 677)**
- **Twist:** Insert key-value pairs. Query sum of all values for keys with a given prefix.
- **Change:** Trie node stores cumulative sum for the prefix. Update sums on insertion.

```python
class MapSum:
    def __init__(self):
        self.root = TrieNode()
        self.keys = {}

    def insert(self, key, val):
        delta = val - self.keys.get(key, 0)
        self.keys[key] = val
        node = self.root
        for ch in key:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            node.val = node.val + delta if hasattr(node, 'val') else delta

    def sum(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return 0
            node = node.children[ch]
        return getattr(node, 'val', 0)
```

**Near Miss: Implement Magic Dictionary (LeetCode 676)**
- **Looks like:** Dictionary search with slight variation
- **But:** Search allows exactly one character difference. Brute force or hash map of wildcard patterns is easier than trie.
- **Lesson:** Trie excels at exact prefix match. Fuzzy match often needs different data structures.

---

## Archetype 10.4: XOR / Bit Trie

### Recognition Signal (10 seconds)
Words: **"maximum XOR", "maximum xor pair", "bit", "binary trie", "array", "two numbers"**

The question is always: **"Find the maximum XOR you can obtain from some pair / subset, where the optimal choice depends on matching opposite bits at the highest positions."**

### Core Structure
```python
class TrieNode:
    def __init__(self):
        self.children = {}  # 0 or 1 -> TrieNode

def max_xor(nums):
    root = TrieNode()
    max_result = 0

    for num in nums:
        node = root
        # Insert num bit by bit from MSB to LSB
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            if bit not in node.children:
                node.children[bit] = TrieNode()
            node = node.children[bit]

        # Query for best match (opposite bits preferred)
        node = root
        curr_xor = 0
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            toggled = 1 - bit
            if toggled in node.children:
                curr_xor |= (1 << i)
                node = node.children[toggled]
            else:
                node = node.children[bit]
        max_result = max(max_result, curr_xor)

    return max_result
```

### The Invariant
At each bit level, choosing the opposite bit (if available) maximizes the XOR contribution at that bit position (2^i). Because we process from MSB to LSB, greedy local choices yield the global maximum (higher bits dominate lower bits).

### Canonical Problem: Maximum XOR of Two Numbers in an Array (LeetCode 421)
**Statement:** Given an integer array nums, return the maximum result of nums[i] XOR nums[j].

```python
class TrieNode:
    def __init__(self):
        self.children = {}

class Solution:
    def findMaximumXOR(self, nums):
        root = TrieNode()
        max_xor = 0

        for num in nums:
            # Insert
            node = root
            for i in range(31, -1, -1):
                bit = (num >> i) & 1
                if bit not in node.children:
                    node.children[bit] = TrieNode()
                node = node.children[bit]

            # Query
            node = root
            curr = 0
            for i in range(31, -1, -1):
                bit = (num >> i) & 1
                want = 1 - bit
                if want in node.children:
                    curr |= (1 << i)
                    node = node.children[want]
                else:
                    node = node.children[bit]
            max_xor = max(max_xor, curr)

        return max_xor
```

### Variation Family

**V1: Maximum XOR With an Element From Array (LeetCode 1707)**
- **Twist:** Queries ask for max XOR of x with any array element <= limit (mi)
- **Change:** Sort nums and queries by threshold. Insert eligible nums into trie as you go. Answer each query against the current trie.

```python
def maximizeXor(nums, queries):
    nums.sort()
    # Sort queries by limit, keep original index
    sorted_queries = sorted([(m, x, i) for i, (x, m) in enumerate(queries)])
    res = [-1] * len(queries)
    root = TrieNode()
    idx = 0

    for m, x, i in sorted_queries:
        while idx < len(nums) and nums[idx] <= m:
            # Insert nums[idx]
            node = root
            for b in range(31, -1, -1):
                bit = (nums[idx] >> b) & 1
                if bit not in node.children:
                    node.children[bit] = TrieNode()
                node = node.children[bit]
            idx += 1
        if idx == 0:
            continue  # No eligible numbers
        # Query x
        node = root
        curr = 0
        for b in range(31, -1, -1):
            bit = (x >> b) & 1
            want = 1 - bit
            if want in node.children:
                curr |= (1 << b)
                node = node.children[want]
            else:
                node = node.children[bit]
        res[i] = curr
    return res
```

**V2: Find the Maximum XOR of Two Elements in an Array (same as canonical, but using hash set approach for contrast)**
- **Key insight:** Trie gives O(n * B). A bitmask + prefix set approach also works in O(n * B) and can be simpler in some languages.

**V3: Count Pairs With XOR in a Range (LeetCode 1803)**
- **Twist:** Count pairs with XOR in [low, high]
- **Change:** Use trie to count how many previous numbers have XOR with current in range. Bit-by-bit decision with branch counting.

**V4: Maximum Genetic Difference Query (LeetCode 1938)**
- **Twist:** Queries on a tree: max XOR of node value with value in its subtree
- **Change:** Euler tour + persistent trie / offline DFS with insert/remove on trie.
- **Pattern blend:** Tree traversal + bit trie.

**Near Miss: Single Number III (LeetCode 260)**
- **Looks like:** XOR bit manipulation
- **But:** Uses bitwise XOR properties (a ^ b ^ c ^ c = a ^ b) and bit masking. No trie needed.
- **Lesson:** Bit tries solve "maximize XOR with arbitrary pair" problems. Pure XOR cancellations use linear algebra / hashing.

---

## Pattern 10 Mastery Checklist

Before moving to Pattern 11, confirm you can:

- [ ] Implement a trie with insert, search, startsWith from scratch
- [ ] Use trie to optimize grid word search (prune dead branches)
- [ ] Replace words by finding shortest prefix in a trie
- [ ] Build and query a bit trie for maximum XOR
- [ ] Distinguish when a trie helps vs when a hash set suffices
- [ ] Know how to handle wildcard '.' in trie search (DFS branch)

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Forgetting to set `is_end` on insert | Words that are prefixes of other words are lost | Always mark terminal nodes |
| Not pruning trie leaves in Word Search II | Re-exploring impossible paths repeatedly | Delete empty children after backtracking |
| Searching before any insert in XOR trie | Querying against empty trie crashes | Initialize or handle empty tree |
| Using recursion without depth limit in trie DFS | Stack overflow on very long words | Iterative traversal or ensure word length is bounded |
| Confusing bit order in XOR trie | Inserting LSB first gives wrong greedy answer | Always insert MSB first (31 down to 0) |

---

## Pattern Blends (What Comes Next)

Trie does not live in isolation. It blends with:

- **DFS / Backtracking:** Word search on a board (Archetype 10.2)
- **Greedy / Bit manipulation:** Maximum XOR queries (Archetype 10.4)
- **Sorting:** Autocomplete suggestions to keep lexicographic order (Archetype 10.3)
- **Dynamic programming:** Word break uses trie to test prefixes efficiently

---

*Next: Pattern 11 — Graphs*
