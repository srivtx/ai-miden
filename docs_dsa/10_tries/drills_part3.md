# Pattern 10: Tries - Drills Part 3
## Near Misses + Pattern Blends + Interview Simulation (15 Problems)

---

### 1. 139. Word Break
**Archetype:** 10.3 Replace/Prefix Matching
**Type:** Near Miss
**Statement:** Given a string and a dictionary, determine if the string can be segmented into dictionary words.
**Why it fits:** It looks like a prefix-matching problem where a trie could check if substrings are in the dictionary. However, the canonical solution uses DP because you need to check segmentations, not just prefixes.
**The Twist:** The trie can accelerate the inner loop of DP by quickly checking if s[i:j] is in the dictionary, but the overall structure remains DP, not pure trie traversal.
**Code Skeleton:**
```python
def word_break(s: str, wordDict: list[str]) -> bool:
    root = {}
    for word in wordDict:
        node = root
        for char in word:
            node = node.setdefault(char, {})
        node['#'] = True

    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True

    for i in range(n):
        if not dp[i]:
            continue
        node = root
        for j in range(i, n):
            if s[j] not in node:
                break
            node = node[s[j]]
            if '#' in node:
                dp[j + 1] = True
    return dp[n]
```

### 2. 140. Word Break II
**Archetype:** 10.3 Replace/Prefix Matching
**Type:** Near Miss
**Statement:** Return all possible sentence segmentations of a string using dictionary words.
**Why it fits:** Like Word Break, this appears to be about prefix matching in a dictionary. A trie helps validate words, but the combinatorial explosion of valid sentences requires backtracking or memoization.
**The Twist:** You must return all valid segmentations, not just a boolean. The trie accelerates word validation, but the core challenge is backtracking/DFS, not trie traversal.
**Code Skeleton:**
```python
def word_break_ii(s: str, wordDict: list[str]) -> list[str]:
    root = {}
    for word in wordDict:
        node = root
        for char in word:
            node = node.setdefault(char, {})
        node['#'] = True

    memo = {}

    def backtrack(start):
        if start in memo:
            return memo[start]
        if start == len(s):
            return [""]
        node = root
        res = []
        for end in range(start, len(s)):
            char = s[end]
            if char not in node:
                break
            node = node[char]
            if '#' in node:
                word = s[start:end+1]
                for suffix in backtrack(end + 1):
                    res.append(word + (" " + suffix if suffix else ""))
        memo[start] = res
        return res

    return backtrack(0)
```

### 3. 820. Short Encoding of Words
**Archetype:** 10.3 Replace/Prefix Matching
**Type:** Near Miss
**Statement:** Given a list of words, return the length of the shortest reference string that encodes them such that each word is a suffix of the reference string preceded by '#'.
**Why it fits:** It looks like prefix matching, but the problem is actually about suffixes. Words that are suffixes of other words can be embedded for free.
**The Twist:** You must match suffixes, not prefixes. The solution uses a reversed trie (or hash set of reversed words) to eliminate words that are suffixes of others.
**Code Skeleton:**
```python
def minimum_length_encoding(words: list[str]) -> int:
    root = {}
    leaves = []
    for word in set(words):
        node = root
        for char in reversed(word):
            node = node.setdefault(char, {})
        leaves.append((node, len(word) + 1))
    return sum(length for node, length in leaves if not node)
```

### 4. 1166. Design File System
**Archetype:** 10.1 Basic Trie Operations
**Type:** Near Miss
**Statement:** Design an in-memory file system that supports creating paths with values and retrieving values by path.
**Why it fits:** Paths are strings separated by '/', which resembles a trie structure. However, each path segment can be arbitrary strings, and the operation is closer to a hash map tree.
**The Twist:** The path segments are multi-character strings, not single characters. A standard character-by-character trie is possible but overkill; a nested hash map is the natural structure.
**Code Skeleton:**
```python
class FileSystem:
    def __init__(self):
        self.paths = {}

    def createPath(self, path: str, value: int) -> bool:
        parts = path.split('/')[1:]
        node = self.paths
        for part in parts[:-1]:
            if part not in node:
                return False
            node = node[part]
        if parts[-1] in node:
            return False
        node[parts[-1]] = {"#val": value}
        return True

    def get(self, path: str) -> int:
        parts = path.split('/')[1:]
        node = self.paths
        for part in parts:
            if part not in node:
                return -1
            node = node[part]
        return node.get("#val", -1)
```

