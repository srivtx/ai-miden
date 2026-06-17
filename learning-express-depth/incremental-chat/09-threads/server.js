// 09-threads: Reply to a message in a thread. The thread is a separate timeline.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id TEXT, user_id TEXT, text TEXT, parent_id INTEGER, thread_count INTEGER DEFAULT 0, latest_reply_at TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE INDEX idx_messages_parent ON messages(parent_id)`);

// Top-level message in a room
app.post('/rooms/:id/messages', (req, res) => {
  const { user_id, text } = req.body;
  if (!user_id || !text) return res.status(422).json({ error: 'user_id and text required' });
  const r = db.prepare('INSERT INTO messages (room_id, user_id, text) VALUES (?, ?, ?)').run(req.params.id, user_id, text);
  res.status(201).json(db.prepare('SELECT * FROM messages WHERE id = ?').get(r.lastInsertRowid));
});

// Reply in a thread
app.post('/messages/:id/replies', (req, res) => {
  const parentId = parseInt(req.params.id);
  const { user_id, text } = req.body;
  if (!user_id || !text) return res.status(422).json({ error: 'user_id and text required' });
  const parent = db.prepare('SELECT * FROM messages WHERE id = ?').get(parentId);
  if (!parent) return res.status(404).json({ error: 'parent message not found' });
  const r = db.prepare('INSERT INTO messages (room_id, user_id, text, parent_id) VALUES (?, ?, ?, ?)').run(parent.room_id, user_id, text, parentId);
  // Update parent's thread count
  db.prepare('UPDATE messages SET thread_count = thread_count + 1, latest_reply_at = datetime("now") WHERE id = ?').run(parentId);
  res.status(201).json(db.prepare('SELECT * FROM messages WHERE id = ?').get(r.lastInsertRowid));
});

// Get thread (all replies to a message)
app.get('/messages/:id/thread', (req, res) => {
  const parentId = parseInt(req.params.id);
  const parent = db.prepare('SELECT * FROM messages WHERE id = ?').get(parentId);
  if (!parent) return res.status(404).json({ error: 'not found' });
  const replies = db.prepare('SELECT * FROM messages WHERE parent_id = ? ORDER BY created_at ASC').all(parentId);
  res.json({ parent, count: replies.length, replies });
});

// Get top-level messages in a room (with thread counts)
app.get('/rooms/:id/messages', (req, res) => {
  const messages = db.prepare("SELECT * FROM messages WHERE room_id = ? AND parent_id IS NULL ORDER BY id DESC LIMIT 50").all(req.params.id);
  res.json({ room_id: req.params.id, messages: messages.reverse() });
});

app.listen(3000, () => console.log('09-threads on :3000'));
