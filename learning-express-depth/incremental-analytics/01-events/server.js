// 01-events: Track events. Anything users do: page view, button click, purchase, etc.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    anonymous_id TEXT,
    event_name TEXT NOT NULL,
    properties TEXT,
    ts TEXT DEFAULT (datetime('now'))
  )
`);
db.exec(`CREATE INDEX idx_events_name ON events(event_name, ts)`);
db.exec(`CREATE INDEX idx_events_user ON events(user_id, ts)`);

// Track a single event
app.post('/track', (req, res) => {
  const { user_id, anonymous_id, event_name, properties } = req.body;
  if (!event_name) return res.status(422).json({ error: 'event_name required' });
  db.prepare('INSERT INTO events (user_id, anonymous_id, event_name, properties) VALUES (?, ?, ?, ?)').run(user_id || null, anonymous_id || null, event_name, JSON.stringify(properties || {}));
  res.status(202).json({ tracked: true });
});

// Track a batch of events
app.post('/track/batch', (req, res) => {
  const { events } = req.body;
  if (!Array.isArray(events)) return res.status(422).json({ error: 'events must be array' });
  const stmt = db.prepare('INSERT INTO events (user_id, anonymous_id, event_name, properties) VALUES (?, ?, ?, ?)');
  for (const e of events) {
    if (e.event_name) stmt.run(e.user_id || null, e.anonymous_id || null, e.event_name, JSON.stringify(e.properties || {}));
  }
  res.status(202).json({ tracked: events.length });
});

// Query events
app.get('/events', (req, res) => {
  const { event_name, user_id, since, limit = 100 } = req.query;
  let query = 'SELECT * FROM events WHERE 1=1';
  const params = [];
  if (event_name) { query += ' AND event_name = ?'; params.push(event_name); }
  if (user_id) { query += ' AND user_id = ?'; params.push(user_id); }
  if (since) { query += ' AND ts > ?'; params.push(since); }
  query += ' ORDER BY id DESC LIMIT ?';
  params.push(parseInt(limit));
  const events = db.prepare(query).all(...params).map(e => ({ ...e, properties: JSON.parse(e.properties || '{}') }));
  res.json({ count: events.length, events });
});

// Top events by count
app.get('/events/top', (req, res) => {
  const since = req.query.since || new Date(Date.now() - 24 * 3600000).toISOString();
  const top = db.prepare(`
    SELECT event_name, COUNT(*) as count
    FROM events WHERE ts > ?
    GROUP BY event_name
    ORDER BY count DESC
    LIMIT 10
  `).all(since);
  res.json({ since, top });
});

app.listen(3000, () => console.log('01-events on :3000'));