### 5. 336. Palindrome Pairs
**Archetype:** 10.1 Basic Trie Operations
**Type:** Near Miss
**Statement:** Given a list of unique words, find all pairs of distinct indices (i, j) such that the concatenation of the two words is a palindrome.
**Why it fits:** It looks like prefix/suffix matching. A trie can store reversed words to find matching prefixes, but the palindrome constraint adds a layer of complexity beyond standard trie queries.
**The Twist:** For each word, you must check if any prefix is a palindrome (and the remaining suffix matches a reversed word in the trie), and vice versa. This requires palindrome precomputation, not just trie traversal.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.index = -1
        self.palindrome_indices = []

class Solution:
    def palindromePairs(self, words: list[str]) -> list[list[int]]:
        root = TrieNode()
        for i, word in enumerate(words):
            node = root
            reversed_word = word[::-1]
            for j, char in enumerate(reversed_word):
                if word[:len(word)-j] == word[:len(word)-j][::-1]:
                    node.palindrome_indices.append(i)
                node = node.children.setdefault(char, TrieNode())
            node.index = i

        ans = []
        for i, word in enumerate(words):
            node = root
            for j, char in enumerate(word):
                if node.index >= 0 and node.index != i and word[j:] == word[j:][::-1]:
                    ans.append([i, node.index])
                if char not in node.children:
                    break
                node = node.children[char]
            else:
                if node.index >= 0 and node.index != i:
                    ans.append([i, node.index])
                for j in node.palindrome_indices:
                    if i != j:
                        ans.append([i, j])
        return ans
```

### 6. 472. Concatenated Words
**Archetype:** 10.1 Basic Trie Operations + DP
**Type:** Pattern Blend
**Statement:** Given an array of words, find all concatenated words which can be formed by concatenating at least two shorter words in the array.
**Why it fits:** This blends trie prefix lookups with dynamic programming. The trie stores the dictionary, and DP checks if a word can be segmented into two or more valid words.
**The Twist:** The words must be formed by at least two shorter words from the original list. You must sort words by length and build the trie incrementally to ensure the "shorter" constraint.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Solution:
    def findAllConcatenatedWordsInADict(self, words: list[str]) -> list[str]:
        root = TrieNode()

        def can_form(word):
            if not word:
                return True
            node = root
            for i, char in enumerate(word):
                if char not in node.children:
                    return False
                node = node.children[char]
                if node.is_end and can_form(word[i+1:]):
                    return True
            return False

        ans = []
        for word in sorted(words, key=len):
            if can_form(word):
                ans.append(word)
            node = root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
            node.is_end = True
        return ans
```

### 7. 1065. Index Pairs of a String
**Archetype:** 10.1 Basic Trie Operations + String Matching
**Type:** Pattern Blend
**Statement:** Given a text string and words, return all index pairs [i, j] such that substring text[i:j+1] is in words.
**Why it fits:** This blends trie construction with substring scanning. Instead of checking each word against the text, you build a trie and walk it from every position in the text.
**The Twist:** You must report all matching substrings, including overlapping ones. The trie allows early termination when no prefix matches.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Solution:
    def indexPairs(self, text: str, words: list[str]) -> list[list[int]]:
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
            node.is_end = True

        ans = []
        for i in range(len(text)):
            node = root
            for j in range(i, len(text)):
                if text[j] not in node.children:
                    break
                node = node.children[text[j]]
                if node.is_end:
                    ans.append([i, j])
        return ans
