# The Thought

> *"SQL is a language for asking questions of data. SQLite answers. better-sqlite3 is the bridge."*

## What SQL Is

SQL (Structured Query Language) is the standard language for relational databases. It has four main operations:

- **SELECT** — read rows
- **INSERT** — create a row
- **UPDATE** — modify a row
- **DELETE** — remove a row

Plus operations for creating and modifying tables:

- **CREATE TABLE** — define a new table
- **ALTER TABLE** — modify a table
- **DROP TABLE** — delete a table

Example:

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

INSERT INTO users (username, hash, created_at) VALUES ('alice', '$2b$...', 1234567890);

SELECT * FROM users WHERE username = 'alice';
```

Every SQL database (Postgres, MySQL, SQLite, etc.) speaks this language. The syntax varies slightly; the concepts are universal.

## What SQLite Is

SQLite is a *serverless* database engine. There is no database server. The whole database is a single file on disk. You open the file, run queries, close the file.

Why SQLite is great for development:

- **Zero setup** — no server to install, no `docker run postgres`, no connection string
- **Single file** — `app.db` is your entire database
- **Fast** — for small-to-medium workloads, faster than Postgres
- **Reliable** — used in every smartphone, every browser, every Mac

Why SQLite is not enough for production:

- **Single writer** — only one process can write at a time. High-write workloads suffer.
- **No network** — the file is local. You can't have a separate DB server.
- **No replication** — single point of failure.

For learning and small apps, SQLite is perfect. For high-scale production, you'd use Postgres or MySQL.

## What `better-sqlite3` Is

`better-sqlite3` is a Node library that talks to SQLite. It is:

- **Synchronous** — no callbacks, no promises. `db.prepare(...).get(...)` is just a function call.
- **Fast** — faster than `sqlite3` (the async alternative).
- **Bindings** — it uses a native C binding to SQLite.

The synchronous API is unusual for Node (where everything is async). But SQLite is so fast that the synchronous API is fine. The query runs in microseconds.

## Prepared Statements

A *prepared statement* is a pre-compiled SQL query. You prepare it once, then run it many times with different parameters.

```js
const insertUser = db.prepare(`
  INSERT INTO users (username, hash, created_at) VALUES (?, ?, ?)
`);

insertUser.run('alice', '$2b$...', 1234567890);
insertUser.run('bob', '$2b$...', 1234567891);
```

The `?` are *placeholders*. The values are passed separately. This is critical for **SQL injection prevention**.

### SQL Injection

Imagine you don't use prepared statements:

```js
const username = req.body.username;  // user input
db.exec(`INSERT INTO users (username, hash) VALUES ('${username}', '...')`);
```

If the user sends `username = "alice', '...'); DROP TABLE users; --"`, the SQL becomes:

```sql
INSERT INTO users (username, hash) VALUES ('alice', '...'); DROP TABLE users; --', '...')
```

The `'` closes the string. The `);` ends the INSERT. The `DROP TABLE users;` is a new statement. The `--` comments out the rest.

Boom. Your users table is gone.

Prepared statements prevent this because the value is treated as data, not as SQL. The `?` is a *parameter*, not a *placeholder*. The database engine handles the escaping.

**Always use prepared statements. Never concatenate user input into SQL.**

## The Schema

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
```

- `id INTEGER PRIMARY KEY AUTOINCREMENT` — auto-incrementing numeric ID. Each row gets a unique number.
- `username TEXT UNIQUE NOT NULL` — the username, must be unique and not null.
- `hash TEXT NOT NULL` — the bcrypt hash, not null.
- `created_at INTEGER NOT NULL` — Unix timestamp in milliseconds.

`UNIQUE` means SQLite will reject duplicate usernames. `NOT NULL` means the column is required.

## The Operations

### Insert

```js
const insertUser = db.prepare(`
  INSERT INTO users (username, hash, created_at) VALUES (?, ?, ?)
`);

const result = insertUser.run(username, hash, Date.now());
// result.lastInsertRowid is the new user's id
```

`statement.run(...args)` executes the statement. Returns an object with metadata, including `lastInsertRowid` (the auto-incremented ID of the new row).

### Select one

```js
const findUserByUsername = db.prepare(`
  SELECT id, username, hash, created_at FROM users WHERE username = ?
`);

const user = findUserByUsername.get(username);
// user is { id, username, hash, created_at } or undefined
```

`statement.get(...args)` returns the first row as an object, or `undefined` if no match.

### Select all

```js
const allUsers = db.prepare(`SELECT * FROM users`);
const users = allUsers.all();
// users is an array
```

`statement.all()` returns all rows as an array.

### Other operations

- `statement.iterate()` — returns an iterator (for large results)
- `db.exec(multipleStatements)` — execute multiple SQL statements separated by `;` (used for `CREATE TABLE`)

## Common Confusions (read these)

**Confusion 1: "Why synchronous?"**
SQLite operations are very fast (microseconds). Making them async would add overhead (microseconds → milliseconds). For most apps, synchronous is fine. For high-throughput apps, you'd use `sqlite3` (async) or Postgres.

**Confusion 2: "Where is the database file?"**
We pass `'app.db'` to the `Database` constructor. The file is in the current working directory. You can also pass `':memory:'` for an in-memory database (useful for tests).

**Confusion 3: "What if I delete app.db?"**
All data is gone. The next time the server starts, it creates a new empty database. SQLite doesn't have a built-in backup. You'd copy the file.

**Confusion 4: "What if two servers write at the same time?"**
SQLite uses file locking. The second writer will fail with `SQLITE_BUSY`. For a single-server app, this is fine. For multi-server, use Postgres (which has proper concurrency control).

**Confusion 5: "Can I use SQL features specific to Postgres?"**
No. SQLite is a smaller subset. No `JSONB`, no `ARRAY`, no `UUID` type. Most basic SQL works in both. We use only standard SQL.

**Confusion 6: "Why `INTEGER` for `created_at` instead of `DATETIME`?"**
SQLite doesn't have a native date type. We store Unix timestamps in milliseconds as integers. This is the convention. You can format them in JS with `new Date(timestamp).toISOString()`.

**Confusion 7: "What is `AUTOINCREMENT`?"**
It tells SQLite to automatically assign an incrementing ID. Without it, SQLite uses the *rowid* (which can be reused after a delete). With it, IDs are monotonically increasing and never reused.

**Confusion 8: "Why not use an ORM?"**
We will in project 13. For now, raw SQL is fine for two queries.

## What We Are About to Build

A ~60-line Express app that:

1. Has the same routes as project 09
2. Uses a `users` table instead of a `Map`
3. Uses prepared statements for insert and query
4. Persists across restarts

The handlers are almost identical to project 09. The `USERS` Map is replaced by `db.prepare(...)` statements. The signup handler inserts a row. The login handler queries a row.

In [BUILD.md](./BUILD.md) we will go line by line.
