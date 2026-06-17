// 03-users: User accounts with display names, avatars, status.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE, display_name TEXT, avatar_url TEXT, status TEXT DEFAULT 'active', created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id TEXT, user_id TEXT, text TEXT, created_at TEXT DEFAULT (datetime('now')));
`);

// Simple auth: just check X-User-Id header (in real apps: JWT or session)
function auth(req, res, next) {
  const userId = req.headers['x-user-id'];
  if (!userId) return res.status(401).json({ error: 'X-User-Id required' });
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
  if (!user) return res.status(401).json({ error: 'user not found' });
  req.user = user;
  next();
}

app.post('/users', (req, res) => {
  const { username, display_name, avatar_url } = req.body;
  if (!username) return res.status(422).json({ error: 'username required' });
  const id = 'u_' + crypto.randomBytes(4).toString('hex');
  try {
    db.prepare('INSERT INTO users (id, username, display_name, avatar_url) VALUES (?, ?, ?, ?)').run(id, username, display_name || username, avatar_url);
    res.status(201).json({ id, username, display_name: display_name || username, avatar_url });
  } catch { res.status(409).json({ error: 'username taken' }); }
});

app.get('/users/:id', (req, res) => {
  const user = db.prepare('SELECT id, username, display_name, avatar_url, status, created_at FROM users WHERE id = ?').get(req.params.id);
  user ? res.json(user) : res.status(404).json({ error: 'not found' });
});

app.get('/users', (req, res) => res.json({ users: db.prepare('SELECT id, username, display_name, avatar_url FROM users').all() }));

// Post a message as the authenticated user
app.post('/rooms/:id/messages', auth, (req, res) => {
  const { text } = req.body;
  if (!text) return res.status(422).json({ error: 'text required' });
  const r = db.prepare('INSERT INTO messages (room_id, user_id, text) VALUES (?, ?, ?)').run(req.params.id, req.user.id, text);
  res.status(201).json(db.prepare('SELECT * FROM messages WHERE id = ?').get(r.lastInsertRowid));
});

// Get messages with user info
app.get('/rooms/:id/messages', (req, res) => {
  const messages = db.prepare(`
    SELECT m.*, u.username, u.display_name, u.avatar_url
    FROM messages m JOIN users u ON u.id = m.user_id
    WHERE m.room_id = ?
    ORDER BY m.id DESC LIMIT 50
  `).all(req.params.id);
  res.json({ room_id: req.params.id, messages: messages.reverse() });
});

app.listen(3000, () => console.log('03-users on :3000 (use X-User-Id header)'));
