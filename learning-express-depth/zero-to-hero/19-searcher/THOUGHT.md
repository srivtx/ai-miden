# The Thought

> *"An inverted index is a map from words to rows. Build it once. Search it forever."*

## What an Inverted Index Is

A regular index maps *row IDs* to *column values*. `INDEX (user_id)` lets you find rows by user_id quickly.

An *inverted index* is the opposite: it maps *column values* (words) to *row IDs*. The FTS index says:

```
"hello" → rows 1, 5, 12
"world" → rows 1, 2, 5
"goodbye" → row 2
```

When you search for "hello," the database looks up "hello" in the inverted index and gets the row IDs. No table scan. O(log n) lookup.

## How FTS5 Works in SQLite

FTS5 is a *virtual table* module. You create a virtual table that looks like a regular table but is backed by an inverted index:

```sql
CREATE VIRTUAL TABLE posts_fts USING fts5(
  title, body, content='posts', content_rowid='id'
);
```

- `posts_fts` — the name of the FTS table
- `fts5` — the module
- `title, body` — the columns to index
- `content='posts'` — the source table (the "content table")
- `content_rowid='id'` — the row ID column in the source table

This creates an FTS table that mirrors `posts.title` and `posts.body`. The FTS table has its own internal structure (the inverted index). The `rowid` of the FTS table matches the `id` of `posts`.

### Keeping the FTS Table in Sync

When you insert, update, or delete a `posts` row, the FTS table must be updated. We can do this with **triggers**:

```sql
CREATE TRIGGER posts_ai AFTER INSERT ON posts BEGIN
  INSERT INTO posts_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;

CREATE TRIGGER posts_ad AFTER DELETE ON posts BEGIN
  INSERT INTO posts_fts(posts_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
END;

CREATE TRIGGER posts_au AFTER UPDATE ON posts BEGIN
  INSERT INTO posts_fts(posts_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
  INSERT INTO posts_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;
```

The triggers run automatically. When you `INSERT INTO posts`, the FTS table is also inserted. When you `DELETE FROM posts`, the FTS table is also deleted. When you `UPDATE posts`, the FTS table is updated.

The `'delete'` command in the FTS insert is a special syntax for FTS5 — it tells FTS to delete the row. (The full syntax is `INSERT INTO posts_fts(posts_fts, rowid, ...) VALUES('delete', old.id, ...)`.)

### Searching

```sql
SELECT posts.*, posts_fts.rank
FROM posts_fts
JOIN posts ON posts_fts.rowid = posts.id
WHERE posts_fts MATCH 'hello'
ORDER BY posts_fts.rank;
```

- `posts_fts MATCH 'hello'` — search for the term "hello"
- `posts_fts.rank` — the BM25 score (lower is more relevant)
- `ORDER BY posts_fts.rank` — sort by relevance

The result is a list of posts, ordered by relevance, with the rank as a column.

## BM25

BM25 is the standard ranking algorithm for full-text search. It scores each document based on:

- **Term frequency (TF)** — how many times the search term appears in the document. More occurrences = higher score.
- **Inverse document frequency (IDF)** — how rare the term is across all documents. A rare term (e.g., "elasticsearch") is more meaningful than a common term (e.g., "the").
- **Document length** — shorter documents are more relevant (a 100-word document with 1 match is more focused than a 10000-word document with 1 match).

The formula (simplified):

```
BM25(q, d) = IDF(q) * (TF(q, d) * (k + 1)) / (TF(q, d) + k * (1 - b + b * |d| / avgdl))
```

Where:
- `q` is the search term
- `d` is the document
- `|d|` is the document length
- `avgdl` is the average document length
- `k` and `b` are constants (typically 1.2 and 0.75)

In SQLite FTS5, the rank is the negative of the BM25 score. Lower rank = more relevant. (You can flip the sign with `-posts_fts.rank` if you want higher = more relevant.)

## Query Syntax

FTS5 supports a rich query syntax:

- **Term**: `hello` — match documents containing "hello"
- **Phrase**: `"hello world"` — match the exact phrase
- **Boolean**: `hello AND world`, `hello OR world`, `hello NOT world`
- **Prefix**: `hel*` — match documents with words starting with "hel"
- **Column filter**: `title:hello` — match "hello" only in the title column

We use the simple form (`?q=hello`). The client can send more complex queries if needed.

## Common Confusions (read these)

**Confusion 1: "Why is the rank negative?"**
SQLite FTS5 returns the negative of the BM25 score so that `ORDER BY rank` (ascending) returns more relevant results first. You can flip the sign with `-rank` if you want ascending = less relevant.

**Confusion 2: "What if the FTS table is out of sync?"**
The triggers handle sync. If you bypass the triggers (e.g., direct SQL with `db.raw()`), the FTS table can become inconsistent. We use the Knex query builder, which generates normal SQL, so the triggers fire.

**Confusion 3: "What if the query has special characters?"**
FTS5's query syntax has special characters: `*`, `AND`, `OR`, `NOT`, `"`. A user could send `?q=AND` and break the query. We should sanitize or use the `query` syntax (not `MATCH`).

**Confusion 4: "Why FTS5 and not LIKE?"**
FTS5 uses an inverted index. `LIKE '%foo%'` does a table scan. FTS5 is **O(log n)**; LIKE is **O(n)**. For 1M rows, FTS5 is milliseconds; LIKE is seconds.

**Confusion 5: "What about case sensitivity?"**
FTS5 tokenizes lowercase by default. "Hello" and "hello" are the same word. The original case is preserved in the source table; the FTS table is case-insensitive.

**Confusion 6: "What about stemming?"**
FTS5 supports the Porter stemmer for English. "running" matches "ran". Other languages need different tokenizers (`unicode61` is the default; `porter` is the stemmer).

**Confusion 7: "Why FTS5 and not Elasticsearch?"**
Elasticsearch is a full-text search engine designed for scale. It's fast and feature-rich. But it's a separate service. For our scale (1M rows), FTS5 is enough. For 100M rows, Elasticsearch is better.

**Confusion 8: "What if I need fuzzy search?"**
FTS5 doesn't support fuzzy matching (typos). For that, use Meilisearch or Elasticsearch.

## What We Are About to Build

A ~300-line Express app that:

1. Has a `posts_fts` virtual table (FTS5)
2. Has triggers to keep FTS in sync
3. Has `GET /posts?q=...` that searches the FTS table
4. Returns results ordered by BM25 rank
5. Returns `{ data, meta }` with pagination

The handlers are slightly updated. The schema (validation) is unchanged. The error wall is unchanged.

In [BUILD.md](./BUILD.md) we will go line by line.
