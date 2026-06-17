// 04_crud_sqlite.js — CRUD with real SQL database. Learn: SQL, prepared statements, schema.

const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

// ---- Database setup ----
const db = new Database(':memory:'); // in-memory SQLite (use './data.db' for file)
db.pragma('journal_mode = WAL'); // better concurrency

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
  )
`);

// CREATE
app.post('/users', (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) return res.status(400).json({ error: 'name and email required' });
  try {
    const stmt = db.prepare('INSERT INTO users (name, email) VALUES (?, ?)');
    const result = stmt.run(name, email);
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(result.lastInsertRowid);
    res.status(201).json(user);
  } catch (e) {
    if (e.message.includes('UNIQUE')) return res.status(409).json({ error: 'Email already exists' });
    throw e;
  }
});

// READ all (with pagination: ?page=1&limit=10)
app.get('/users', (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const offset = (page - 1) * limit;
  const users = db.prepare('SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?').all(limit, offset);
  const total = db.prepare('SELECT COUNT(*) as count FROM users').get().count;
  res.json({ page, limit, total, users });
});

// READ one
app.get('/users/:id', (req, res) => {
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.params.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json(user);
});

// UPDATE
app.put('/users/:id', (req, res) => {
  const { name, email } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.params.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  db.prepare('UPDATE users SET name = COALESCE(?, name), email = COALESCE(?, email) WHERE id = ?')
    .run(name || null, email || null, req.params.id);
  res.json(db.prepare('SELECT * FROM users WHERE id = ?').get(req.params.id));
});

// DELETE
app.delete('/users/:id', (req, res) => {
  const result = db.prepare('DELETE FROM users WHERE id = ?').run(req.params.id);
  if (result.changes === 0) return res.status(404).json({ error: 'User not found' });
  res.status(204).send();
});

app.listen(3000, () => console.log('SQLite CRUD on :3000'));
