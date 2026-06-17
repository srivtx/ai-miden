// 10-realtime: Real-time event stream. SSE for one-to-many. Latest 100 events live.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, event_name TEXT, properties TEXT, ts TEXT DEFAULT (datetime('now')))`);

// Connected SSE clients
const clients = new Set();

function broadcast(event) {
  for (const res of clients) {
    res.write(`event: ${event.event_name}\ndata: ${JSON.stringify({ id: event.id, user_id: event.user_id, properties: JSON.parse(event.properties || '{}'), ts: event.ts })}\n\n`);
  }
}

// SSE endpoint: live event stream
app.get('/stream', (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  });
  res.flushHeaders();
  res.write(`event: connected\ndata: ${JSON.stringify({ ts: new Date().toISOString() })}\n\n`);
  clients.add(res);
  req.on('close', () => clients.delete(res));
});

// Track an event: also broadcast it
app.post('/track', (req, res) => {
  const { user_id, event_name, properties } = req.body;
  if (!event_name) return res.status(422).json({ error: 'event_name required' });
  const r = db.prepare('INSERT INTO events (user_id, event_name, properties) VALUES (?, ?, ?)').run(user_id, event_name, JSON.stringify(properties || {}));
  const event = db.prepare('SELECT * FROM events WHERE id = ?').get(r.lastInsertRowid);
  broadcast(event);
  res.status(202).json({ tracked: true, id: event.id });
});

// Live counts (auto-refreshed)
const liveCounts = {};
setInterval(() => {
  for (const e of db.prepare('SELECT event_name, COUNT(*) as c FROM events WHERE ts > datetime("now", "-1 minute") GROUP BY event_name').all()) {
    liveCounts[e.event_name] = e.c;
  }
}, 5000);

app.get('/live/counts', (req, res) => res.json({ window: '1 minute', counts: liveCounts }));

// Recent events
app.get('/recent', (req, res) => {
  const events = db.prepare('SELECT * FROM events ORDER BY id DESC LIMIT 20').all().map(e => ({ ...e, properties: JSON.parse(e.properties || '{}') }));
  res.json({ events });
});

app.listen(3000, () => console.log('10-realtime on :3000 (try /stream with curl -N)'));
