// 09-todo-caching: In-memory cache with TTL. Invalidate on write.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);

// Simple in-memory cache
const cache = new Map();
const TTL_MS = 30 * 1000;

function getCached(key) {
  const entry = cache.get(key);
  if (!entry) return null;
  if (entry.expiresAt < Date.now()) {
    cache.delete(key);
    return null;
  }
  return entry.data;
}
function setCache(key, data) {
  cache.set(key, { data, expiresAt: Date.now() + TTL_MS });
}
function invalidate(...keys) {
  for (const k of keys) cache.delete(k);
}

app.get('/todos', (req, res) => {
  const cached = getCached('todos:list');
  if (cached) {
    res.set('X-Cache', 'HIT');
    return res.json(cached);
  }
  const todos = db.prepare('SELECT * FROM todos ORDER BY id DESC').all();
  const result = { count: todos.length, todos };
  setCache('todos:list', result);
  res.set('X-Cache', 'MISS');
  res.json(result);
});

app.post('/todos', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const r = db.prepare('INSERT INTO todos (title) VALUES (?)').run(req.body.title);
  invalidate('todos:list', 'todos:stats');  // Invalidate the cache
  res.status(201).json(db.prepare('SELECT * FROM todos WHERE id = ?').get(r.lastInsertRowid));
});

app.patch('/todos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(id);
  if (!todo) return res.status(404).json({ error: 'not found' });
  const updates = [];
  const params = [];
  if (req.body.title !== undefined) { updates.push('title = ?'); params.push(req.body.title); }
  if (req.body.done !== undefined) { updates.push('done = ?'); params.push(req.body.done ? 1 : 0); }
  if (!updates.length) return res.status(422).json({ error: 'no updates' });
  params.push(id);
  db.prepare(`UPDATE todos SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  invalidate('todos:list');  // Invalidate
  res.json(db.prepare('SELECT * FROM todos WHERE id = ?').get(id));
});

app.delete('/todos/:id', (req, res) => {
  const r = db.prepare('DELETE FROM todos WHERE id = ?').run(parseInt(req.params.id));
  if (!r.changes) return res.status(404).json({ error: 'not found' });
  invalidate('todos:list');
  res.status(204).end();
});

app.get('/admin/cache', (req, res) => res.json({ size: cache.size, keys: Array.from(cache.keys()) }));

app.listen(3000, () => console.log('09-todo-caching on :3000'));
