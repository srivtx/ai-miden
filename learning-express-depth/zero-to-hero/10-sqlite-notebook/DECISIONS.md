# The Decisions

> *"SQLite is the simplest database. better-sqlite3 is the simplest API. We start with the foundation."*

## Decision 1: SQLite and not Postgres/MySQL

**Alternatives**:
- **Postgres** — production-grade, more features, JSONB, full-text search, etc.
- **MySQL** — production-grade, widely used
- **MongoDB** — document database, not relational

**Why SQLite**: Zero setup. Single file. Fast for small-to-medium workloads. Used in every smartphone, every browser, every Mac. Perfect for learning.

**Trade-off**: Single writer. No network. No replication. For high-scale production, you'd use Postgres. The transition is straightforward (similar SQL, similar concepts).

## Decision 2: `better-sqlite3` and not `sqlite3`

**Alternatives**:
- **`sqlite3`** — async, callback-based, older
- **`better-sqlite3`** — sync, promise-free, faster
- **`node:sqlite`** — built into Node 22+, sync

**Why `better-sqlite3`**: Faster, simpler API, no callbacks. The sync API is fine because SQLite is so fast.

**Trade-off**: Synchronous means long queries block the event loop. For our scale, queries are microseconds. We don't notice. For high-throughput apps, use the async `sqlite3` or Postgres.

## Decision 3: Numeric `id` as primary key

**Alternative**: `username` as primary key.

**Why numeric ID**: Stable (usernames can change). Faster joins. Standard convention. Allows multiple users with the same display name.

**Trade-off**: An extra column. We have to remember to use `id` for foreign keys.

## Decision 4: `INTEGER` for `created_at` instead of `DATETIME`

**Alternative**: SQLite's `DATETIME` type, or ISO strings.

**Why integer**: SQLite doesn't have a native date type. Unix timestamps (milliseconds since 1970) are simple, fast, and easy to convert with `new Date(timestamp)`.

**Trade-off**: Less readable in raw SQL. `1700000000000` is less obvious than `'2024-01-15'`. We can format in the API response.

## Decision 5: `AUTOINCREMENT` instead of default

**Alternative**: Just `INTEGER PRIMARY KEY` (uses rowid).

**Why AUTOINCREMENT**: Guarantees IDs are monotonically increasing and never reused. Default behavior reuses IDs after delete.

**Trade-off**: Slightly slower (needs to track the max ID). We accept this for correctness.

## Decision 6: Explicit column list in `SELECT`

**Alternative**: `SELECT *`.

**Why explicit**: If we add a column later (e.g., `password_reset_token`), we won't accidentally return it. We control the API surface.

**Trade-off**: A bit more verbose. We accept this for safety.

## Decision 7: Prepared statements for everything

**Alternative**: String concatenation.

**Why prepared statements**: SQL injection prevention. The `?` placeholders are filled with parameterized values. The database treats them as data, not as SQL.

**Trade-off**: None. Always use prepared statements.

## Decision 8: No password column rename

**Alternative**: Rename `hash` to `password_hash` for clarity.

**Why we don't**: The column name `hash` is fine. It's the bcrypt hash, not the password. Renaming is a project 12 (Migration) concern.

## Decision 9: No index on `created_at`

We don't query by `created_at` often. We don't need an index.

**Why no index**: Indexes have a cost (slower writes, more storage). We only add indexes for columns we query often. `username` is indexed automatically (because of `UNIQUE`).

## Decision 10: No transactions yet

**Alternative**: Wrap each request in a transaction.

**Why we don't**: We have one statement per request. Transactions matter when we have multiple writes that must succeed or fail together. We'll cover this in project 27 (Transaction).

---

## What We Did Not Decide

- **Multiple entity types** — we have only `users`. Project 11 adds `posts`.
- **Foreign keys** — we don't have relations yet. Project 11.
- **Schema evolution** — we have one `CREATE TABLE`. If we change the schema, we have to drop and recreate. Project 12.
- **ORM** — we hand-write SQL. Project 13.
- **Connection pooling** — `better-sqlite3` is sync, no pool. For Postgres, we'd need one.
- **Transactions** — single-statement writes don't need them. Project 27.
- **Backups** — `app.db` is the backup target. Project 39 (Observability) or a separate concern.
- **Replication** — single file, single point of failure. Out of scope for the learning path.

Each is a future decision.

---

## The Meta-Decision: The Data Layer Begins

For 9 projects, our data was either in code (constants) or in memory (`Map`s). The server was the source of truth. Restart, lose everything.

Now we have a *database*. The data is on disk. The server is just a *reader* and *writer* of the data. The data outlives the server.

This is the foundation of every real app. From here, we add:

- **Multiple tables** (project 11): `posts`, `comments`, etc.
- **Foreign keys** (project 11): relations between tables
- **Schema evolution** (project 12): add columns, add tables, safely
- **ORM** (project 13): cleaner database code
- **Transactions** (project 27): atomic multi-write operations
- **Indexing** (project 22-23): faster queries

The auth flow is solid. The data layer is starting. The path continues.