```

### 8. 527. Word Abbreviation
**Archetype:** 10.1 Basic Trie Operations + Greedy
**Type:** Pattern Blend
**Statement:** Given an array of n distinct non-empty strings, create abbreviations using the shortest unique prefix of each word.
**Why it fits:** This blends trie traversal with greedy grouping. You build a trie and use prefix lengths to disambiguate words that share abbreviations.
**The Twist:** Words that share the same abbreviation pattern must be recursively resolved by extending their prefix until unique.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.count = 0

class Solution:
    def wordsAbbreviation(self, words: list[str]) -> list[str]:
        n = len(words[0])
        tries = {}
        for word in words:
            key = (word[0], word[-1], len(word))
            if key not in tries:
                tries[key] = TrieNode()
            node = tries[key]
            for char in word[1:-1]:
                node = node.children.setdefault(char, TrieNode())
                node.count += 1

        ans = []
        for word in words:
            key = (word[0], word[-1], len(word))
            node = tries[key]
            prefix_len = 1
            for char in word[1:-1]:
                if node.count == 1:
                    break
                node = node.children[char]
                prefix_len += 1
            abbr = word[:prefix_len] + str(len(word) - prefix_len - 1) + word[-1]
            ans.append(abbr if len(abbr) < len(word) else word)
        return ans
```

### 9. 745. Prefix and Suffix Search
**Archetype:** 10.1 Basic Trie Operations + Design
**Type:** Pattern Blend
**Statement:** Design a word filter that supports searching for words given a prefix and a suffix.
**Why it fits:** This blends trie structure with a clever encoding trick. Instead of building two tries, you insert every suffix+'{'+word into a single trie.
**The Twist:** The '{' character acts as a delimiter. By inserting all suffixes of each word, any prefix query on this augmented trie simultaneously matches a suffix and a prefix.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.weight = -1

class WordFilter:
    def __init__(self, words: list[str]):
        self.root = TrieNode()
        for weight, word in enumerate(words):
            for i in range(len(word)):
                key = word[i:] + '{' + word
                node = self.root
                for char in key:
                    node = node.children.setdefault(char, TrieNode())
                    node.weight = weight

    def f(self, pref: str, suff: str) -> int:
        node = self.root
        key = suff + '{' + pref
        for char in key:
            if char not in node.children:
                return -1
            node = node.children[char]
        return node.weight
```

### 10. 1233. Remove Sub-Folders from the Filesystem
**Archetype:** 10.3 Replace/Prefix Matching + Sorting
**Type:** Pattern Blend
**Statement:** Given a list of folders, remove all sub-folders and return the remaining folders.
**Why it fits:** This blends trie prefix matching with sorting. A folder is a sub-folder if its path is a prefix of another path in the list.
**The Twist:** Sorting the paths lexicographically guarantees that a parent folder always appears before its children. This lets you solve it with a single pass and a running prefix check.
**Code Skeleton:**
```python
def remove_subfolders(folder: list[str]) -> list[str]:
    folder.sort()
    ans = [folder[0]]
    for f in folder[1:]:
        last = ans[-1] + '/'
        if not f.startswith(last):
            ans.append(f)
    return ans
```

### 11. 642. Design Search Autocomplete System
**Archetype:** 10.1 Basic Trie Operations
**Type:** Interview Sim
**Statement:** Design a search autocomplete system with historical sentence frequencies.
**Why it fits:** This is a classic system design interview problem. It requires a trie with frequency counts at each node, plus the ability to sort suggestions by historical frequency.
**The Twist:** You must support '#' to terminate a sentence and update frequencies. The query is incremental (character by character), so you need to maintain a current node pointer and handle sentence termination.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.sentences = {}

class AutocompleteSystem:
    def __init__(self, sentences: list[str], times: list[int]):
        self.root = TrieNode()
        self.input_so_far = ""
        self.curr = self.root
        for sent, t in zip(sentences, times):
            self._add(sent, t)

    def _add(self, sentence, count):
        node = self.root
        for char in sentence:
            node = node.children.setdefault(char, TrieNode())
            node.sentences[sentence] = node.sentences.get(sentence, 0) + count

    def input(self, c: str) -> list[str]:
        if c == '#':
            self._add(self.input_so_far, 1)
            self.input_so_far = ""
            self.curr = self.root
            return []
        self.input_so_far += c
        if self.curr and c in self.curr.children:
            self.curr = self.curr.children[c]
            items = sorted(self.curr.sentences.items(), key=lambda x: (-x[1], x[0]))
            return [s for s, _ in items[:3]]
        else:
            self.curr = None
            return []
```

