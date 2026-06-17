// 10-audit: Log every auth event. Login, logout, password change, 2FA enable, suspicious activity.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, event TEXT, ip TEXT, user_agent TEXT, success INTEGER, details TEXT, ts TEXT DEFAULT (datetime('now')))`);

function logEvent(userId, event, success, details = {}, ip = null, userAgent = null) {
  db.prepare('INSERT INTO audit_log (user_id, event, ip, user_agent, success, details) VALUES (?, ?, ?, ?, ?, ?)').run(userId, event, ip, userAgent, success ? 1 : 0, JSON.stringify(details));
}

// Middleware: capture IP and user-agent on every request
app.use((req, res, next) => {
  req.ip = req.ip;
  req.userAgent = req.headers['user-agent'];
  next();
});

// Login attempt (success or failure)
app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;
  // ... validate credentials ...
  const user = email === 'alice@example.com' && password === 'password123' ? { id: 'u_alice' } : null;
  if (!user) {
    logEvent(null, 'login_failed', false, { email }, req.ip, req.userAgent);
    return res.status(401).json({ error: 'invalid_credentials' });
  }
  logEvent(user.id, 'login_success', true, {}, req.ip, req.userAgent);
  res.json({ user });
});

// Logout
app.post('/auth/logout', (req, res) => {
  const userId = req.headers['x-user-id'];
  logEvent(userId, 'logout', true);
  res.json({ logged_out: true });
});

// Password change
app.post('/auth/change-password', (req, res) => {
  const userId = req.headers['x-user-id'];
  logEvent(userId, 'password_change', true, { source: 'user_initiated' }, req.ip, req.userAgent);
  res.json({ changed: true });
});

// 2FA enable
app.post('/auth/2fa/enable', (req, res) => {
  const userId = req.headers['x-user-id'];
  logEvent(userId, '2fa_enabled', true, { method: 'totp' }, req.ip, req.userAgent);
  res.json({ enabled: true });
});

// Suspicious activity
app.post('/auth/suspicious', (req, res) => {
  const userId = req.headers['x-user-id'];
  logEvent(userId, 'suspicious_activity', false, { reason: req.body.reason }, req.ip, req.userAgent);
  res.json({ logged: true });
});

// Query the audit log
app.get('/admin/audit', (req, res) => {
  const { user_id, event, success, since, limit = 50 } = req.query;
  let query = 'SELECT * FROM audit_log WHERE 1=1';
  const params = [];
  if (user_id) { query += ' AND user_id = ?'; params.push(user_id); }
  if (event) { query += ' AND event = ?'; params.push(event); }
  if (success !== undefined) { query += ' AND success = ?'; params.push(success === 'true' ? 1 : 0); }
  if (since) { query += ' AND ts > ?'; params.push(since); }
  query += ' ORDER BY id DESC LIMIT ?';
  params.push(parseInt(limit));
  const entries = db.prepare(query).all(...params).map(e => ({ ...e, details: JSON.parse(e.details || '{}') }));
  res.json({ count: entries.length, entries });
});

// Detect suspicious patterns: many failed logins from same IP
app.get('/admin/suspicious-ips', (req, res) => {
  const rows = db.prepare(`
    SELECT ip, COUNT(*) as failed_count
    FROM audit_log
    WHERE event = 'login_failed' AND ts > datetime('now', '-1 hour')
    GROUP BY ip
    HAVING failed_count >= 3
    ORDER BY failed_count DESC
  `).all();
  res.json({ suspicious_ips: rows });
});

app.listen(3000, () => console.log('10-audit on :3000'));
