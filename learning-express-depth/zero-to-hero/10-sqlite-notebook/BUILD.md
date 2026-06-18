# The Build

> *"One file replaces the Map. Three queries replace the inserts. The data survives."*

We are going to replace the in-memory `USERS` Map with a SQLite database. The change from project 09: add `better-sqlite3`, create a `users` table, and use prepared statements for insert and query.

## Setup

```bash
npm install better-sqlite3
```

The `better-sqlite3` package is a synchronous binding to SQLite. It has prebuilt binaries for most platforms, so install is usually fast.

## The File

Create `server.js`. Fill it in.

---

## Lines 1-5: The Imports

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Database = require('better-sqlite3');
```

Four imports. `Database` is new.

---

## Lines 7-8: The Configuration

```js
const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';
```

Same as project 09.

---

## Lines 10-11: The App and Middleware

```js
const app = express();
app.use(express.json());
```

Same as project 09.

---

## Line 13: Open the Database

```js
const db = new Database('app.db');
```

`new Database(filename)` opens (or creates) a SQLite database. The whole database is one file. We pass `'app.db'` — the file is in the current working directory.

If `app.db` doesn't exist, it's created. If it does, it's opened. The `db` object is our handle to the database.

This is synchronous. By the time the line completes, the database is open and ready.

---

## Lines 15-21: Create the Table

```js
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    created_at INTEGER NOT NULL
  )
`);
```

`db.exec(sql)` executes one or more SQL statements. We use it for `CREATE TABLE` because it doesn't return data.

`CREATE TABLE IF NOT EXISTS` — only create if the table doesn't exist. This is idempotent. If the table already exists (from a previous run), this is a no-op.

The table has four columns:

- `id` — auto-incrementing integer, primary key
- `username` — unique text, not null
- `hash` — text, not null
- `created_at` — integer (Unix timestamp in ms), not null

This is the *schema*. It defines the structure of the table.

---

## Lines 23-25: Prepare the Insert Statement

```js
const insertUser = db.prepare(`
  INSERT INTO users (username, hash, created_at) VALUES (?, ?, ?)
`);
```

`db.prepare(sql)` compiles the SQL and returns a *prepared statement*. We can call `.run()` on it many times.

The `?` are placeholders. We'll pass actual values when we run the statement.

Preparing is one-time work. The compiled statement is cached. We define it once and use it many times.

---

## Lines 27-29: Prepare the Select Statement

```js
const findUserByUsername = db.prepare(`
  SELECT id, username, hash, created_at FROM users WHERE username = ?
`);
```

Same pattern. A prepared statement that selects a user by username.

We explicitly list the columns (`id, username, hash, created_at`) instead of `SELECT *`. This is good practice — if we add a column later (e.g., `password_reset_token`), we won't accidentally return it.

---

## Lines 31-33: The Welcome Route

```js
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});
```

Unchanged.

---

## Lines 35-50: The Signup Route (CHANGED)

```js
app.post('/signup', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }
  const existing = findUserByUsername.get(username);
  if (existing) {
    return res.status(409).json({ error: 'username already taken' });
  }
  const hash = await bcrypt.hash(password, 10);
  const result = insertUser.run(username, hash, Date.now());
  res.status(201).json({ id: result.lastInsertRowid, username });
});
```

### What changed from project 09

The `USERS.has(username)` and `USERS.set(...)` are replaced with database calls.

### `findUserByUsername.get(username)`

`.get()` runs the prepared `SELECT` statement with the given argument. Returns the row as an object, or `undefined` if no match.

`{ id, username, hash, created_at }` is the row shape. We check `if (existing)` to see if a user with that username exists.

### `insertUser.run(username, hash, Date.now())`

`.run()` executes the prepared `INSERT` statement. The arguments fill the `?` placeholders in order:
- `?` (username) ← `username`
- `?` (hash) ← `hash`
- `?` (created_at) ← `Date.now()`

Returns an object with metadata, including `lastInsertRowid` — the auto-incremented ID of the new row.

### `res.status(201).json({ id: result.lastInsertRowid, username })`

We return the new user's ID and username. The ID is useful for future references (foreign keys in project 11).

---

## Lines 52-71: The Login Route (CHANGED)

```js
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }
  const user = findUserByUsername.get(username);
  if (!user) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  const token = jwt.sign(
    { userId: user.id, username: user.username },
    SECRET,
    { expiresIn: TOKEN_TTL }
  );
  res.json({ token, user: { id: user.id, username: user.username } });
});
```

### What changed

- `USERS.get(username)` → `findUserByUsername.get(username)`
- The `user` object now has `id`, `username`, `hash`, `created_at` (from the database row)
- The token includes `userId: user.id` (the numeric ID)

### Why `userId: user.id` instead of `user.username`?

