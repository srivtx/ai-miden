// 05-typing: "Alice is typing..." indicators. Ephemeral — auto-clears after 5 seconds.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE typing_indicators (room_id TEXT, user_id TEXT, started_at TEXT, PRIMARY KEY (room_id, user_id))`);

const TYPING_TIMEOUT_MS = 5 * 1000;

// User starts typing in a room
app.post('/rooms/:id/typing', (req, res) => {
  const { user_id } = req.body;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  db.prepare('INSERT OR REPLACE INTO typing_indicators (room_id, user_id, started_at) VALUES (?, ?, datetime("now"))').run(req.params.id, user_id);
  res.json({ typing: true });
});

// User stops typing
app.delete('/rooms/:id/typing', (req, res) => {
  const userId = req.body.user_id || req.query.user_id;
  if (userId) db.prepare('DELETE FROM typing_indicators WHERE room_id = ? AND user_id = ?').run(req.params.id, userId);
  res.json({ typing: false });
});

// Who's currently typing (only fresh ones, within timeout)
app.get('/rooms/:id/typing', (req, res) => {
  const cutoff = new Date(Date.now() - TYPING_TIMEOUT_MS).toISOString();
  const typing = db.prepare('SELECT user_id, started_at FROM typing_indicators WHERE room_id = ? AND started_at > ?').all(req.params.id, cutoff);
  res.json({ room_id: req.params.id, count: typing.length, typing });
});

// Background cleanup: every 10s, remove old indicators
setInterval(() => {
  const cutoff = new Date(Date.now() - TYPING_TIMEOUT_MS).toISOString();
  db.prepare('DELETE FROM typing_indicators WHERE started_at < ?').run(cutoff);
}, 10000);

app.listen(3000, () => console.log('05-typing on :3000 (auto-clears after 5s)'));
