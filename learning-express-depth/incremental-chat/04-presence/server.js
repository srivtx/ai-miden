// 04-presence: Track who's online. Heartbeat from the client, "last seen" on the server.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE, display_name TEXT)`);
db.exec(`CREATE TABLE presence (user_id TEXT PRIMARY KEY, last_seen_at TEXT, status TEXT DEFAULT 'online')`);

const ONLINE_TIMEOUT_MS = 30 * 1000;  // 30 seconds

// Mark user as online (called by client every 10-30 seconds)
app.post('/presence/heartbeat', (req, res) => {
  const userId = req.body.user_id;
  if (!userId) return res.status(422).json({ error: 'user_id required' });
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
  if (!user) return res.status(404).json({ error: 'user not found' });
  db.prepare(`INSERT INTO presence (user_id, last_seen_at, status) VALUES (?, datetime('now'), 'online') ON CONFLICT(user_id) DO UPDATE SET last_seen_at = datetime('now'), status = 'online'`).run(userId);
  res.json({ user_id: userId, status: 'online' });
});

// Explicitly go offline
app.post('/presence/offline', (req, res) => {
  const userId = req.body.user_id;
  if (!userId) return res.status(422).json({ error: 'user_id required' });
  db.prepare("UPDATE presence SET status = 'offline' WHERE user_id = ?").run(userId);
  res.json({ user_id: userId, status: 'offline' });
});

// Who's online?
app.get('/presence', (req, res) => {
  const cutoff = new Date(Date.now() - ONLINE_TIMEOUT_MS).toISOString();
  const online = db.prepare(`
    SELECT u.id, u.username, u.display_name, p.last_seen_at, p.status
    FROM users u JOIN presence p ON p.user_id = u.id
    WHERE p.status = 'online' AND p.last_seen_at > ?
    ORDER BY p.last_seen_at DESC
  `).all(cutoff);
  res.json({ count: online.length, online });
});

// Who's in a specific room?
app.get('/rooms/:id/presence', (req, res) => {
  // In a real app, this would track which users are subscribed to room events
  const cutoff = new Date(Date.now() - ONLINE_TIMEOUT_MS).toISOString();
  const online = db.prepare(`
    SELECT u.id, u.username, u.display_name FROM users u JOIN presence p ON p.user_id = u.id
    WHERE p.status = 'online' AND p.last_seen_at > ?
  `).all(cutoff);
  res.json({ room_id: req.params.id, count: online.length, online });
});

app.listen(3000, () => console.log('04-presence on :3000 (heartbeat every 30s)'));
