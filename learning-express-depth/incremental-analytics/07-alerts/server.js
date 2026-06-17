// 07-alerts: Define alert rules. When a metric crosses a threshold, fire.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, event_name TEXT, ts TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE alert_rules (id TEXT PRIMARY KEY, name TEXT, metric TEXT, operator TEXT CHECK(operator IN ('>', '<', '>=', '<=')), threshold REAL, window_minutes INTEGER, channel TEXT, enabled INTEGER DEFAULT 1)`);
db.exec(`CREATE TABLE alert_history (id INTEGER PRIMARY KEY AUTOINCREMENT, rule_id TEXT, value REAL, fired_at TEXT DEFAULT (datetime('now')))`);

// Create an alert rule
app.post('/alerts', (req, res) => {
  const { name, metric, operator, threshold, window_minutes, channel } = req.body;
  if (!name || !metric || !operator || threshold === undefined) return res.status(422).json({ error: 'missing fields' });
  if (!['>', '<', '>=', '<='].includes(operator)) return res.status(422).json({ error: 'invalid operator' });
  const id = 'a_' + Math.random().toString(36).slice(2, 8);
  db.prepare('INSERT INTO alert_rules VALUES (?, ?, ?, ?, ?, ?, ?, 1)').run(id, name, metric, operator, threshold, window_minutes || 60, channel || 'email');
  res.status(201).json({ id, name, metric, operator, threshold });
});

app.get('/alerts', (req, res) => res.json({ rules: db.prepare('SELECT * FROM alert_rules').all() }));

// Evaluate all rules
app.post('/alerts/evaluate', (req, res) => {
  const rules = db.prepare('SELECT * FROM alert_rules WHERE enabled = 1').all();
  const fired = [];

  for (const rule of rules) {
    const cutoff = new Date(Date.now() - (rule.window_minutes || 60) * 60000).toISOString();
    let value = 0;
    if (rule.metric === 'event_count') {
      value = db.prepare('SELECT COUNT(*) as c FROM events WHERE ts > ?').get(cutoff).c;
    } else if (rule.metric === 'unique_users') {
      value = db.prepare('SELECT COUNT(DISTINCT user_id) as c FROM events WHERE ts > ?').get(cutoff).c;
    } else if (rule.metric === 'error_rate') {
      const total = db.prepare('SELECT COUNT(*) as c FROM events WHERE ts > ?').get(cutoff).c;
      const errors = db.prepare("SELECT COUNT(*) as c FROM events WHERE ts > ? AND event_name = 'error'").get(cutoff).c;
      value = total ? errors / total : 0;
    }

    let triggered = false;
    if (rule.operator === '>' && value > rule.threshold) triggered = true;
    if (rule.operator === '<' && value < rule.threshold) triggered = true;
    if (rule.operator === '>=' && value >= rule.threshold) triggered = true;
    if (rule.operator === '<=' && value <= rule.threshold) triggered = true;

    if (triggered) {
      db.prepare('INSERT INTO alert_history (rule_id, value) VALUES (?, ?)').run(rule.id, value);
      fired.push({ rule_id: rule.id, name: rule.name, value, threshold: rule.threshold });
      console.log(`[alert] ${rule.name}: ${value} ${rule.operator} ${rule.threshold}`);
    }
  }

  res.json({ evaluated: rules.length, fired: fired.length, alerts: fired });
});

// Alert history
app.get('/alerts/history', (req, res) => {
  const history = db.prepare('SELECT * FROM alert_history ORDER BY id DESC LIMIT 50').all();
  res.json({ count: history.length, history });
});

app.listen(3000, () => console.log('07-alerts on :3000 (POST /alerts/evaluate)'));
