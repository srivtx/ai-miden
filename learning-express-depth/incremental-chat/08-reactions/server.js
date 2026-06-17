// 08-reactions: Emoji reactions on messages. Add, remove, count.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id TEXT, user_id TEXT, text TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE reactions (message_id INTEGER, user_id TEXT, emoji TEXT, created_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (message_id, user_id, emoji))`);

const ALLOWED_EMOJI = ['👍', '❤️', '😂', '🎉', '😮', '😢', '🔥', '👏'];

// Add a reaction (or do nothing if already there)
app.post('/messages/:id/reactions', (req, res) => {
  const messageId = parseInt(req.params.id);
  const { user_id, emoji } = req.body;
  if (!user_id || !emoji) return res.status(422).json({ error: 'user_id and emoji required' });
  if (!ALLOWED_EMOJI.includes(emoji)) return res.status(422).json({ error: 'emoji not allowed', allowed: ALLOWED_EMOJI });
  const message = db.prepare('SELECT * FROM messages WHERE id = ?').get(messageId);
  if (!message) return res.status(404).json({ error: 'message not found' });
  try {
    db.prepare('INSERT INTO reactions (message_id, user_id, emoji) VALUES (?, ?, ?)').run(messageId, user_id, emoji);
    res.status(201).json({ reacted: true });
  } catch {
    res.json({ reacted: false, reason: 'already reacted' });
  }
});

// Remove a reaction
app.delete('/messages/:id/reactions', (req, res) => {
  const messageId = parseInt(req.params.id);
  const { user_id, emoji } = req.body;
  const r = db.prepare('DELETE FROM reactions WHERE message_id = ? AND user_id = ? AND emoji = ?').run(messageId, user_id, emoji);
  r.changes ? res.json({ removed: true }) : res.status(404).json({ error: 'reaction not found' });
});

// Get reactions for a message
app.get('/messages/:id/reactions', (req, res) => {
  const messageId = parseInt(req.params.id);
  // Group by emoji, count users
  const reactions = db.prepare(`
    SELECT emoji, COUNT(*) as count, GROUP_CONCAT(user_id) as users
    FROM reactions WHERE message_id = ?
    GROUP BY emoji
  `).all(messageId);
  res.json({ message_id: messageId, reactions });
});

// Get messages in a room with their reactions
app.get('/rooms/:id/messages', (req, res) => {
  const messages = db.prepare('SELECT * FROM messages WHERE room_id = ? ORDER BY id DESC LIMIT 50').all(req.params.id);
  for (const m of messages) {
    const reactions = db.prepare(`
      SELECT emoji, COUNT(*) as count FROM reactions WHERE message_id = ? GROUP BY emoji
    `).all(m.id);
    m.reactions = reactions;
  }
  res.json({ room_id: req.params.id, messages: messages.reverse() });
});

app.listen(3000, () => console.log('08-reactions on :3000'));
