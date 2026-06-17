// 04-sharing: Share files with other users. Permissions: read, write, owner.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE files (id TEXT PRIMARY KEY, owner_id TEXT, name TEXT);
  CREATE TABLE shares (file_id TEXT, user_id TEXT, permission TEXT CHECK(permission IN ('read', 'write')), created_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (file_id, user_id));
`);

function canAccess(fileId, userId, requiredPermission = 'read') {
  const file = db.prepare('SELECT * FROM files WHERE id = ?').get(fileId);
  if (!file) return { allowed: false, reason: 'not_found' };
  if (file.owner_id === userId) return { allowed: true, permission: 'owner' };
  const share = db.prepare('SELECT permission FROM shares WHERE file_id = ? AND user_id = ?').get(fileId, userId);
  if (!share) return { allowed: false, reason: 'no_access' };
  if (requiredPermission === 'write' && share.permission !== 'write') {
    return { allowed: false, reason: 'insufficient_permission' };
  }
  return { allowed: true, permission: share.permission };
}

// Create file (caller becomes owner)
app.post('/files', (req, res) => {
  const { name, owner_id } = req.body;
  if (!name || !owner_id) return res.status(422).json({ error: 'name and owner_id required' });
  const id = 'f_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO files VALUES (?, ?, ?)').run(id, owner_id, name);
  res.status(201).json({ id, owner_id, name });
});

// Share a file
app.post('/files/:id/shares', (req, res) => {
  const file = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  if (!file) return res.status(404).json({ error: 'not found' });
  if (file.owner_id !== req.body.user_id) return res.status(403).json({ error: 'only owner can share' });
  const { user_id, permission } = req.body;
  if (!['read', 'write'].includes(permission)) return res.status(422).json({ error: 'invalid permission' });
  db.prepare('INSERT OR REPLACE INTO shares VALUES (?, ?, ?, ?)').run(req.params.id, user_id, permission, new Date().toISOString());
  res.status(201).json({ shared: true });
});

// List shares
app.get('/files/:id/shares', (req, res) => {
  const shares = db.prepare('SELECT user_id, permission, created_at FROM shares WHERE file_id = ?').all(req.params.id);
  res.json({ file_id: req.params.id, shares });
});

// Access the file
app.get('/files/:id', (req, res) => {
  const access = canAccess(req.params.id, req.query.user_id);
  if (!access.allowed) return res.status(403).json({ error: access.reason });
  const file = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  res.json({ ...file, your_permission: access.permission });
});

app.listen(3000, () => console.log('04-sharing on :3000'));
