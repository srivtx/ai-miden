// 04-cohorts: Group users by signup week. Track what % are still active each week.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT, signup_date TEXT)`);
db.exec(`CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, event_name TEXT, ts TEXT DEFAULT (datetime('now')))`);

// Seed: 10 users signing up each week for 4 weeks
for (let week = 0; week < 4; week++) {
  for (let i = 0; i < 10; i++) {
    const id = `u_w${week}_${i}`;
    const signupDate = new Date(Date.now() - (3 - week) * 7 * 86400000).toISOString();
    db.prepare('INSERT INTO users VALUES (?, ?, ?)').run(id, `${id}@example.com`, signupDate);
    // Week 0: 100% active, Week 1: 80%, Week 2: 60%, Week 3: 50% retention
    for (let w = 0; w <= week; w++) {
      const ts = new Date(Date.now() - (3 - week + w) * 7 * 86400000).toISOString();
      db.prepare('INSERT INTO events (user_id, event_name, ts) VALUES (?, ?, ?)').run(id, 'active', ts);
    }
  }
}

// Compute cohort retention
app.get('/cohorts/retention', (req, res) => {
  // Get all signup weeks
  const cohorts = db.prepare(`
    SELECT
      strftime('%Y-%W', signup_date) as cohort_week,
      COUNT(*) as size
    FROM users
    GROUP BY cohort_week
    ORDER BY cohort_week
  `).all();

  const result = cohorts.map(c => {
    const weekStart = new Date(c.cohort_week + '-1');  // Approximate
    const retention = [];
    for (let w = 0; w < 4; w++) {
      const weekEnd = new Date(weekStart.getTime() + (w + 1) * 7 * 86400000);
      const active = db.prepare(`
        SELECT COUNT(DISTINCT u.id) as count
        FROM users u JOIN events e ON e.user_id = u.id
        WHERE strftime('%Y-%W', u.signup_date) = ? AND e.ts < ? AND e.event_name = 'active'
      `).get(c.cohort_week, weekEnd.toISOString());
      retention.push({
        week: w,
        count: active.count,
        percent: c.size ? Math.round(active.count / c.size * 100) : 0,
      });
    }
    return { cohort: c.cohort_week, size: c.size, retention };
  });

  res.json({ cohorts: result });
});

app.listen(3000, () => console.log('04-cohorts on :3000'));
