// 10-notifications: Notify users when something happens. Mention, reply, reaction.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE)`);
db.exec(`CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id TEXT, user_id TEXT, text TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, type TEXT, message TEXT, source_id TEXT, source_user_id TEXT, read_at TEXT, created_at TEXT DEFAULT (datetime('now')))`);

// Detect @mentions in message text (matches @username)
function detectMentions(text) {
  const matches = text.match(/@(\w+)/g) || [];
  return matches.map(m => m.slice(1).toLowerCase());
}

// Send a message — creates notifications for mentions
app.post('/rooms/:id/messages', (req, res) => {
  const { user_id, text } = req.body;
  if (!user_id || !text) return res.status(422).json({ error: 'user_id and text required' });
  const r = db.prepare('INSERT INTO messages (room_id, user_id, text) VALUES (?, ?, ?)').run(req.params.id, user_id, text);
  const message = db.prepare('SELECT * FROM messages WHERE id = ?').get(r.lastInsertRowid);

  // Create mention notifications
  const mentions = detectMentions(text);
  for (const username of mentions) {
    const user = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
    if (user && user.id !== user_id) {
      db.prepare('INSERT INTO notifications (user_id, type, message, source_id, source_user_id) VALUES (?, ?, ?, ?, ?)').run(user.id, 'mention', `${req.headers['x-username'] || user_id} mentioned you`, message.id, user_id);
    }
  }
  res.status(201).json(message);
});

// Reply notification (when someone replies to your message)
app.post('/messages/:id/replies', (req, res) => {
  const parentId = parseInt(req.params.id);
  const { user_id, text } = req.body;
  const parent = db.prepare('SELECT * FROM messages WHERE id = ?').get(parentId);
  if (!parent) return res.status(404).json({ error: 'not found' });
  if (parent.user_id !== user_id) {
    db.prepare('INSERT INTO notifications (user_id, type, message, source_id, source_user_id) VALUES (?, ?, ?, ?, ?)').run(parent.user_id, 'reply', `${user_id} replied to your message`, parentId, user_id);
  }
  const r = db.prepare('INSERT INTO messages (room_id, user_id, text, parent_id) VALUES (?, ?, ?, ?)').run(parent.room_id, user_id, text, parentId);
  res.status(201).json(db.prepare('SELECT * FROM messages WHERE id = ?').get(r.lastInsertRowid));
});

// Get notifications for a user
app.get('/notifications', (req, res) => {
  const userId = req.query.user_id;
  if (!userId) return res.status(422).json({ error: 'user_id required' });
  const unread = db.prepare('SELECT * FROM notifications WHERE user_id = ? AND read_at IS NULL ORDER BY created_at DESC').all(userId);
  const all = db.prepare('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50').all(userId);
  res.json({ user_id: userId, unread_count: unread.length, total: all.length, notifications: all });
});

// Mark notifications as read
app.post('/notifications/read', (req, res) => {
  const { user_id, ids } = req.body;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  if (ids && ids.length) {
    const placeholders = ids.map(() => '?').join(',');
    db.prepare(`UPDATE notifications SET read_at = datetime('now') WHERE user_id = ? AND id IN (${placeholders})`).run(user_id, ...ids);
  } else {
    db.prepare("UPDATE notifications SET read_at = datetime('now') WHERE user_id = ? AND read_at IS NULL").run(user_id);
  }
  res.json({ marked_read: true });
});

app.listen(3000, () => console.log('10-notifications on :3000'));
