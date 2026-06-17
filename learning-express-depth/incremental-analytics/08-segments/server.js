// 08-segments: Define user segments. "Users who purchased in the last 30 days."
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT, country TEXT, plan TEXT, signup_date TEXT)`);
db.exec(`CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, event_name TEXT, ts TEXT DEFAULT (datetime('now')))`);

function evaluateSegment(rule) {
  // Build the WHERE clause from the rule
  const conditions = [];
  const params = [];
  if (rule.country) { conditions.push('u.country = ?'); params.push(rule.country); }
  if (rule.plan) { conditions.push('u.plan = ?'); params.push(rule.plan); }
  if (rule.signup_after) { conditions.push('u.signup_date > ?'); params.push(rule.signup_after); }
  if (rule.did_event) {
    conditions.push(`u.id IN (SELECT user_id FROM events WHERE event_name = ? AND ts > ?)`);
    params.push(rule.did_event, rule.since || '1970-01-01');
  }
  const where = conditions.length ? 'WHERE ' + conditions.join(' AND ') : '';
  return db.prepare(`SELECT * FROM users u ${where}`).all(...params);
}

// Create a segment (just a rule object for now)
app.post('/segments/preview', (req, res) => {
  const rule = req.body;
  const users = evaluateSegment(rule);
  res.json({ rule, count: users.length, users: users.slice(0, 100) });
});

// Get stats for a segment
app.post('/segments/stats', (req, res) => {
  const rule = req.body;
  const users = evaluateSegment(rule);
  const byCountry = {};
  const byPlan = {};
  for (const u of users) {
    byCountry[u.country] = (byCountry[u.country] || 0) + 1;
    byPlan[u.plan] = (byPlan[u.plan] || 0) + 1;
  }
  res.json({ rule, count: users.length, by_country: byCountry, by_plan: byPlan });
});

// Seed users
const countries = ['US', 'UK', 'FR', 'DE', 'JP'];
const plans = ['free', 'pro', 'enterprise'];
for (let i = 0; i < 100; i++) {
  const id = `u_${i}`;
  const country = countries[i % countries.length];
  const plan = plans[i % plans.length];
  const signup = new Date(Date.now() - i * 86400000).toISOString();
  db.prepare('INSERT INTO users VALUES (?, ?, ?, ?, ?)').run(id, `u${i}@example.com`, country, plan, signup);
  if (i % 3 === 0) db.prepare("INSERT INTO events (user_id, event_name) VALUES (?, 'purchase')").run(id);
}

app.listen(3000, () => console.log('08-segments on :3000'));
