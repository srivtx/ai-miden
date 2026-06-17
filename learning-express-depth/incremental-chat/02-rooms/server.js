// 02-rooms: Multiple rooms. Each room has its own messages.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE rooms (id TEXT PRIMARY KEY, name TEXT, is_private INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id TEXT NOT NULL, sender TEXT, text TEXT, created_at TEXT DEFAULT (datetime('now')));
  CREATE INDEX idx_messages_room ON messages(room_id, id DESC);
`);

function getOrCreateRoom(roomId) {
  let room = db.prepare('SELECT * FROM rooms WHERE id = ?').get(roomId);
  if (!room) {
    db.prepare('INSERT INTO rooms (id, name) VALUES (?, ?)').run(roomId, roomId);
    room = { id: roomId, name: roomId };
  }
  return room;
}

app.get('/rooms', (req, res) => res.json({ rooms: db.prepare('SELECT * FROM rooms').all() }));

app.post('/rooms', (req, res) => {
  const { name, is_private } = req.body;
  if (!name) return res.status(422).json({ error: 'name required' });
  const id = 'r_' + name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  if (db.prepare('SELECT id FROM rooms WHERE id = ?').get(id)) return res.status(409).json({ error: 'room exists' });
  db.prepare('INSERT INTO rooms (id, name, is_private) VALUES (?, ?, ?)').run(id, name, is_private ? 1 : 0);
  res.status(201).json({ id, name });
});

// Get messages for a room
app.get('/rooms/:id/messages', (req, res) => {
  getOrCreateRoom(req.params.id);
  const limit = Math.min(100, parseInt(req.query.limit) || 50);
  const before = req.query.before ? parseInt(req.query.before) : null;
  let query = 'SELECT * FROM messages WHERE room_id = ?';
  const params = [req.params.id];
  if (before) { query += ' AND id < ?'; params.push(before); }
  query += ' ORDER BY id DESC LIMIT ?';
  params.push(limit);
  res.json({ room_id: req.params.id, messages: db.prepare(query).all(...params).reverse() });
});

// Post to a room
app.post('/rooms/:id/messages', (req, res) => {
  getOrCreateRoom(req.params.id);
  const { sender, text } = req.body;
  if (!sender || !text) return res.status(422).json({ error: 'sender and text required' });
  const r = db.prepare('INSERT INTO messages (room_id, sender, text) VALUES (?, ?, ?)').run(req.params.id, sender, text);
  res.status(201).json(db.prepare('SELECT * FROM messages WHERE id = ?').get(r.lastInsertRowid));
});

app.listen(3000, () => console.log('02-rooms on :3000'));
