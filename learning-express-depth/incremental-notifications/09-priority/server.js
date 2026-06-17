// 09-priority: Priority levels. Critical = immediate. Low = batch.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE notifications (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, priority TEXT DEFAULT 'normal', status TEXT DEFAULT 'queued', sent_at TEXT, created_at TEXT DEFAULT (datetime('now')))`);

const PRIORITIES = ['critical', 'high', 'normal', 'low'];

// Send: critical goes immediately, low waits
app.post('/notifications', (req, res) => {
  const { user_id, title, priority = 'normal' } = req.body;
  if (!user_id || !title) return res.status(422).json({ error: 'user_id and title required' });
  if (!PRIORITIES.includes(priority)) return res.status(422).json({ error: 'invalid priority', allowed: PRIORITIES });
  const id = 'n_' + Math.random().toString(36).slice(2, 10);
  db.prepare("INSERT INTO notifications (id, user_id, title, priority, status) VALUES (?, ?, ?, ?, 'queued')").run(id, user_id, title, priority);

  // Critical and high: send immediately
  if (priority === 'critical' || priority === 'high') {
    setImmediate(() => {
      db.prepare("UPDATE notifications SET status = 'sent', sent_at = datetime('now') WHERE id = ?").run(id);
      console.log(`[urgent] sent ${priority}: ${title}`);
    });
    res.status(202).json({ id, priority, status: 'sending' });
  } else {
    // Normal and low: queue for batch processing
    res.status(202).json({ id, priority, status: 'queued' });
  }
});

// Process the queue (called by cron every minute for high-priority items)
app.post('/process-queue', (req, res) => {
  // Send high (not yet sent) and normal
  const pending = db.prepare("SELECT * FROM notifications WHERE status = 'queued' AND priority IN ('high', 'normal') ORDER BY priority, created_at").all();
  for (const n of pending) {
    db.prepare("UPDATE notifications SET status = 'sent', sent_at = datetime('now') WHERE id = ?").run(n.id);
  }
  res.json({ processed: pending.length });
});

app.get('/notifications/:id', (req, res) => {
  const n = db.prepare('SELECT * FROM notifications WHERE id = ?').get(req.params.id);
  n ? res.json(n) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('09-priority on :3000 (critical=immediate, low=batched)'));
