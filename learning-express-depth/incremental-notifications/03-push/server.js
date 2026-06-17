// 03-push: Push notifications to mobile. Register device, send notification.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE devices (id TEXT PRIMARY KEY, user_id TEXT, platform TEXT, token TEXT, registered_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE push_notifications (id TEXT PRIMARY KEY, device_id TEXT, title TEXT, body TEXT, data TEXT, status TEXT DEFAULT 'queued', created_at TEXT DEFAULT (datetime('now')))`);

// Register a device
app.post('/devices', (req, res) => {
  const { user_id, platform, token } = req.body;
  if (!user_id || !platform || !token) return res.status(422).json({ error: 'user_id, platform, token required' });
  const id = 'd_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO devices VALUES (?, ?, ?, ?, ?)').run(id, user_id, platform, token, new Date().toISOString());
  res.status(201).json({ id, user_id, platform });
});

// Send a push to all of a user's devices
app.post('/push', (req, res) => {
  const { user_id, title, body, data } = req.body;
  if (!user_id || !title) return res.status(422).json({ error: 'user_id and title required' });
  const devices = db.prepare('SELECT * FROM devices WHERE user_id = ?').all(user_id);
  if (!devices.length) return res.status(404).json({ error: 'no devices registered' });
  for (const d of devices) {
    const id = 'pn_' + Math.random().toString(36).slice(2, 10);
    db.prepare("INSERT INTO push_notifications (id, device_id, title, body, data) VALUES (?, ?, ?, ?, ?)").run(id, d.id, title, body || '', JSON.stringify(data || {}));
    setImmediate(() => {
      db.prepare("UPDATE push_notifications SET status = 'sent' WHERE id = ?").run(id);
      console.log(`[push] sent to ${d.platform}: ${title}`);
    });
  }
  res.status(202).json({ sent_to: devices.length });
});

app.get('/devices', (req, res) => res.json({ devices: db.prepare('SELECT * FROM devices').all() }));

app.listen(3000, () => console.log('03-push on :3000'));
