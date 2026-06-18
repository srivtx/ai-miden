# Project 10: The SQLite Notebook

> *"Memory is volatile. Disk is forever. Let's persist."*

Projects 06-09 used in-memory storage. Sessions, users — all in `Map`s. Restart the server, all data is gone. The auth flow is real, but the data is ephemeral.

This project introduces **SQLite** — the simplest database. It's a single file on disk. No server to install. No connection string. Just `better-sqlite3` and a file path.

By the end, our users will be in a `users` table. Sign up creates a row. Login queries the row. Restart the server, the data is still there. The auth flow is the same; the storage is durable.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is in-memory bad? Why a database?
2. [The Thought](./THOUGHT.md) — What is SQL? What is SQLite? What is `better-sqlite3`?
3. [The Build](./BUILD.md) — Line-by-line construction of the SQLite-backed auth
4. [The Decisions](./DECISIONS.md) — Why SQLite? Why not Postgres? Why better-sqlite3?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

SQLite is a serverless database engine. The whole database is one file. `better-sqlite3` is a Node library that talks to SQLite synchronously — no callbacks, no promises for the basic operations. We create a `db` object, run `db.exec` to create tables, and use prepared statements (`db.prepare`) to insert and query. The auth flow is the same as project 09; the only change is the storage. Users are rows in a `users` table, not entries in a `Map`.

---

## The Code

```js
// server.js
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

Setup:

```bash
npm install better-sqlite3
node server.js
```

Test it:

```bash
# Signup
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"id":1,"username":"alice"}

# Restart the server
# Ctrl+C
node server.js

# Login (data is still there!)
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"token":"...","user":{"id":1,"username":"alice"}}
```

The pain of "I lose all data on restart" is solved. The auth flow is the same. The storage is durable.

---

## What You Will Have Learned

- What SQL is (a query language for relational databases)
- What SQLite is (a serverless database engine, one file)
- What `better-sqlite3` is (a synchronous Node binding to SQLite)
- How to create a table with `CREATE TABLE`
- How to use prepared statements (`db.prepare`) to prevent SQL injection
- How to insert and query with `INSERT` and `SELECT`
- Why a primary key matters (uniquely identifies a row)

These are the foundations of *data persistence*. From here, every project uses a database. The patterns (`db.prepare`, `statement.run`, `statement.get`) become the default.
