// 04-todo-auth: Add users, signup, login, JWT. Each user has their own todos.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT)`);
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL REFERENCES users(id), title TEXT NOT NULL, done INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);

function hashPassword(pw, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  return { hash: crypto.pbkdf2Sync(pw, salt, 100000, 64, 'sha512').toString('hex'), salt };
}
function verifyPassword(pw, hash, salt) {
  const test = crypto.pbkdf2Sync(pw, salt, 100000, 64, 'sha512').toString('hex');
  return test.length === hash.length && crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(hash, 'hex'));
}
function auth(req, res, next) {
  const token = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch { res.status(401).json({ error: 'unauthorized' }); }
}

// Signup
app.post('/auth/signup', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password || password.length < 8) return res.status(422).json({ error: 'invalid input' });
  const id = 'u_' + crypto.randomBytes(4).toString('hex');
  const { hash, salt } = hashPassword(password);
  try {
    db.prepare('INSERT INTO users (id, email, password_hash, salt) VALUES (?, ?, ?, ?)').run(id, email, hash, salt);
    res.status(201).json({ user: { id, email }, token: jwt.sign({ sub: id, email }, SECRET, { expiresIn: '7d' }) });
  } catch { res.status(409).json({ error: 'email taken' }); }
});

// Login
app.post('/auth/login', (req, res) => {
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(req.body.email);
  if (!user || !verifyPassword(req.body.password, user.password_hash, user.salt)) return res.status(401).json({ error: 'invalid' });
  res.json({ user: { id: user.id, email: user.email }, token: jwt.sign({ sub: user.id, email: user.email }, SECRET, { expiresIn: '7d' }) });
});

// Todos — only the user's own
app.get('/todos', auth, (req, res) => {
  const todos = db.prepare('SELECT * FROM todos WHERE user_id = ? ORDER BY id DESC').all(req.user.sub);
  res.json({ count: todos.length, todos });
});

app.post('/todos', auth, (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const r = db.prepare('INSERT INTO todos (user_id, title) VALUES (?, ?)').run(req.user.sub, req.body.title);
  res.status(201).json(db.prepare('SELECT * FROM todos WHERE id = ?').get(r.lastInsertRowid));
});

app.patch('/todos/:id', auth, (req, res) => {
  const todo = db.prepare('SELECT * FROM todos WHERE id = ? AND user_id = ?').get(parseInt(req.params.id), req.user.sub);
  if (!todo) return res.status(404).json({ error: 'not found or not yours' });
  if (req.body.title !== undefined) db.prepare('UPDATE todos SET title = ? WHERE id = ?').run(req.body.title, todo.id);
  if (req.body.done !== undefined) db.prepare('UPDATE todos SET done = ? WHERE id = ?').run(req.body.done ? 1 : 0, todo.id);
  res.json(db.prepare('SELECT * FROM todos WHERE id = ?').get(todo.id));
});

app.delete('/todos/:id', auth, (req, res) => {
  const r = db.prepare('DELETE FROM todos WHERE id = ? AND user_id = ?').run(parseInt(req.params.id), req.user.sub);
  r.changes ? res.status(204).end() : res.status(404).json({ error: 'not found or not yours' });
});

app.listen(3000, () => console.log('04-todo-auth on :3000'));
