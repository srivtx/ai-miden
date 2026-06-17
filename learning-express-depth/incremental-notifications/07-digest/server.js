// 07-digest: Group notifications. Instead of 10 emails, send 1 daily digest.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE notifications (id TEXT PRIMARY KEY, user_id TEXT, type TEXT, title TEXT, body TEXT, delivered_at TEXT, created_at TEXT DEFAULT (datetime('now')))`);

const DIGEST_WINDOW_HOURS = 24;

// Queue a notification (don't send yet)
app.post('/notifications', (req, res) => {
  const { user_id, type, title, body } = req.body;
  if (!user_id || !title) return res.status(422).json({ error: 'user_id and title required' });
  const id = 'n_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO notifications (id, user_id, type, title, body) VALUES (?, ?, ?, ?, ?)').run(id, user_id, type, title, body || '');
  res.status(201).json({ id, queued: true });
});

// Build a digest for a user: all undelivered notifications in the window
app.get('/digest/:user_id', (req, res) => {
  const since = new Date(Date.now() - DIGEST_WINDOW_HOURS * 3600000).toISOString();
  const pending = db.prepare('SELECT * FROM notifications WHERE user_id = ? AND delivered_at IS NULL AND created_at > ? ORDER BY created_at').all(req.params.user_id, since);
  if (!pending.length) return res.json({ user_id: req.params.user_id, count: 0, items: [] });
  const summary = pending.map(n => `- [${n.type}] ${n.title}`).join('\n');
  res.json({
    user_id: req.params.user_id,
    count: pending.length,
    summary: `You have ${pending.length} new notifications:\n\n${summary}`,
    items: pending,
  });
});

// Send the digest (marks them delivered)
app.post('/digest/:user_id/send', (req, res) => {
  const since = new Date(Date.now() - DIGEST_WINDOW_HOURS * 3600000).toISOString();
  const r = db.prepare("UPDATE notifications SET delivered_at = datetime('now') WHERE user_id = ? AND delivered_at IS NULL AND created_at > ?").run(req.params.user_id, since);
  res.json({ delivered: r.changes });
});

app.listen(3000, () => console.log('07-digest on :3000 (24h window)'));
