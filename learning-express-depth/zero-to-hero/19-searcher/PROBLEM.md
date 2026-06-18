# The Problem

> *"LIKE '%foo%' is a full table scan. For 1M rows, that's 1M comparisons. For 100M rows, the database catches fire."*

## Why LIKE Is Slow

A `LIKE` query with a leading wildcard (`'%foo%'`) cannot use an index. The database has to *scan every row* and check if the pattern matches.

```sql
SELECT * FROM posts WHERE title LIKE '%hello%';
```

For 1M rows, this reads every row, compares the title, and returns the matches. The cost is **O(n)** in the number of rows. The query time grows linearly with the table size.

For 10 rows, LIKE is fine. For 1M rows, LIKE is seconds. For 100M rows, LIKE is minutes. The user waits. The database is on fire.

## What Pain Is This Solving?

Imagine the alternative. You have 1M posts. A user types "hello" in the search box. Your server runs `SELECT * FROM posts WHERE title LIKE '%hello%'`. The database scans all 1M rows. The query takes 5 seconds. The user sees a spinner. They refresh. The query runs again. The database is now under double load.

Multiply by 1000 concurrent users. The database is overwhelmed. The site goes down. The CEO calls you. You have a bad day.

The fix is **full-text search**. The database builds an *inverted index* — a mapping from words to rows. Searching for "hello" is a lookup in the index: "which rows contain 'hello'?" The cost is **O(log n)** — constant, regardless of the table size.

For 1M rows, FTS is milliseconds. For 100M rows, FTS is still milliseconds. The user is happy. The database is calm. The CEO is happy. You have a good day.

## The Deeper Problem: Search Is Not Just Speed

Search is not just about speed. It's also about *relevance*. If a user searches for "hello," do they want:

- Posts with "hello" in the title (more relevant)?
- Posts with "hello" in the body (less relevant)?
- Posts that mention "hello" once or many times?
- Posts that mention "hello" recently or a long time ago?

`LIKE '%hello%'` answers "does the text contain 'hello'?" but doesn't tell you *which* results are most relevant.

FTS5 uses the **BM25** algorithm to rank results. BM25 considers:

- **Term frequency** — how often does the word appear in the document?
- **Inverse document frequency** — how rare is the word across all documents?
- **Document length** — shorter documents are more relevant for a given match count.

The result is a *rank score* per document. The lower the score (in SQLite's convention), the more relevant. The client can sort by rank.

FTS5 also supports:
- **Tokenization** — splitting "Hello, World!" into ["hello", "world"]
- **Stemming** — "running" matches "ran" (Porter stemmer, English)
- **Highlighting** — `**hello**` to mark the match in the original text
- **Phrase queries** — `"hello world"` matches the exact phrase
- **Boolean queries** — `hello AND world`, `hello OR world`, `hello NOT world`

## What This Project Will Solve

This project will:

1. Create a virtual `posts_fts` table (FTS5)
2. Index `title` and `body` from `posts`
3. Keep the FTS table in sync with `posts` (on insert, update, delete)
4. Add a `?q=` query parameter to `GET /posts`
5. Use `MATCH` against the FTS table when `q` is provided
6. Return results ordered by BM25 rank

By the end, the API has search. The user can find posts by text. The results are ranked by relevance.

## What This Project Will *Not* Solve

- **Typo tolerance** — FTS5 doesn't fuzzy-match. "helo" doesn't match "hello". For that, use Meilisearch or Elasticsearch.
- **Multi-language stemming** — FTS5 uses Porter stemmer (English). For other languages, you'd use a different stemmer or a different search engine.
- **Faceted search** — "posts about X, in category Y, by author Z, sorted by date." Out of scope.
- **Highlighting** — `**hello**` markers in the response. Out of scope (we can add).
- **Search-as-you-type** — incremental search. Out of scope.
- **Synonyms** — "car" matches "automobile". Out of scope (FTS5 has limited support; Meilisearch has more).

## The Question This Project Answers

> *"How do I find rows by text, fast and ranked?"*

If you can answer: "use FTS5, build an inverted index, search with MATCH, rank by BM25," you are ready for project 20.
