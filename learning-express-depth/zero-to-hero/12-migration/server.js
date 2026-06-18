// server.js
//
// Project 12: The Migration
// ==========================
// Adds a simple migration system. The schema is versioned. Each migration
// is applied once, in order, transactionally. Existing data is preserved.
//
// Setup:
//   npm install better-sqlite3
//   node server.js

const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const Database = require("better-sqlite3");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";

const app = express();
app.use(express.json());

const db = new Database("app.db");
db.pragma("foreign_keys = ON");

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

function runMigrations() {
  db.exec(`CREATE TABLE IF NOT EXISTS migrations (
    version INTEGER PRIMARY KEY,
    applied_at INTEGER NOT NULL
  )`);

  const applied = new Set(
    db
      .prepare("SELECT version FROM migrations")
      .all()
      .map((r) => r.version),
  );

  for (const m of MIGRATIONS) {
    if (applied.has(m.version)) continue;
    const tx = db.transaction(() => {
      db.exec(m.up);
      db.prepare(
        "INSERT INTO migrations (version, applied_at) VALUES (?, ?)",
      ).run(m.version, Date.now());
    });
    tx();
    console.log(`Applied migration ${m.version}`);
  }
}

runMigrations();

const insertUser = db.prepare(`
  INSERT INTO users (username, hash, email, created_at) VALUES (?, ?, ?, ?)
`);
const findUserByUsername = db.prepare(`
  SELECT id, username, hash, email, created_at FROM users WHERE username = ?
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

app.get("/", (req, res) => {
  res.json({ message: "Welcome to the API." });
});

app.post("/signup", async (req, res) => {
  const { username, password, email } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "username and password required" });
  }
  const existing = findUserByUsername.get(username);
  if (existing) {
    return res.status(409).json({ error: "username already taken" });
  }
  const hash = await bcrypt.hash(password, 10);
  const result = insertUser.run(username, hash, email || null, Date.now());
  res
    .status(201)
    .json({ id: result.lastInsertRowid, username, email: email || null });
});

app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "username and password required" });
  }
  const user = findUserByUsername.get(username);
  if (!user) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  const ok = await bcrypt.compare(password, user.hash);
  if (!ok) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  const token = jwt.sign({ userId: user.id, username: user.username }, SECRET, {
    expiresIn: TOKEN_TTL,
  });
  res.json({
    token,
    user: { id: user.id, username: user.username, email: user.email },
  });
});

function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith("Bearer ")) {
    return res
      .status(401)
      .json({ error: "missing or invalid authorization header" });
  }
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: "invalid or expired token" });
  }
}

app.post("/posts", authMiddleware, (req, res) => {
  const { title, body } = req.body;
  if (!title || !body) {
    return res.status(400).json({ error: "title and body required" });
  }
  const result = insertPost.run(req.user.userId, title, body, Date.now());
  res
    .status(201)
    .json({ id: result.lastInsertRowid, userId: req.user.userId, title, body });
});

app.get("/posts", (req, res) => {
  const posts = findAllPosts.all();
  res.json(posts);
});

app.get("/posts/:id", (req, res) => {
  const post = findPostById.get(req.params.id);
  if (!post) {
    return res.status(404).json({ error: "Not Found" });
  }
  res.json(post);
});

app.get("/users/:id/posts", (req, res) => {
  const posts = findPostsByUserId.all(req.params.id);
  res.json(posts);
});

app.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});
