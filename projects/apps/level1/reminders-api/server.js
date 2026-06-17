// Reminders API — Step 9. Adds: scheduled tasks, time-based triggers, recurring reminders.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE reminders (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, notes TEXT, due_at TEXT, recurrence TEXT, completed INTEGER DEFAULT 0, completed_at TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE INDEX idx_reminders_user_due ON reminders(user_id, due_at)`);

app.get('/reminders', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { completed, due_before, due_after } = req.query;
  let query = 'SELECT * FROM reminders WHERE user_id = ?';
  const params = [req.userId];
  if (completed !== undefined) { query += ' AND completed = ?'; params.push(completed === 'true' ? 1 : 0); }
  if (due_before) { query += ' AND due_at < ?'; params.push(due_before); }
  if (due_after) { query += ' AND due_at > ?'; params.push(due_after); }
  query += ' ORDER BY due_at ASC';
  res.json({ reminders: db.prepare(query).all(...params) });
});

app.post('/reminders', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { title, notes, due_at, recurrence } = req.body;
  if (!title || !due_at) return res.status(422).json({ error: 'missing_fields' });
  const id = 'r_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO reminders (id, user_id, title, notes, due_at, recurrence) VALUES (?, ?, ?, ?, ?, ?)').run(id, req.userId, title, notes || '', due_at, recurrence || null);
  res.status(201).json(db.prepare('SELECT * FROM reminders WHERE id = ?').get(id));
});

app.patch('/reminders/:id/complete', (req, res) => {
  const reminder = db.prepare('SELECT * FROM reminders WHERE id = ?').get(req.params.id);
  if (!reminder) return res.status(404).json({ error: 'not_found' });
  db.prepare('UPDATE reminders SET completed = 1, completed_at = ? WHERE id = ?').run(new Date().toISOString(), req.params.id);
  // If recurring, create the next instance
  if (reminder.recurrence) {
    const interval = reminder.recurrence === 'daily' ? 86400000 : reminder.recurrence === 'weekly' ? 604800000 : 2592000000;
    const nextDue = new Date(new Date(reminder.due_at).getTime() + interval).toISOString();
    const nextId = 'r_' + crypto.randomBytes(4).toString('hex');
    db.prepare('INSERT INTO reminders (id, user_id, title, notes, due_at, recurrence) VALUES (?, ?, ?, ?, ?, ?)').run(nextId, reminder.user_id, reminder.title, reminder.notes, nextDue, reminder.recurrence);
    return res.json({ completed: reminder.id, next: nextId });
  }
  res.json({ completed: reminder.id });
});

// === "Now" endpoint: what should I be reminded of right now? ===
app.get('/reminders/now', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const window = parseInt(req.query.window) || 60; // next 60 minutes
  const now = new Date();
  const until = new Date(now.getTime() + window * 60000);
  const due = db.prepare('SELECT * FROM reminders WHERE user_id = ? AND completed = 0 AND due_at BETWEEN ? AND ? ORDER BY due_at ASC').all(req.userId, now.toISOString(), until.toISOString());
  const overdue = db.prepare('SELECT * FROM reminders WHERE user_id = ? AND completed = 0 AND due_at < ? ORDER BY due_at ASC').all(req.userId, now.toISOString());
  res.json({ now: now.toISOString(), due, overdue });
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Reminders API :3000 — X-User-Id header'));
module.exports = app;
