# Project 19: The Searcher

> *"`LIKE '%foo%'` is not search. It's a cry for help."*

In project 18, we paginate lists. But the client can only filter by *exact* fields (e.g., `?user_id=42`). What if they want to search by *text*? "Find all posts with 'hello' in the title or body"?

A naive approach is `LIKE '%hello%'`. This works for small tables. It is **O(n)** — the database scans every row, comparing the text. For 1M rows, this takes seconds. The user waits. The database is on fire.

**Full-text search (FTS)** is the proper solution. SQLite has built-in FTS5. We can create a *virtual table* that indexes the text columns. The database builds an *inverted index* — a mapping from words to rows. Searching is then **O(log n)** — the database looks up the word in the index and returns the matching rows.

FTS5 also supports:
- **Tokenization** — splitting text into words (handling punctuation, case, etc.)
- **Stemming** — "running" matches "ran" (Porter stemmer)
- **Ranking** — BM25 algorithm, which scores results by relevance
- **Highlighting** — `**hello**` to mark matches

We add FTS5 to our `posts` table. The `GET /posts` endpoint accepts a `?q=hello` query parameter. The server searches the FTS index and returns the ranked results.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is LIKE slow? What is full-text search?
2. [The Thought](./THOUGHT.md) — How does FTS5 work? What is BM25? What is stemming?
3. [The Build](./BUILD.md) — Line-by-line construction of the search
4. [The Decisions](./DECISIONS.md) — Why FTS5? Why not Elasticsearch? Why not Meilisearch?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

FTS5 is SQLite's full-text search engine. We create a virtual `posts_fts` table that indexes the `title` and `body` of posts. On insert, update, or delete, we keep the FTS table in sync (via triggers or application logic). The `GET /posts?q=hello` query uses `MATCH` against the FTS table, which returns ranked results using BM25. The result is fast, relevant, and predictable.

---

## The Code

```sql
-- Migration
CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
  title, body, content='posts', content_rowid='id'
);
```

```js
// In the list handler
app.get('/posts', asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const q = req.query.q;

  let query;
  let countQuery;

  if (q) {
    query = db('posts_fts')
      .join('posts', 'posts_fts.rowid', 'posts.id')
      .join('users', 'posts.user_id', 'users.id')
      .select('posts.*', 'users.username as author', 'posts_fts.rank')
      .where('posts_fts', 'MATCH', q)
      .orderBy('posts_fts.rank')
      .limit(limit)
      .offset(offset);
    countQuery = db('posts_fts').where('posts_fts', 'MATCH', q).count('* as count');
  } else {
    query = db('posts')
      .join('users', 'posts.user_id', 'users.id')
      .select('posts.*', 'users.username as author')
      .orderBy('posts.created_at', 'desc')
      .limit(limit)
      .offset(offset);
    countQuery = db('posts').count('id as count');
  }

  const [posts, [{ count }]] = await Promise.all([query, countQuery]);
  res.json({ data: posts, meta: meta(count, limit, offset) });
}));
```

Test it:

```bash
# Create some posts
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello World","body":"This is a post about greeting."}'

curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Goodbye World","body":"This is a post about leaving."}'

# Search
curl 'http://localhost:3000/posts?q=hello'
# {"data":[{"title":"Hello World",...,"rank":-...}],"meta":{...}}

curl 'http://localhost:3000/posts?q=world'
# Both posts, ranked by relevance

curl 'http://localhost:3000/posts?q=greeting'
# The "Hello" post (matched "greeting" in body)
```

The pain of "LIKE is slow and dumb" is solved. FTS5 is fast, ranked, and relevant.

---

## What You Will Have Learned

- What full-text search is (inverted index, tokenization, ranking)
- How FTS5 works in SQLite (virtual tables, MATCH, BM25)
- How to keep an FTS table in sync with the main table
- The `rank` column from FTS5 (BM25 score; lower is more relevant)
- Why `LIKE '%foo%'` doesn't use an index
- The difference between search and filter

These are the foundations of *search*. From here, every project that needs text search uses FTS5 (or a similar engine).
