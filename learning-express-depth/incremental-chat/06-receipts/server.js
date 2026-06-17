// 06-receipts: Read receipts. Mark messages as read. See who has read what.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id TEXT, user_id TEXT, text TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE read_receipts (user_id TEXT, message_id INTEGER, read_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (user_id, message_id))`);

// Mark a message (or all messages in a room) as read
app.post('/read', (req, res) => {
  const { user_id, room_id, message_id, up_to } = req.body;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  if (message_id) {
    // Mark a specific message as read
    db.prepare('INSERT OR IGNORE INTO read_receipts (user_id, message_id) VALUES (?, ?)').run(user_id, message_id);
    return res.json({ read: true });
  }
  if (room_id && up_to) {
    // Mark all messages in a room up to a certain message as read
    const messages = db.prepare('SELECT id FROM messages WHERE room_id = ? AND id <= ?').all(room_id, up_to);
    for (const m of messages) {
      db.prepare('INSERT OR IGNORE INTO read_receipts (user_id, message_id) VALUES (?, ?)').run(user_id, m.id);
    }
    return res.json({ read: true, count: messages.length });
  }
  res.status(422).json({ error: 'message_id or room_id+up_to required' });
});

// Unread count for a user in a room
app.get('/rooms/:id/unread', (req, res) => {
  const userId = req.query.user_id;
  if (!userId) return res.status(422).json({ error: 'user_id required' });
  const count = db.prepare(`
    SELECT COUNT(*) as c FROM messages m
    WHERE m.room_id = ? AND m.user_id != ? AND m.id NOT IN (SELECT message_id FROM read_receipts WHERE user_id = ?)
  `).get(req.params.id, userId, userId).c;
  res.json({ room_id: req.params.id, user_id: userId, unread: count });
});

// Who has read a specific message
app.get('/messages/:id/receipts', (req, res) => {
  const receipts = db.prepare(`
    SELECT r.user_id, r.read_at, u.username, u.display_name
    FROM read_receipts r JOIN users u ON u.id = r.user_id
    WHERE r.message_id = ?
    ORDER BY r.read_at
  `).all(parseInt(req.params.id));
  res.json({ message_id: parseInt(req.params.id), count: receipts.length, receipts });
});

app.listen(3000, () => console.log('06-receipts on :3000'));