### 12. 1804. Implement Trie II (Prefix Tree)
**Archetype:** 10.1 Basic Trie Operations
**Type:** Interview Sim
**Statement:** Implement a trie supporting insert, countWordsEqualTo, countWordsStartingWith, and erase.
**Why it fits:** This is a direct follow-up to the classic Trie problem in an interview setting. It tests whether the candidate understands how to augment trie nodes with frequency counts.
**The Twist:** You must support deletion (erase) and exact count queries. This requires tracking `word_count` and `prefix_count` at every node, updating them on insert and erase.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word_count = 0
        self.prefix_count = 0

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
            node.prefix_count += 1
        node.word_count += 1

    def countWordsEqualTo(self, word: str) -> int:
        node = self.root
        for char in word:
            if char not in node.children:
                return 0
            node = node.children[char]
        return node.word_count

    def countWordsStartingWith(self, prefix: str) -> int:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return 0
            node = node.children[char]
        return node.prefix_count

    def erase(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.children[char]
            node.prefix_count -= 1
        node.word_count -= 1
```

### 13. 745. Prefix and Suffix Search
**Archetype:** 10.1 Basic Trie Operations
**Type:** Interview Sim
**Statement:** Design a word filter returning the highest-weight word matching a prefix and suffix.
**Why it fits:** A classic hard design problem. The interview tests whether you can find the elegant suffix#prefix trie trick or get stuck with two tries.
**The Twist:** The naive two-trie approach is too slow. The expected solution uses a single trie with concatenated suffix#word strings, which is non-obvious.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.weight = -1

class WordFilter:
    def __init__(self, words: list[str]):
        self.root = TrieNode()
        for weight, word in enumerate(words):
            for i in range(len(word)):
                key = word[i:] + '{' + word
                node = self.root
                for char in key:
                    node = node.children.setdefault(char, TrieNode())
                    node.weight = weight

    def f(self, pref: str, suff: str) -> int:
        node = self.root
        key = suff + '{' + pref
        for char in key:
            if char not in node.children:
                return -1
            node = node.children[char]
        return node.weight
```

### 14. 2707. Extra Characters in a String
**Archetype:** 10.1 Basic Trie Operations + DP
**Type:** Interview Sim
**Statement:** Return the minimum number of extra characters left over if you optimally segment the string into dictionary words.
**Why it fits:** This is a frequent interview variation of Word Break. The interviewer wants to see if you can optimize the DP with a trie to avoid O(N^2) substring checks.
**The Twist:** The DP state is simple, but the naive O(N^2) approach TLEs on long strings. The trie reduces the inner loop to average O(L) where L is max word length.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Solution:
    def minExtraChar(self, s: str, dictionary: list[str]) -> int:
        root = TrieNode()
        for word in dictionary:
            node = root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
            node.is_end = True

        n = len(s)
        dp = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            dp[i] = dp[i + 1] + 1
            node = root
            for j in range(i, n):
                if s[j] not in node.children:
                    break
                node = node.children[s[j]]
                if node.is_end:
                    dp[i] = min(dp[i], dp[j + 1])
        return dp[0]
```

### 15. 2416. Sum of Prefix Scores of Strings
**Archetype:** 10.1 Basic Trie Operations
**Type:** Interview Sim
**Statement:** For each string in words, find the sum of scores of every non-empty prefix, where the score of a prefix is its frequency across all words.
**Why it fits:** This tests whether you can augment a trie with frequency counts and then traverse it efficiently for all words. It is a good follow-up to Trie II.
**The Twist:** You need prefix frequencies for ALL words simultaneously. Building the trie once and then doing a second pass to accumulate scores is the expected solution.
**Code Skeleton:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.count = 0

class Solution:
    def sumPrefixScores(self, words: list[str]) -> list[int]:
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
                node.count += 1

        ans = []
        for word in words:
            score = 0
            node = root
            for char in word:
                node = node.children[char]
                score += node.count
            ans.append(score)
        return ans
```