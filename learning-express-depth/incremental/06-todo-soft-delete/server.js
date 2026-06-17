// 06-todo-soft-delete: Never actually delete. Mark with deleted_at, restore, list trash.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0, deleted_at TEXT, deleted_by TEXT, created_at TEXT DEFAULT (datetime('now')))`);

function softDelete(id, by = 'system') {
  const now = new Date().toISOString();
  const r = db.prepare('UPDATE todos SET deleted_at = ?, deleted_by = ? WHERE id = ? AND deleted_at IS NULL').run(now, by, id);
  return r.changes > 0;
}
function restore(id) {
  const r = db.prepare('UPDATE todos SET deleted_at = NULL, deleted_by = NULL WHERE id = ? AND deleted_at IS NOT NULL').run(id);
  return r.changes > 0;
}

// All list queries filter out soft-deleted
app.get('/todos', (req, res) => {
  const items = db.prepare('SELECT * FROM todos WHERE deleted_at IS NULL ORDER BY id DESC').all();
  res.json({ count: items.length, todos: items });
});

// See the trash
app.get('/todos/trash', (req, res) => {
  const items = db.prepare('SELECT * FROM todos WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC').all();
  res.json({ count: items.length, todos: items });
});

app.post('/todos', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const r = db.prepare('INSERT INTO todos (title) VALUES (?)').run(req.body.title);
  res.status(201).json(db.prepare('SELECT * FROM todos WHERE id = ?').get(r.lastInsertRowid));
});

// Soft delete
app.delete('/todos/:id', (req, res) => {
  softDelete(parseInt(req.params.id), req.body?.deletedBy)
    ? res.json({ deleted: true })
    : res.status(404).json({ error: 'not found or already deleted' });
});

// Restore
app.post('/todos/:id/restore', (req, res) => {
  restore(parseInt(req.params.id))
    ? res.json({ restored: true })
    : res.status(404).json({ error: 'not found or not deleted' });
});

// Hard delete (permanent — use carefully)
app.delete('/todos/:id/hard', (req, res) => {
  const r = db.prepare('DELETE FROM todos WHERE id = ?').run(parseInt(req.params.id));
  r.changes ? res.status(204).end() : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('06-todo-soft-delete on :3000'));
