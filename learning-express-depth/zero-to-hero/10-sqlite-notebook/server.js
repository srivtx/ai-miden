// server.js
//
// Project 10: The SQLite Notebook
// ================================
// Replaces the in-memory USERS Map with a SQLite database. Users are
// rows in a `users` table. Signup inserts. Login queries. The data
// persists across restarts.
//
// Setup:
//   npm install better-sqlite3
//   node server.js
//
// Test:
//   curl -X POST http://localhost:3000/signup \
//     -H "Content-Type: application/json" \
//     -d '{"username":"alice","password":"hunter2"}'
//   # Restart the server, log in again — data is still there.

const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const Database = require("better-sqlite3");

const SECRET = "dev-secret-change-in-prod";
const TOKEN_TTL = "7d";

const app = express();
app.use(express.json());

const db = new Database("app.db");

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

app.get("/", (req, res) => {
  res.json({ message: "Welcome to the API." });
});

app.post("/signup", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "username and password required" });
  }
  const existing = findUserByUsername.get(username);
  if (existing) {
    return res.status(409).json({ error: "username already taken" });
  }
  const hash = await bcrypt.hash(password, 10);
  const result = insertUser.run(username, hash, Date.now());
  res.status(201).json({ id: result.lastInsertRowid, username });
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
  res.json({ token, user: { id: user.id, username: user.username } });
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

app.get("/me", authMiddleware, (req, res) => {
  res.json({ user: req.user });
});

app.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});
