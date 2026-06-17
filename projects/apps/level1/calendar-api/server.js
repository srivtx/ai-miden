// Calendar API — Step 8. Adds: events, time slots, recurring, attendees, conflict detection.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE events (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, description TEXT, start_at TEXT, end_at TEXT, all_day INTEGER DEFAULT 0, recurrence TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE attendees (event_id TEXT, user_email TEXT, status TEXT DEFAULT 'pending', PRIMARY KEY (event_id, user_email))`);
db.exec(`CREATE INDEX idx_events_user_time ON events(user_id, start_at)`);

// === Recurrence helper (RRULE subset: daily, weekly, monthly) ===
function expandRecurrence(event, fromDate, toDate) {
  if (!event.recurrence) return [event];
  const occurrences = [event];
  const start = new Date(event.start_at);
  const end = new Date(event.end_at);
  const duration = end - start;
  const rule = event.recurrence; // "daily", "weekly", "monthly"
  const interval = rule === 'daily' ? 86400000 : rule === 'weekly' ? 604800000 : 2592000000;
  let current = new Date(start.getTime() + interval);
  while (current <= toDate) {
    if (current >= fromDate) {
      const occ = { ...event, id: event.id + '_' + current.getTime(), start_at: current.toISOString(), end_at: new Date(current.getTime() + duration).toISOString() };
      occurrences.push(occ);
    }
    current = new Date(current.getTime() + interval);
  }
  return occurrences;
}

app.get('/events', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const from = req.query.from ? new Date(req.query.from) : new Date();
  const to = req.query.to ? new Date(req.query.to) : new Date(Date.now() + 30 * 86400000);
  const events = db.prepare('SELECT * FROM events WHERE user_id = ? AND start_at < ? AND (end_at > ? OR recurrence IS NOT NULL)').all(req.userId, to.toISOString(), from.toISOString());
  const expanded = events.flatMap(e => expandRecurrence(e, from, to));
  res.json({ from: from.toISOString(), to: to.toISOString(), count: expanded.length, events: expanded });
});

app.post('/events', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { title, description, start_at, end_at, all_day, recurrence, attendees } = req.body;
  if (!title || !start_at || !end_at) return res.status(422).json({ error: 'missing_fields' });
  const id = 'e_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO events (id, user_id, title, description, start_at, end_at, all_day, recurrence) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(id, req.userId, title, description || '', start_at, end_at, all_day ? 1 : 0, recurrence || null);
  if (Array.isArray(attendees)) {
    for (const email of attendees) {
      try { db.prepare('INSERT INTO attendees (event_id, user_email) VALUES (?, ?)').run(id, email); } catch {}
    }
  }
  res.status(201).json(db.prepare('SELECT * FROM events WHERE id = ?').get(id));
});

app.get('/events/:id', (req, res) => {
  const event = db.prepare('SELECT * FROM events WHERE id = ?').get(req.params.id);
  if (!event) return res.status(404).json({ error: 'not_found' });
  event.attendees = db.prepare('SELECT user_email, status FROM attendees WHERE event_id = ?').all(event.id);
  res.json(event);
});

app.post('/events/:id/rsvp', (req, res) => {
  const { email, status } = req.body;
  if (!['pending', 'accepted', 'declined'].includes(status)) return res.status(422).json({ error: 'invalid_status' });
  db.prepare('UPDATE attendees SET status = ? WHERE event_id = ? AND user_email = ?').run(status, req.params.id, email);
  res.json({ event_id: req.params.id, email, status });
});

// === Conflict detection: find overlapping events ===
app.get('/conflicts', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { start_at, end_at } = req.query;
  if (!start_at || !end_at) return res.status(422).json({ error: 'missing_range' });
  const conflicts = db.prepare('SELECT * FROM events WHERE user_id = ? AND start_at < ? AND end_at > ?').all(req.userId, end_at, start_at);
  res.json({ range: { start_at, end_at }, conflicts });
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Calendar API :3000 — X-User-Id header'));
module.exports = app;
