# 43 — Search with Ranking

**New concept:** relevance ranking.

Naive search returns results in some order (often the order they were added). Better search ranks them by how well they match. A document with the search term in its title is more relevant than one with it only in the body.

## Run it

```bash
npm install
node server.js
```

```bash
# Search for "JavaScript"
curl 'http://localhost:3000/search?q=JavaScript'
# Returns: doc 1 (high score, title match + body match) first
#          then doc 3 (title match + body match)
#          doc 2 and 4 don't match (score 0, filtered out)

# Search for "Python data"
curl 'http://localhost:3000/search?q=Python+data'
# Returns: doc 4 (matches "Python" and "data" in body, "data" in title)
#          then doc 2 (matches "Python" in body)
```

## How to think about it

When you search Google, you don't get random results. You get the most relevant first. How does Google decide? Lots of factors, but the basic idea: count matches, weight some places higher, then sort.

## How to build it (line by line)

```js
function tokenize(text) {
  return text.toLowerCase().match(/[a-z0-9]+/g) || [];
}
```

**Lines 13-15.** Break text into words.

**`text.toLowerCase()`** — case-insensitive.

**`text.match(/[a-z0-9]+/g)`** — regex: any sequence of letters/digits. Returns an array of words.

**`|| []`** — if no matches, return empty array (not null).

```js
function score(doc, queryTokens) {
  let score = 0;
  const docTokens = tokenize(doc.title + ' ' + doc.body);
  for (const term of queryTokens) {
    const count = docTokens.filter(t => t === term).length;
    score += count;
  }
  // Title match counts more
  const titleLower = doc.title.toLowerCase();
  for (const term of queryTokens) {
    if (titleLower.includes(term)) score += 5;
  }
  return score;
}
```

**Lines 18-30.** Score a document. Two parts:
1. Count occurrences in the body (each occurrence = 1 point)
2. Title match = 5 bonus points

**Why boost the title?** Because if a doc has the search term in the title, it's more likely to be what the user wants.

```js
const scored = docs
  .map(doc => ({ ...doc, score: score(doc, queryTokens) }))
  .filter(d => d.score > 0)
  .sort((a, b) => b.score - a.score);
```

**Lines 38-41.** Score everything, drop the zero-score ones, sort by score descending.

**`b.score - a.score`** — descending order (highest first).

## What we learned

1. Search ranking = score + sort
2. Title matches are worth more than body matches
3. We can build search from scratch (real engines like Elasticsearch do this plus more)
4. Tokenization (splitting text into words) is the first step

## What's next

In **44-rate-limiter** we limit how many requests a client can make.
