# The Build

> *"A posts table. A foreign key. Four routes. The world is now a graph."*

We are going to add a `posts` table with a foreign key to `users`, and four new routes for posts.

## Setup

```bash
npm install better-sqlite3
```

(If you've been following along, you already have it.)

## The File

Create `server.js`. Fill it in.

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

Same as project 10.

---

## Lines 14-15: Open the Database, Enable Foreign Keys

```js
const db = new Database('app.db');
db.pragma('foreign_keys = ON');
```

`db.pragma(...)` runs a PRAGMA statement. `PRAGMA foreign_keys = ON` enables foreign key enforcement. We do it once, right after opening the database.

---

## Lines 17-29: Create the Tables

```js
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
```

`db.exec` can run multiple statements separated by `;`. We create both tables in one call.

The `posts` table:

- `id` — auto-incrementing primary key
- `user_id` — references `users(id)` with `ON DELETE CASCADE`
- `title` — required text
- `body` — required text
- `created_at` — required integer (timestamp)

The `FOREIGN KEY` clause defines the relationship. `ON DELETE CASCADE` means: when a user is deleted, their posts are deleted too.

`IF NOT EXISTS` makes this idempotent — running it multiple times is safe.

---

## Lines 31-35: User Prepared Statements (Unchanged)

```js
const insertUser = db.prepare(`
  INSERT INTO users (username, hash, created_at) VALUES (?, ?, ?)
`);
const findUserByUsername = db.prepare(`
  SELECT id, username, hash, created_at FROM users WHERE username = ?
`);
```

Same as project 10.

---

## Lines 37-52: Post Prepared Statements (NEW)

```js
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
```

### `insertPost` (no JOIN)

Inserts a post. Takes `user_id`, `title`, `body`, `created_at`. No JOIN — we're inserting, not querying.

### `findPostById` (with JOIN)

Gets one post *with* the author's username. The `JOIN users ON posts.user_id = users.id` combines the two tables. The `users.username AS author` renames the column for clarity.

### `findPostsByUserId` (no JOIN)

Gets all posts by a specific user. No JOIN needed — we just want the posts. The handler can fetch the user separately if needed.

### `findAllPosts` (with JOIN)

Gets all posts, with the author's username, newest first.

The `ORDER BY posts.created_at DESC` puts newest first.

---

## Lines 54-90: Auth Routes (Unchanged)

```js
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to the API.' });
});

app.post('/signup', async (req, res) => { ... });
app.post('/login', async (req, res) => { ... });
function authMiddleware(req, res, next) { ... }
```

All unchanged from project 10.

---

## Lines 92-100: POST /posts (NEW)

```js
app.post('/posts', authMiddleware, (req, res) => {
  const { title, body } = req.body;
  if (!title || !body) {
    return res.status(400).json({ error: 'title and body required' });
  }
  const result = insertPost.run(req.user.userId, title, body, Date.now());
  res.status(201).json({ id: result.lastInsertRowid, userId: req.user.userId, title, body });
});
```

The handler is protected by `authMiddleware`. Only authenticated users can create posts.

`req.user.userId` comes from the JWT (set in `authMiddleware`). This is the ID of the logged-in user. We use it as the `user_id` for the new post.

The foreign key constraint ensures the user exists. If `req.user.userId` doesn't exist in `users` (e.g., the user was deleted after the token was issued), the insert fails with a foreign key error. We should catch this in a future project.

---

## Lines 102-105: GET /posts (NEW)

```js
app.get('/posts', (req, res) => {
  const posts = findAllPosts.all();
  res.json(posts);
});
```

Returns all posts with their authors. No authentication required (it's a public read).

`findAllPosts.all()` returns an array. Each post has `id`, `user_id`, `title`, `body`, `created_at`, and `author` (the username from the JOIN).

For 1M posts, this is a problem (1M rows in one response). Pagination is project 18.

---

## Lines 107-113: GET /posts/:id (NEW)

```js
app.get('/posts/:id', (req, res) => {
  const post = findPostById.get(req.params.id);
  if (!post) {
    return res.status(404).json({ error: 'Not Found' });
  }
  res.json(post);
});
```

`:id` is a path parameter. Express extracts it into `req.params.id`.

`findPostById.get(id)` returns the post (with the author) or `undefined`. If undefined, return 404.

---

## Lines 115-118: GET /users/:id/posts (NEW)

```js
app.get('/users/:id/posts', (req, res) => {
  const posts = findPostsByUserId.all(req.params.id);
  res.json(posts);
});
```

Get all posts by a specific user. No JOIN — we just return the posts. (We could include the user info by fetching from `users` first, but it's not necessary for this route.)

---

## Lines 120-122: Start the Server

```js
app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

Unchanged.

---

## The Full File

The full file is shown in the README. ~120 lines total.

---

## Run It

```bash
node server.js

# Signup
curl -X POST http://localhost:3000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2"}'
# {"id":1,"username":"alice"}

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

# Create another post
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Second","body":"Post"}'
# {"id":2,"userId":1,"title":"Second","body":"Post"}

# List all posts
curl http://localhost:3000/posts
# [{"id":2,"userId":1,"title":"Second","body":"Post","author":"alice",...},
#  {"id":1,"userId":1,"title":"Hello","body":"World","author":"alice",...}]

# Get one post
curl http://localhost:3000/posts/1
# {"id":1,"userId":1,"title":"Hello","body":"World","author":"alice",...}

# Get posts by user 1
curl http://localhost:3000/users/1/posts
# [{"id":2,...},{"id":1,...}]
```

---

## Experiments

### Experiment 1: Try to insert a post with an invalid user

```js
db.prepare(`INSERT INTO posts (user_id, title, body, created_at) VALUES (?, ?, ?, ?)`).run(999, 'orphan', 'no user', Date.now());
```

This throws `FOREIGN KEY constraint failed`. The foreign key constraint is enforced.

### Experiment 2: Delete a user and see the cascade

```js
db.prepare('DELETE FROM users WHERE id = ?').run(1);
```

User 1 is deleted. All posts with `user_id = 1` are also deleted (CASCADE).

### Experiment 3: Try without `PRAGMA foreign_keys = ON`

Comment out the `db.pragma(...)` line. Restart. Try the orphan insert — it succeeds (no constraint check). The data is inconsistent. Always turn on the pragma.

### Experiment 4: Use a LEFT JOIN

```sql
SELECT posts.id, posts.title, users.username AS author
FROM posts LEFT JOIN users ON posts.user_id = users.id
```

`LEFT JOIN` returns all posts, even if the user is missing (the `author` would be NULL). With foreign keys, this shouldn't happen, but it's a good escape hatch.

### Experiment 5: Try to find posts by a non-existent user

```bash
curl http://localhost:3000/users/999/posts
# [] (empty array)
```

The query returns no rows. No 404 — the user isn't checked, just the posts. We could check if the user exists first, but it's not necessary.

### Experiment 6: Aggregate posts per user

```sql
SELECT users.username, COUNT(posts.id) AS post_count
FROM users LEFT JOIN posts ON users.id = posts.user_id
GROUP BY users.id
ORDER BY post_count DESC;
```

This is the kind of query that motivates a JOIN. We can compute "posts per user" in one query.

---

## Summary

You now have a relational database. Two tables: `users` and `posts`. They're connected by a foreign key. We can JOIN them. The relationship is enforced by the database.

The data model is now a *graph*: users have many posts; posts belong to a user. This is the foundation of every real app.

In project 12, we will add schema migrations — the ability to evolve the schema (add columns, add tables) without dropping data.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
