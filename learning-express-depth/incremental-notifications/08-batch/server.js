// 08-batch: Group sends. Send to 1000 users efficiently. Bulk endpoints.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT, segment TEXT)`);
db.exec(`CREATE TABLE notifications (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, body TEXT, status TEXT DEFAULT 'queued', created_at TEXT DEFAULT (datetime('now')))`);

// Seed 100 users
for (let i = 0; i < 100; i++) {
  const segment = i % 3 === 0 ? 'premium' : 'free';
  db.prepare('INSERT INTO users VALUES (?, ?, ?)').run(`u_${i}`, `u${i}@example.com`, segment);
}

// Bulk send to all users in a segment
app.post('/broadcast', (req, res) => {
  const { segment, title, body } = req.body;
  if (!segment || !title) return res.status(422).json({ error: 'segment and title required' });
  const users = db.prepare('SELECT id FROM users WHERE segment = ?').all(segment);
  const stmt = db.prepare('INSERT INTO notifications (user_id, title, body) VALUES (?, ?, ?)');
  for (const u of users) stmt.run(u.id, title, body || '');
  res.status(202).json({ sent_to: users.length });
});

// Bulk send to a list of user_ids
app.post('/bulk', (req, res) => {
  const { user_ids, title, body } = req.body;
  if (!Array.isArray(user_ids) || !title) return res.status(422).json({ error: 'user_ids array and title required' });
  const stmt = db.prepare('INSERT INTO notifications (user_id, title, body) VALUES (?, ?, ?)');
  for (const id of user_ids) stmt.run(id, title, body || '');
  res.status(202).json({ sent_to: user_ids.length });
});

app.listen(3000, () => console.log('08-broadcast on :3000 (100 users seeded)'));
