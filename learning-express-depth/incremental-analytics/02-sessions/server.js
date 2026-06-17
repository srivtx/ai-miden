// 02-sessions: Group events into sessions. A session is a continuous visit (with 30 min idle timeout).
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, anonymous_id TEXT, event_name TEXT, properties TEXT, ts TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE sessions (id TEXT PRIMARY KEY, user_id TEXT, anonymous_id TEXT, started_at TEXT, ended_at TEXT, event_count INTEGER DEFAULT 0)`);

const SESSION_TIMEOUT_MS = 30 * 60 * 1000;  // 30 minutes idle

function getOrCreateSession(userId, anonymousId, eventTs) {
  // Find a recent session (within timeout)
  const cutoff = new Date(new Date(eventTs).getTime() - SESSION_TIMEOUT_MS).toISOString();
  const userKey = userId || anonymousId;
  const recent = db.prepare(`
    SELECT * FROM sessions
    WHERE (user_id = ? OR anonymous_id = ?) AND started_at > ? AND ended_at IS NULL
    ORDER BY started_at DESC LIMIT 1
  `).get(userId, anonymousId, cutoff);
  if (recent) return recent;
  // Create a new session
  const id = 's_' + Math.random().toString(36).slice(2, 12);
  db.prepare('INSERT INTO sessions (id, user_id, anonymous_id, started_at) VALUES (?, ?, ?, ?)').run(id, userId, anonymousId, eventTs);
  return { id, user_id: userId, anonymous_id: anonymousId, started_at: eventTs };
}

app.post('/track', (req, res) => {
  const { user_id, anonymous_id, event_name, properties } = req.body;
  if (!event_name) return res.status(422).json({ error: 'event_name required' });
  const ts = new Date().toISOString();
  const session = getOrCreateSession(user_id, anonymousId, ts);
  db.prepare('INSERT INTO events (user_id, anonymous_id, event_name, properties, ts) VALUES (?, ?, ?, ?, ?)').run(user_id, anonymousId, event_name, JSON.stringify(properties || {}), ts);
  db.prepare('UPDATE sessions SET event_count = event_count + 1, ended_at = ? WHERE id = ?').run(ts, session.id);
  res.status(202).json({ tracked: true, session_id: session.id });
});

// Sessions for a user
app.get('/sessions', (req, res) => {
  const { user_id, since } = req.query;
  let query = 'SELECT * FROM sessions WHERE 1=1';
  const params = [];
  if (user_id) { query += ' AND user_id = ?'; params.push(user_id); }
  if (since) { query += ' AND started_at > ?'; params.push(since); }
  query += ' ORDER BY started_at DESC LIMIT 50';
  res.json({ sessions: db.prepare(query).all(...params) });
});

// Session stats
app.get('/sessions/stats', (req, res) => {
  const since = req.query.since || new Date(Date.now() - 24 * 3600000).toISOString();
  const stats = db.prepare(`
    SELECT
      COUNT(*) as total_sessions,
      COUNT(DISTINCT COALESCE(user_id, anonymous_id)) as unique_users,
      AVG(event_count) as avg_events_per_session
    FROM sessions WHERE started_at > ?
  `).get(since);
  res.json({ since, ...stats });
});

app.listen(3000, () => console.log('02-sessions on :3000 (30 min idle timeout)'));
