// 04-in-app: In-app notifications. Inbox, unread count, mark as read.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE notifications (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, body TEXT, link TEXT, read_at TEXT, created_at TEXT DEFAULT (datetime('now')))`);

// Send a notification to a user
app.post('/notifications', (req, res) => {
  const { user_id, title, body, link } = req.body;
  if (!user_id || !title) return res.status(422).json({ error: 'user_id and title required' });
  const id = 'n_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO notifications (id, user_id, title, body, link) VALUES (?, ?, ?, ?, ?)').run(id, user_id, title, body || '', link || null);
  res.status(201).json({ id });
});

// Get the user's inbox
app.get('/notifications', (req, res) => {
  const { user_id, unread } = req.query;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  let query = 'SELECT * FROM notifications WHERE user_id = ?';
  const params = [user_id];
  if (unread === 'true') { query += ' AND read_at IS NULL'; }
  query += ' ORDER BY created_at DESC LIMIT 50';
  res.json({ notifications: db.prepare(query).all(...params) });
});

// Unread count
app.get('/notifications/unread-count', (req, res) => {
  const { user_id } = req.query;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  const count = db.prepare('SELECT COUNT(*) as c FROM notifications WHERE user_id = ? AND read_at IS NULL').get(user_id).c;
  res.json({ user_id, unread: count });
});

// Mark as read
app.post('/notifications/:id/read', (req, res) => {
  const r = db.prepare('UPDATE notifications SET read_at = datetime("now") WHERE id = ?').run(req.params.id);
  r.changes ? res.json({ read: true }) : res.status(404).json({ error: 'not found' });
});

// Mark all as read
app.post('/notifications/read-all', (req, res) => {
  const { user_id } = req.body;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  const r = db.prepare('UPDATE notifications SET read_at = datetime("now") WHERE user_id = ? AND read_at IS NULL').run(user_id);
  res.json({ marked: r.changes });
});

app.listen(3000, () => console.log('04-in-app on :3000'));
