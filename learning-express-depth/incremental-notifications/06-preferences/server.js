// 06-preferences: Per-user notification preferences. Each event_type can be sent via email/push/in_app.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE preferences (user_id TEXT, event_type TEXT, channel TEXT, enabled INTEGER DEFAULT 1, PRIMARY KEY (user_id, event_type, channel))`);

// Get a user's preferences (with defaults if not set)
app.get('/users/:id/preferences', (req, res) => {
  const prefs = db.prepare('SELECT * FROM preferences WHERE user_id = ?').all(req.params.id);
  // Default: all enabled for all channels
  if (!prefs.length) {
    return res.json({
      user_id: req.params.id,
      defaults: { email: true, push: true, in_app: true, sms: false },
    });
  }
  res.json({ user_id: req.params.id, preferences: prefs });
});

// Set a preference
app.put('/users/:id/preferences/:event_type/:channel', (req, res) => {
  const { enabled } = req.body;
  if (enabled === undefined) return res.status(422).json({ error: 'enabled required' });
  db.prepare('INSERT OR REPLACE INTO preferences VALUES (?, ?, ?, ?)').run(req.params.id, req.params.event_type, req.params.channel, enabled ? 1 : 0);
  res.json({ user_id: req.params.id, event_type: req.params.event_type, channel: req.params.channel, enabled });
});

// Should we send this notification? Check preferences
app.get('/should-send', (req, res) => {
  const { user_id, event_type, channel } = req.query;
  if (!user_id || !event_type || !channel) return res.status(422).json({ error: 'missing params' });
  const pref = db.prepare('SELECT enabled FROM preferences WHERE user_id = ? AND event_type = ? AND channel = ?').get(user_id, event_type, channel);
  const enabled = pref ? !!pref.enabled : true;  // default true
  res.json({ user_id, event_type, channel, should_send: enabled });
});

app.listen(3000, () => console.log('06-preferences on :3000'));