Because numeric IDs are stable. Usernames can change. IDs can't (well, they shouldn't). Foreign keys in project 11 will reference `user.id`.

---

## Lines 73-83: The authMiddleware (Unchanged)

```js
function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'missing or invalid authorization header' });
  }
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: 'invalid or expired token' });
  }
}
```

Same as project 09. The middleware is independent of the storage.

---

## Lines 85-87: The Me Route (Unchanged)

```js
app.get('/me', authMiddleware, (req, res) => {
  res.json({ user: req.user });
});
```

Same as project 09.

---

## Lines 89-91: Start the Server

```js
app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

Same as project 09.

---

## The Full File

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Database = require('better-sqlite3');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());

const db = new Database('app.db');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    created_at INTEGER NOT NULL
  )
`);

const insertUser = db.prepare(`
  INSERT INTO users (username, hash, created_at) VALUES (?, ?, ?)
`);

const findUserByUsername = db.prepare(`
  SELECT id, username, hash, created_at FROM users WHERE username = ?
`);

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});

app.post('/signup', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }
  const existing = findUserByUsername.get(username);
  if (existing) {
    return res.status(409).json({ error: 'username already taken' });
  }
  const hash = await bcrypt.hash(password, 10);
  const result = insertUser.run(username, hash, Date.now());
  res.status(201).json({ id: result.lastInsertRowid, username });
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }
  const user = findUserByUsername.get(username);
  if (!user) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  const token = jwt.sign(
    { userId: user.id, username: user.username },
    SECRET,
    { expiresIn: TOKEN_TTL }
  );
  res.json({ token, user: { id: user.id, username: user.username } });
});

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'missing or invalid authorization header' });
  }
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: 'invalid or expired token' });
  }
}

app.get('/me', authMiddleware, (req, res) => {
  res.json({ user: req.user });
});

app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

---

## Run It

```bash
npm install better-sqlite3
node server.js

# Signup
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"id":1,"username":"alice"}

# Signup another
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","password":"correcthorse"}'
# {"id":2,"username":"bob"}

# Login
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"token":"...","user":{"id":1,"username":"alice"}}

# Restart the server
# Ctrl+C, then node server.js

# Login again — the data is still there
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"token":"...","user":{"id":1,"username":"alice"}}
```

The data persists. The auth flow is the same. The storage is durable.

---

## Experiments

### Experiment 1: Inspect the database

```bash
sqlite3 app.db
```

The `sqlite3` CLI is installed with most systems. Inside:

```sql
.tables
-- users

.schema users
-- CREATE TABLE users (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   username TEXT UNIQUE NOT NULL,
--   hash TEXT NOT NULL,
--   created_at INTEGER NOT NULL
-- );

SELECT * FROM users;
-- 1|alice|$2b$10$...|1700000000000
-- 2|bob|$2b$10$...|1700000001000
```

You can see the rows. The `|` is the column separator. `id` is 1 for alice, 2 for bob.

### Experiment 2: Drop the table

```js
db.exec('DROP TABLE users');
```

Restart. The table is gone. The next signup will recreate it (because of `IF NOT EXISTS`). But wait — no it won't, because we already created it. Let me re-read. Oh, `IF NOT EXISTS` means "only create if it doesn't exist." So if we drop it, the next `CREATE TABLE` recreates it. The data is gone.

### Experiment 3: Use `:memory:` for tests

```js
const db = new Database(':memory:');
```

This creates an in-memory database. Fast. No file. Data is lost when the process exits. Useful for tests.

### Experiment 4: Use a custom column

Add a `email` column:

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE,
  hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
```

This requires dropping the table first (or using a migration, project 12). For now, just delete `app.db` and re-run.

### Experiment 5: Index on `username`

```sql
CREATE INDEX idx_users_username ON users(username);
```

For 1 million users, `SELECT ... WHERE username = ?` is slow without an index. With an index, it's fast. We don't have this problem yet (1 user). But it's good to know.

`UNIQUE` already creates an index. So `username` is already indexed. Good.

### Experiment 6: Use transactions for multi-row inserts

```js
const insertMany = db.transaction((users) => {
  for (const u of users) {
    insertUser.run(u.username, u.hash, u.createdAt);
  }
});

insertMany([
  { username: 'carol', hash: '...', createdAt: Date.now() },
  { username: 'dave', hash: '...', createdAt: Date.now() },
]);
```

A transaction wraps multiple writes. Either all succeed or all fail. We'll cover transactions in project 27.

---

## Summary

You now have a database. Users are rows in a `users` table. Sign up creates a row. Login queries it. The data persists across restarts.

The auth flow is the same. The storage is durable. The patterns (`db.prepare`, `statement.run`, `statement.get`) are universal. They work in any SQL database.

In project 11, we will add a `posts` table with a foreign key to `users`. This is the foundation of *relations* — the core of a relational database.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
