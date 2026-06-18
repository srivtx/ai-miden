# The Build

> *"An inverted index is a map from words to rows. Build it once. Search it forever."*

We are going to add FTS5 full-text search to the `posts` table.

## The Migration

```sql
-- Migration 3: Add FTS5 virtual table
CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
  title, body, content='posts', content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS posts_ai AFTER INSERT ON posts BEGIN
  INSERT INTO posts_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;

CREATE TRIGGER IF NOT EXISTS posts_ad AFTER DELETE ON posts BEGIN
  INSERT INTO posts_fts(posts_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
END;

CREATE TRIGGER IF NOT EXISTS posts_au AFTER UPDATE ON posts BEGIN
  INSERT INTO posts_fts(posts_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
  INSERT INTO posts_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;
```

This migration (added to the `MIGRATIONS` array) creates the FTS table and the triggers. Existing posts are not indexed (we'd need a one-time backfill; for now, we accept that).

For an existing database, you'd run a backfill:

```sql
INSERT INTO posts_fts(rowid, title, body) SELECT id, title, body FROM posts;
```

## The Search Handler

```js
app.get('/posts', asyncHandler(async (req, res) => {
  const { limit, offset } = paginate(req);
  const q = req.query.q;

  let dataQuery;
  let countQuery;

  if (q) {
    dataQuery = db('posts_fts')
      .join('posts', 'posts_fts.rowid', 'posts.id')
      .join('users', 'posts.user_id', 'users.id')
      .select('posts.*', 'users.username as author', 'posts_fts.rank')
      .where('posts_fts', 'MATCH', q)
      .orderBy('posts_fts.rank')
      .limit(limit)
      .offset(offset);
    countQuery = db('posts_fts').where('posts_fts', 'MATCH', q).count('* as count').first();
  } else {
    dataQuery = db('posts')
      .join('users', 'posts.user_id', 'users.id')
      .select('posts.*', 'users.username as author')
      .orderBy('posts.created_at', 'desc')
      .limit(limit)
      .offset(offset);
    countQuery = db('posts').count('id as count').first();
  }

  const [posts, countResult] = await Promise.all([dataQuery, countQuery]);
  const count = countResult.count;
  res.json({ data: posts, meta: meta(count, limit, offset) });
}));
```

### The structure

- `req.query.q` is the search term (if provided)
- If `q` is provided, we use the FTS table
- If not, we use the regular `posts` table (the old behavior)
- The data query and count query run in parallel

### FTS query

```js
db('posts_fts')
  .join('posts', 'posts_fts.rowid', 'posts.id')
  .join('users', 'posts.user_id', 'users.id')
  .select('posts.*', 'users.username as author', 'posts_fts.rank')
  .where('posts_fts', 'MATCH', q)
  .orderBy('posts_fts.rank')
```

- `db('posts_fts')` — query the FTS table
- `.join('posts', 'posts_fts.rowid', 'posts.id')` — join to `posts` to get the full row
- `.join('users', 'posts.user_id', 'users.id')` — join to `users` for the author
- `.where('posts_fts', 'MATCH', q)` — the FTS5 MATCH clause
- `.orderBy('posts_fts.rank')` — sort by relevance (lower rank = more relevant)

### FTS count

```js
db('posts_fts').where('posts_fts', 'MATCH', q).count('* as count').first();
```

Counts the matches in the FTS table. Returns `[{ count: 5 }]`. We destructure `count` in the parallel `Promise.all`.

## Run It

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

curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"JavaScript Tips","body":"Some helpful JavaScript tricks."}'

# Search for "hello"
curl 'http://localhost:3000/posts?q=hello'
# {"data":[{"id":1,"title":"Hello World","author":"alice","rank":-1.234,...}],"meta":{...}}

# Search for "world" (matches two posts)
curl 'http://localhost:3000/posts?q=world'
# Both Hello and Goodbye posts, ordered by rank

# Search for "javascript"
curl 'http://localhost:3000/posts?q=javascript'
# The JavaScript Tips post

# No query (returns all, ordered by created_at)
curl 'http://localhost:3000/posts'
# All posts, ordered by created_at DESC
```

Search is fast. Results are ranked. The pagination still works.

---

## Experiments

### Experiment 1: Phrase search

```bash
curl 'http://localhost:3000/posts?q="hello%20world"'
# Exact phrase "hello world"
```

The URL-encoded space is `%20`. FTS5 matches the exact phrase.

### Experiment 2: Boolean search

```bash
curl 'http://localhost:3000/posts?q=hello%20OR%20goodbye'
# Either "hello" or "goodbye"
```

`%20` is a space. FTS5 supports `OR`, `AND`, `NOT`.

### Experiment 3: Prefix search

```bash
curl 'http://localhost:3000/posts?q=java*'
# Matches "javascript", "java", etc.
```

The `*` is a prefix wildcard.

### Experiment 4: Rank inspection

```bash
curl 'http://localhost:3000/posts?q=world' | jq '.data[].rank'
# -1.234, -1.567
```

The `rank` field is the BM25 score (negative). Lower = more relevant.

### Experiment 5: Search with no results

```bash
curl 'http://localhost:3000/posts?q=nonexistent'
# {"data":[],"meta":{"total":0,...}}
```

Empty data, but `meta` is correct.

### Experiment 6: Backfill existing posts

```bash
sqlite3 app.db "INSERT INTO posts_fts(rowid, title, body) SELECT id, title, body FROM posts;"
```

If you have existing posts that aren't in the FTS table, run this to backfill.

---

## Summary

You now have full-text search. The `GET /posts?q=` endpoint searches the FTS5 index. Results are ranked by BM25. The query is fast (O(log n)) regardless of the table size.

This is the foundation of *every* searchable API. From here, every project that needs text search uses FTS5 (or a similar engine). The patterns (virtual table, triggers, MATCH, BM25) are universal.

In project 20, we will add file upload. The client can attach images to posts. We will use multipart/form-data and stream the file to disk (or S3).

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
