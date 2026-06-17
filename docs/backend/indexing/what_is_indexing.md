## Why it exists (THE PROBLEM)

You have a `users` table with 10 million rows. You run `SELECT * FROM users WHERE email = 'zen@test.com'`. The database takes 4 seconds. Why? It scans every row (full table scan) checking the email. 10M rows × 0.5µs per comparison = 4 seconds. Without an index, the database has no way to jump to the matching row.

**Index** = a sorted data structure (usually B-tree) that lets the database find matching rows in O(log n) instead of O(n). With an index on `email`, the same query takes 5ms (8 comparisons instead of 10 million). 800× speedup.

This is the single most impactful performance optimization for databases. 90% of "slow query" problems are solved by adding the right index.

## Definition (very simple)

**Index** = a sorted lookup table. The database maintains a separate data structure that maps index values to row locations. Instead of scanning the whole table, the database does a binary search on the index.

```sql
-- Without index: O(n) full table scan
SELECT * FROM users WHERE email = 'zen@test.com';  -- 4 seconds

-- Add index: O(log n) binary search
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'zen@test.com';  -- 5ms
```

## Real-life analogy

**Without index = textbook with no table of contents.** To find "the section about photosynthesis," you flip through every page (4 minutes).

**With index = textbook with an index page at the back.** Look up "photosynthesis" alphabetically → page 142 → done (10 seconds).

The textbook is unchanged. You added a tiny separate structure (the index) that points to where the information is.

## Tiny numeric example

Table `users` with 10M rows, no index on `email`:

```sql
-- Time: ~4 seconds
SELECT * FROM users WHERE email = 'zen@test.com';
-- Database: scan all 10M rows, check email on each
-- 10M * 0.4µs = 4 seconds
```

After `CREATE INDEX idx_users_email ON users(email);`:

```sql
-- Time: ~5ms
SELECT * FROM users WHERE email = 'zen@test.com';
-- Database: B-tree lookup, 23 comparisons (log2(10M) ≈ 23)
-- 23 * 0.2µs = 5µs + disk read
```

**800× speedup** on a 10M-row table. On a 1B-row table, the difference is 40 seconds vs 0.1ms (400,000×).

## Common confusion (5+ bullet points)

1. **"Index everything."** Each index slows down writes (INSERT, UPDATE, DELETE). The database must update the index for every row changed. 10 indexes on a table = 10× slower writes. Index the columns you FILTER and SORT by, not everything.

2. **"My index is slow."** Probably a BAD index. Common mistakes: indexing a column with only 2 distinct values (boolean, gender). The database ignores the index (full scan is faster). Index columns with high cardinality (millions of distinct values).

3. **"SELECT * defeats my index."** Mostly true. If you SELECT only indexed columns, the database can return the answer WITHOUT reading the table. If you SELECT other columns too, the database has to look up the row after finding it via index. 100× difference.

4. **"Composite index vs separate indexes."** Composite index on (a, b) is used for queries on `a` alone, `a + b`, but NOT `b` alone. The order matters. (last_name, first_name) is good for "find by last name" or "find by full name", bad for "find by first name".

5. **"EXPLAIN ANALYZE."** Always run this on slow queries. SQLite: `EXPLAIN QUERY PLAN SELECT ...`. PostgreSQL: `EXPLAIN ANALYZE SELECT ...`. Shows whether the index is actually used, and what scan type is happening (full table scan, index scan, index-only scan).

6. **"When NOT to index."** Tiny tables (< 1000 rows) — full scan is faster than index lookup. Columns that are rarely queried. Frequently updated columns (each write updates the index). Columns with NULL or low-cardinality values.

## Key properties

| Property | No index | With index |
|---|---|---|
| SELECT WHERE | O(n) full scan | O(log n) B-tree |
| Insert/Update/Delete | No overhead | Index must be updated |
| Disk space | Just table | Table + index |
| 10M row query | 4 seconds | 5ms |
| 1B row query | 7 minutes | 50ms |

## Tech comparison: index types

| Type | Use case | DBs |
|---|---|---|
| **B-tree** (default) | Equality, range, ORDER BY | All |
| **Hash** | Equality only, faster lookup | PostgreSQL, MySQL |
| **GIN** | Full-text search, JSONB | PostgreSQL |
| **Partial** | Index a subset (WHERE clause) | PostgreSQL |
| **Full-text (FTS)** | Tokenized text search | SQLite (FTS5), Postgres |

## Connection to our projects

Look at our 73 apps. Every single one has queries like:
- `WHERE user_id = ?` — should have index on `user_id`
- `WHERE email = ?` — should have UNIQUE index on `email`
- `ORDER BY created_at DESC LIMIT 20` — should have index on `created_at`

Right now most are 100-row dev datasets (no index needed). At 10K+ rows: add indexes. The pattern is the same: `CREATE INDEX idx_X_Y ON table_name(column);`. Run it on every foreign key, every column you filter by, every column you sort by. In production. NOT in dev. (Indexes on tiny tables are just overhead.)

## SQLite indexes (practical)

```sql
-- Always: index foreign keys
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Always: index unique emails (auto-created by UNIQUE constraint)
-- This is already done by the UNIQUE keyword:
CREATE TABLE users (email TEXT UNIQUE, ...);  -- creates automatic index

-- Often: index status, created_at for sorting
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created ON tasks(created_at DESC);

-- Composite: index common filter combinations
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- Test it: did the index actually help?
EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE user_id = 42;
-- Should show: USING INDEX idx_tasks_user_id (not SCAN)
```
