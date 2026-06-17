// Todo API — The classic first project. CRUD + filter by status.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER DEFAULT 0, priority TEXT DEFAULT 'medium', created_at TEXT DEFAULT (datetime('now')))`);

app.get('/todos', (req, res) => {
  const { done, priority, q } = req.query;
  let query = 'SELECT * FROM todos WHERE 1=1';
  const params = [];
  if (done !== undefined) { query += ' AND done = ?'; params.push(done === 'true' ? 1 : 0); }
  if (priority) { query += ' AND priority = ?'; params.push(priority); }
  if (q) { query += ' AND title LIKE ?'; params.push('%' + q + '%'); }
  query += ' ORDER BY id DESC';
  res.json({ count: db.prepare(query.replace('*', 'COUNT(*) as c')).get(...params).c, items: db.prepare(query).all(...params) });
});

app.post('/todos', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'missing_title' });
  const priority = ['low', 'medium', 'high'].includes(req.body.priority) ? req.body.priority : 'medium';
  const result = db.prepare('INSERT INTO todos (title, priority) VALUES (?, ?)').run(req.body.title, priority);
  res.status(201).json(db.prepare('SELECT * FROM todos WHERE id = ?').get(result.lastInsertRowid));
});

app.get('/todos/:id', (req, res) => {
  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(parseInt(req.params.id));
  todo ? res.json(todo) : res.status(404).json({ error: 'not_found' });
});

app.patch('/todos/:id', (req, res) => {
  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(parseInt(req.params.id));
  if (!todo) return res.status(404).json({ error: 'not_found' });
  const updates = [];
  const params = [];
  if (req.body.title !== undefined) { updates.push('title = ?'); params.push(req.body.title); }
  if (req.body.done !== undefined) { updates.push('done = ?'); params.push(req.body.done ? 1 : 0); }
  if (req.body.priority !== undefined) { updates.push('priority = ?'); params.push(req.body.priority); }
  if (!updates.length) return res.status(422).json({ error: 'no_updates' });
  params.push(parseInt(req.params.id));
  db.prepare(`UPDATE todos SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  res.json(db.prepare('SELECT * FROM todos WHERE id = ?').get(parseInt(req.params.id)));
});

app.delete('/todos/:id', (req, res) => {
  const result = db.prepare('DELETE FROM todos WHERE id = ?').run(parseInt(req.params.id));
  result.changes ? res.status(204).end() : res.status(404).json({ error: 'not_found' });
});

app.get('/stats', (req, res) => {
  const total = db.prepare('SELECT COUNT(*) as c FROM todos').get().c;
  const done = db.prepare('SELECT COUNT(*) as c FROM todos WHERE done = 1').get().c;
  const byPriority = db.prepare('SELECT priority, COUNT(*) as count FROM todos GROUP BY priority').all();
  res.json({ total, done, pending: total - done, byPriority });
});

app.listen(3000, () => console.log('Todo API :3000 — GET/POST/PATCH/DELETE /todos'));
module.exports = app;
