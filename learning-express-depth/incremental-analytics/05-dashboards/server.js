// 05-dashboards: Pre-computed metrics. One endpoint, many numbers. Powers the dashboard UI.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, event_name TEXT, properties TEXT, ts TEXT DEFAULT (datetime('now')))`);

// Dashboard endpoint: all key metrics in one call
app.get('/dashboard', (req, res) => {
  const now = new Date();
  const last24h = new Date(now - 24 * 3600000).toISOString();
  const last7d = new Date(now - 7 * 86400000).toISOString();
  const last30d = new Date(now - 30 * 86400000).toISOString();

  // Total events
  const totalEvents = db.prepare('SELECT COUNT(*) as c FROM events').get().c;

  // Events in last 24h
  const events24h = db.prepare('SELECT COUNT(*) as c FROM events WHERE ts > ?').get(last24h).c;

  // Unique users in last 24h
  const dau = db.prepare('SELECT COUNT(DISTINCT user_id) as c FROM events WHERE ts > ? AND user_id IS NOT NULL').get(last24h).c;

  // Top events in last 7 days
  const topEvents = db.prepare(`
    SELECT event_name, COUNT(*) as count FROM events WHERE ts > ?
    GROUP BY event_name ORDER BY count DESC LIMIT 10
  `).all(last7d);

  // Top properties (for purchase events, the totals)
  const revenue = db.prepare(`
    SELECT SUM(CAST(json_extract(properties, '$.amount') AS REAL)) as total
    FROM events WHERE event_name = 'purchase' AND ts > ?
  `).get(last30d).total || 0;

  // Daily event counts (for a chart)
  const dailyCounts = db.prepare(`
    SELECT date(ts) as day, COUNT(*) as count
    FROM events WHERE ts > ?
    GROUP BY day ORDER BY day
  `).all(last7d);

  res.json({
    now: now.toISOString(),
    totals: { events: totalEvents, events_24h: events24h },
    active_users: { dau, wau: db.prepare('SELECT COUNT(DISTINCT user_id) as c FROM events WHERE ts > ? AND user_id IS NOT NULL').get(last7d).c, mau: db.prepare('SELECT COUNT(DISTINCT user_id) as c FROM events WHERE ts > ? AND user_id IS NOT NULL').get(last30d).c },
    top_events: topEvents,
    revenue_30d: revenue,
    daily_counts: dailyCounts,
  });
});

app.listen(3000, () => console.log('05-dashboards on :3000'));
