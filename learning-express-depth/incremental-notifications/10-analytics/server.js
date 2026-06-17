// 10-analytics: Track notification delivery, opens, clicks. Per-channel rates.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE notifications (id TEXT PRIMARY KEY, channel TEXT, sent_at TEXT, delivered_at TEXT, opened_at TEXT, clicked_at TEXT)`);

app.post('/notifications/:id/delivered', (req, res) => {
  const r = db.prepare("UPDATE notifications SET delivered_at = datetime('now') WHERE id = ?").run(req.params.id);
  r.changes ? res.json({ delivered: true }) : res.status(404).json({ error: 'not found' });
});

app.post('/notifications/:id/opened', (req, res) => {
  const r = db.prepare("UPDATE notifications SET opened_at = datetime('now') WHERE id = ?").run(req.params.id);
  r.changes ? res.json({ opened: true }) : res.status(404).json({ error: 'not found' });
});

app.post('/notifications/:id/clicked', (req, res) => {
  const r = db.prepare("UPDATE notifications SET clicked_at = datetime('now') WHERE id = ?").run(req.params.id);
  r.changes ? res.json({ clicked: true }) : res.status(404).json({ error: 'not found' });
});

// Per-channel rates
app.get('/analytics/channels', (req, res) => {
  const since = req.query.since || new Date(Date.now() - 30 * 86400000).toISOString();
  const stats = db.prepare(`
    SELECT
      channel,
      COUNT(*) as sent,
      COUNT(delivered_at) as delivered,
      COUNT(opened_at) as opened,
      COUNT(clicked_at) as clicked,
      ROUND(100.0 * COUNT(delivered_at) / COUNT(*), 1) as delivery_rate,
      ROUND(100.0 * COUNT(opened_at) / COUNT(*), 1) as open_rate,
      ROUND(100.0 * COUNT(clicked_at) / COUNT(*), 1) as click_rate
    FROM notifications
    WHERE sent_at > ?
    GROUP BY channel
  `).all(since);
  res.json({ since, channels: stats });
});

app.listen(3000, () => console.log('10-analytics on :3000'));
