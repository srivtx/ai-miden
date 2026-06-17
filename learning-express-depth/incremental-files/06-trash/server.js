// 06-trash: Soft delete. Files go to trash, can be restored, auto-purged after 30 days.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE files (id TEXT PRIMARY KEY, name TEXT, owner_id TEXT, deleted_at TEXT, deleted_by TEXT)`);

const TRASH_TTL_DAYS = 30;

// Soft delete
app.delete('/files/:id', (req, res) => {
  const file = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  if (!file) return res.status(404).json({ error: 'not found' });
  if (file.deleted_at) return res.json({ already_deleted: true });
  const now = new Date().toISOString();
  db.prepare('UPDATE files SET deleted_at = ?, deleted_by = ? WHERE id = ?').run(now, req.body.deleted_by, file.id);
  res.json({ deleted: true, deleted_at: now, purge_after: new Date(Date.now() + TRASH_TTL_DAYS * 86400000).toISOString() });
});

// List trash
app.get('/trash', (req, res) => {
  const trash = db.prepare('SELECT * FROM files WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC').all();
  res.json({ count: trash.length, items: trash });
});

// Restore from trash
app.post('/files/:id/restore', (req, res) => {
  const file = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  if (!file) return res.status(404).json({ error: 'not found' });
  if (!file.deleted_at) return res.status(409).json({ error: 'not in trash' });
  db.prepare('UPDATE files SET deleted_at = NULL, deleted_by = NULL WHERE id = ?').run(file.id);
  res.json({ restored: true });
});

// Purge (permanent delete)
app.delete('/files/:id/purge', (req, res) => {
  const file = db.prepare('SELECT * FROM files WHERE id = ? AND deleted_at IS NOT NULL').get(req.params.id);
  if (!file) return res.status(404).json({ error: 'not in trash' });
  db.prepare('DELETE FROM files WHERE id = ?').run(req.params.id);
  res.status(204).end();
});

// Auto-purge: every hour, remove files in trash for > 30 days
setInterval(() => {
  const cutoff = new Date(Date.now() - TRASH_TTL_DAYS * 86400000).toISOString();
  const purged = db.prepare('DELETE FROM files WHERE deleted_at IS NOT NULL AND deleted_at < ?').run(cutoff).changes;
  if (purged) console.log(`[trash] purged ${purged} old files`);
}, 60 * 60 * 1000);

app.listen(3000, () => console.log('06-trash on :3000 (auto-purge after 30 days)'));
