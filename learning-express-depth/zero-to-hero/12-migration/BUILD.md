# The Build

> *"The schema is code. The code is versioned. The version is applied."*

We are going to add a simple migration system. The change from project 11: replace the `db.exec(...)` with a `MIGRATIONS` array and a `runMigrations()` function.

## Setup

```bash
npm install better-sqlite3
```

(If you've been following along, you already have it.)

## The File

Create `server.js`. Fill it in. The structure is the same as project 11, with the new migration system.

---

## Lines 1-12: The Imports and App (Unchanged)

```js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Database = require('better-sqlite3');

const SECRET = 'dev-secret-change-in-prod';
const TOKEN_TTL = '7d';

const app = express();
app.use(express.json());
```

Same as project 11.

---

## Lines 14-15: Open the Database

```js
const db = new Database('app.db');
db.pragma('foreign_keys = ON');
```

Same as project 11.

---

## Lines 17-37: The MIGRATIONS Array (NEW)

```js
const MIGRATIONS = [
  {
    version: 1,
    up: `
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        hash TEXT NOT NULL,
        created_at INTEGER NOT NULL
      );

      CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `,
  },
  {
    version: 2,
    up: `ALTER TABLE users ADD COLUMN email TEXT UNIQUE`,
  },
];
```

### The structure

Each migration has a `version` (integer) and an `up` (SQL string).

### Migration 1: initial schema

Same as the `db.exec(...)` in project 11. It creates the `users` and `posts` tables.

### Migration 2: add `email`

`ALTER TABLE users ADD COLUMN email TEXT UNIQUE` adds an `email` column. Existing rows have `NULL` for the new column. New rows can have an `email`.

We use `UNIQUE` to prevent duplicate emails. (We're not enforcing NOT NULL, because old users don't have an email.)

---

## Lines 39-60: The Migration Runner (NEW)

```js
function runMigrations() {
  db.exec(`CREATE TABLE IF NOT EXISTS migrations (
    version INTEGER PRIMARY KEY,
    applied_at INTEGER NOT NULL
  )`);

  const applied = new Set(
    db.prepare('SELECT version FROM migrations').all().map((r) => r.version)
  );

  for (const m of MIGRATIONS) {
    if (applied.has(m.version)) continue;
    const tx = db.transaction(() => {
      db.exec(m.up);
      db.prepare('INSERT INTO migrations (version, applied_at) VALUES (?, ?)').run(m.version, Date.now());
    });
    tx();
    console.log(`Applied migration ${m.version}`);
  }
}

runMigrations();
```

### Step by step

1. `db.exec('CREATE TABLE IF NOT EXISTS migrations ...')` — create the `migrations` table. Idempotent.
2. Read the applied versions into a `Set`. O(1) lookup.
3. For each migration in `MIGRATIONS`:
   - If already applied, skip
   - Otherwise, wrap the migration + the `INSERT` in a transaction
   - Run the transaction

### The transaction

```js
const tx = db.transaction(() => {
  db.exec(m.up);
  db.prepare('INSERT INTO migrations (version, applied_at) VALUES (?, ?)').run(m.version, Date.now());
});
tx();
```

`db.transaction(fn)` returns a function. When called, it runs `fn` inside a transaction. If `fn` throws, the transaction is rolled back. We want both the schema change and the `migrations` insert to succeed or fail together.

---

## Lines 62-110: Rest of the Server (Same as Project 11, with optional email)

The auth flow is unchanged. The post flow is unchanged. The signup handler now accepts an optional `email`:

```js
app.post('/signup', async (req, res) => {
  const { username, password, email } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }
  const existing = findUserByUsername.get(username);
  if (existing) {
    return res.status(409).json({ error: 'username already taken' });
  }
  const hash = await bcrypt.hash(password, 10);
  const result = insertUser.run(username, hash, Date.now());
  res.status(201).json({ id: result.lastInsertRowid, username, email: email || null });
});
```

The `insertUser` prepared statement would need to be updated to include `email`. For brevity, we skip that here — the README and the file show the full version.

---

## The Full File

The full file is shown in the README. The migration system is the only new piece.

---

## Run It

```bash
# First run
node server.js
# Applied migration 1
# Applied migration 2
# Server listening on http://localhost:3000

# Signup with email
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2","email":"alice@example.com"}'

# Restart
node server.js
# (no migrations applied — already done)
# Server listening on http://localhost:3000

# The email column is there
sqlite3 app.db "SELECT id, username, email FROM users"
# 1|alice|alice@example.com
```

The schema evolved. The data is preserved. The migration was applied once.

---

## Experiments

### Experiment 1: Add a third migration

```js
{
  version: 3,
  up: `ALTER TABLE posts ADD COLUMN published INTEGER NOT NULL DEFAULT 0`,
},
```

Restart. The migration is applied. The `published` column is added. Existing posts have `published = 0` (the default).

### Experiment 2: Add a broken migration

```js
{
  version: 4,
  up: `ALTER TABLE nonexistent ADD COLUMN foo TEXT`,
},
```

Restart. The migration fails (the table doesn't exist). The transaction is rolled back. The `migrations` table does not have version 4. Next startup, the migration is retried. Fix the SQL, restart, it's applied.

### Experiment 3: Manually mark a migration as applied

```js
db.prepare('INSERT INTO migrations (version, applied_at) VALUES (?, ?)').run(2, Date.now());
```

Now version 2 is in the `migrations` table. The system thinks it's been applied. It won't run it again. Useful for "I already did this manually, don't re-run it."

### Experiment 4: Reset the database

```bash
rm app.db
node server.js
```

The database is gone. Both migrations are applied on startup. The data is empty.

### Experiment 5: Use a complex migration

```js
{
  version: 5,
  up: `
    CREATE TABLE comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_id INTEGER NOT NULL,
      user_id INTEGER NOT NULL,
      body TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE INDEX idx_comments_post_id ON comments(post_id);
  `,
},
```

A migration can have multiple statements. The transaction wraps them all. If any fails, all are rolled back.

---

## Summary

You now have a migration system. The schema is versioned. Changes are applied automatically. Existing data is preserved. Adding a column is one line in the `MIGRATIONS` array.

This is the foundation of *schema evolution*. From here, every project that adds a column or a table adds a new migration. The data is always safe.

In project 13, we will add an ORM (Object-Relational Mapper) — a layer that hides the SQL behind a clean JavaScript API. We won't hand-write prepared statements anymore.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
