# Project 11: The Foreign Key

> *"One table is a list. Two tables connected is a graph. Three is a world."*

Project 10 gave us one table: `users`. Real apps have many tables, and they are *related*. A post has an author (a user). A comment has a post and an author. An order has a user and products.

This project adds a `posts` table with a **foreign key** to `users`. A post's `user_id` column references a user's `id`. Now we can:

- Create a post (linked to the logged-in user)
- List all posts
- List all posts by a specific user
- Get a post with its author info

The foundation of *relations* is built.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why multiple tables? What is a foreign key?
2. [The Thought](./THOUGHT.md) — How do foreign keys work? What is a JOIN?
3. [The Build](./BUILD.md) — Line-by-line construction of the posts table and routes
4. [The Decisions](./DECISIONS.md) — Why a separate table? Why not a JSON column? Why not a foreign key?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A *foreign key* is a column in one table that references the primary key of another. `posts.user_id` references `users.id`. SQLite (with `PRAGMA foreign_keys = ON`) enforces the constraint: you can't insert a post with a `user_id` that doesn't exist in `users`. A *JOIN* lets us combine rows from two tables. `SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id` returns posts with their authors. Foreign keys + JOINs are the foundation of relational databases.

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
db.pragma('foreign_keys = ON');

db.exec(`
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
`);

const insertUser = db.prepare(`
  INSERT INTO users (username, hash, created_at) VALUES (?, ?, ?)
`);
const findUserByUsername = db.prepare(`
  SELECT id, username, hash, created_at FROM users WHERE username = ?
`);

const insertPost = db.prepare(`
  INSERT INTO posts (user_id, title, body, created_at) VALUES (?, ?, ?, ?)
`);
const findPostById = db.prepare(`
  SELECT posts.id, posts.user_id, posts.title, posts.body, posts.created_at,
         users.username AS author
  FROM posts JOIN users ON posts.user_id = users.id
  WHERE posts.id = ?
`);
const findPostsByUserId = db.prepare(`
  SELECT id, user_id, title, body, created_at FROM posts WHERE user_id = ? ORDER BY created_at DESC
`);
const findAllPosts = db.prepare(`
  SELECT posts.id, posts.user_id, posts.title, posts.body, posts.created_at,
         users.username AS author
  FROM posts JOIN users ON posts.user_id = users.id
  ORDER BY posts.created_at DESC
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
  const token = jwt.sign({ userId: user.id, username: user.username }, SECRET, { expiresIn: TOKEN_TTL });
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

app.post('/posts', authMiddleware, (req, res) => {
  const { title, body } = req.body;
  if (!title || !body) {
    return res.status(400).json({ error: 'title and body required' });
  }
  const result = insertPost.run(req.user.userId, title, body, Date.now());
  res.status(201).json({ id: result.lastInsertRowid, userId: req.user.userId, title, body });
});

app.get('/posts', (req, res) => {
  const posts = findAllPosts.all();
  res.json(posts);
});

app.get('/posts/:id', (req, res) => {
  const post = findPostById.get(req.params.id);
  if (!post) {
    return res.status(404).json({ error: 'Not Found' });
  }
  res.json(post);
});

app.get('/users/:id/posts', (req, res) => {
  const posts = findPostsByUserId.all(req.params.id);
  res.json(posts);
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

# Login
TOKEN=$(curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# Create a post
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","body":"World"}'
# {"id":1,"userId":1,"title":"Hello","body":"World"}

# List all posts
curl http://localhost:3000/posts
# [{"id":1,"userId":1,"title":"Hello","body":"World","author":"alice",...}]

# Get one post
curl http://localhost:3000/posts/1
# {"id":1,"userId":1,"title":"Hello","body":"World","author":"alice",...}

# Get posts by user 1
curl http://localhost:3000/users/1/posts
# [{"id":1,"userId":1,...}]
```

The pain of "I can't connect entities" is solved. Posts are linked to users. We can query posts by user. We can join tables to get the author's name.

---

## What You Will Have Learned

- What a foreign key is (a column that references another table's primary key)
- How to enable foreign keys in SQLite (`PRAGMA foreign_keys = ON`)
- How to define a foreign key in `CREATE TABLE` (`FOREIGN KEY (col) REFERENCES other(id)`)
- What `ON DELETE CASCADE` does (delete child rows when parent is deleted)
- What a `JOIN` is (combining rows from two tables)
- How to write `INNER JOIN` with `ON`
- How path parameters work (`req.params.id`)

These are the foundations of *relations* in databases. From here, every project uses foreign keys and JOINs.
