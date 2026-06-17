// 10-quotas: Per-user storage limits. Check before upload, reject if over quota.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT, quota_bytes INTEGER DEFAULT 1073741824)`);  // 1GB default
db.exec(`CREATE TABLE files (id TEXT PRIMARY KEY, user_id TEXT, name TEXT, size_bytes INTEGER)`);

function getUserUsage(userId) {
  const used = db.prepare('SELECT COALESCE(SUM(size_bytes), 0) as used FROM files WHERE user_id = ?').get(userId).used;
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
  return { used, quota: user?.quota_bytes || 0 };
}

app.post('/files', (req, res) => {
  const { name, size_bytes, user_id } = req.body;
  if (!name || !user_id || !size_bytes) return res.status(422).json({ error: 'name, size_bytes, user_id required' });
  const { used, quota } = getUserUsage(user_id);
  if (used + size_bytes > quota) {
    return res.status(413).json({ error: 'quota_exceeded', used, quota, requested: size_bytes, available: quota - used });
  }
  const id = 'f_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO files VALUES (?, ?, ?, ?)').run(id, user_id, name, size_bytes);
  res.status(201).json({ id, used_after: used + size_bytes, quota_remaining: quota - used - size_bytes });
});

app.get('/users/:id/quota', (req, res) => {
  const { used, quota } = getUserUsage(req.params.id);
  res.json({ user_id: req.params.id, used, quota, available: quota - used, percent_used: Math.round(used / quota * 1000) / 10 });
});

app.patch('/users/:id/quota', (req, res) => {
  const { quota_bytes } = req.body;
  if (quota_bytes === undefined) return res.status(422).json({ error: 'quota_bytes required' });
  const r = db.prepare('UPDATE users SET quota_bytes = ? WHERE id = ?').run(quota_bytes, req.params.id);
  r.changes ? res.json({ quota_bytes }) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('10-quotas on :3000 (default 1GB per user)'));
