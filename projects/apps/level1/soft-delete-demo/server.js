// Soft Delete Demo — Mark as deleted, never remove, restore, filter on read.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE items (id TEXT PRIMARY KEY, name TEXT, deleted_at TEXT, deleted_by TEXT, created_at TEXT DEFAULT (datetime('now')))`);

// Seed
for (let i = 1; i <= 10; i++) {
  db.prepare('INSERT INTO items (id, name) VALUES (?, ?)').run('it_' + i, `Item ${i}`);
}
db.prepare('UPDATE items SET deleted_at = ?, deleted_by = ? WHERE id = ?').run(new Date().toISOString(), 'admin@x.com', 'it_3');
db.prepare('UPDATE items SET deleted_at = ?, deleted_by = ? WHERE id = ?').run(new Date().toISOString(), 'admin@x.com', 'it_7');

// === Soft delete helper ===
function softDelete(id, by = 'system') {
  const now = new Date().toISOString();
  const result = db.prepare('UPDATE items SET deleted_at = ?, deleted_by = ? WHERE id = ? AND deleted_at IS NULL').run(now, by, id);
  return result.changes > 0;
}

function restore(id) {
  const result = db.prepare('UPDATE items SET deleted_at = NULL, deleted_by = NULL WHERE id = ? AND deleted_at IS NOT NULL').run(id);
  return result.changes > 0;
}

function listActive() { return db.prepare('SELECT * FROM items WHERE deleted_at IS NULL ORDER BY id').all(); }
function listDeleted() { return db.prepare('SELECT * FROM items WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC').all(); }
function listAll() { return db.prepare('SELECT * FROM items ORDER BY id').all(); }

// === Endpoints ===
app.get('/items', (req, res) => {
  const includeDeleted = req.query.include_deleted === 'true';
  res.json({ items: includeDeleted ? listAll() : listActive() });
});

app.get('/items/deleted', (req, res) => res.json({ deleted: listDeleted() }));

app.get('/items/:id', (req, res) => {
  const item = db.prepare('SELECT * FROM items WHERE id = ?').get(req.params.id);
  if (!item) return res.status(404).json({ error: 'not_found' });
  if (item.deleted_at && req.query.include_deleted !== 'true') return res.status(410).json({ error: 'gone', deletedAt: item.deleted_at });
  res.json(item);
});

app.post('/items', (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'it_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO items (id, name) VALUES (?, ?)').run(id, req.body.name);
  res.status(201).json({ id, name: req.body.name });
});

app.delete('/items/:id', (req, res) => {
  const ok = softDelete(req.params.id, req.body?.deletedBy || 'system');
  ok ? res.json({ id: req.params.id, deleted: true }) : res.status(404).json({ error: 'not_found_or_already_deleted' });
});

app.post('/items/:id/restore', (req, res) => {
  const ok = restore(req.params.id);
  ok ? res.json({ id: req.params.id, restored: true }) : res.status(404).json({ error: 'not_found_or_not_deleted' });
});

app.delete('/items/:id/hard', (req, res) => {
  const result = db.prepare('DELETE FROM items WHERE id = ?').run(req.params.id);
  result.changes ? res.json({ id: req.params.id, hardDeleted: true }) : res.status(404).json({ error: 'not_found' });
});

app.listen(3000, () => console.log('Soft delete demo :3000 — GET /items, GET /items/deleted, POST /items/:id/restore, DELETE /items/:id/hard'));
module.exports = app;
