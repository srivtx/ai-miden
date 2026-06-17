// Security Basics — Helmet, CORS, rate limit, parameterized queries, XSS escaping.
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const Database = require('better-sqlite3');
const app = express();

app.use(helmet());
app.use(cors({ origin: 'https://myapp.com', credentials: true }));
app.use(express.json());

const db = new Database(':memory:');
db.exec('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)');

// === DEMO 1: SQL Injection (BAD vs GOOD) ===
// Vulnerable
app.get('/unsafe/users/:name', (req, res) => {
  // DON'T DO THIS. Attacker sends: %' OR '1'='1
  const result = db.prepare(`SELECT * FROM users WHERE name = '${req.params.name}'`).all();
  res.json(result); // Returns ALL users!
});

// Safe: parameterized query
app.get('/users/:name', (req, res) => {
  const result = db.prepare('SELECT * FROM users WHERE name = ?').all(req.params.name);
  res.json(result); // Only exact match
});

// === DEMO 2: XSS escaping ===
function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

app.post('/comments', (req, res) => {
  const { author, text } = req.body;
  // BAD: direct interpolation
  // res.send(`<div>${author}: ${text}</div>`);  // XSS if text is <script>alert(1)</script>

  // GOOD: escape
  res.send(`<div>${escapeHtml(author)}: ${escapeHtml(text)}</div>`);
});

// === DEMO 3: Strong password hashing ===
const bcrypt = require('bcryptjs');
app.post('/register', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email and password required' });
  if (password.length < 12) return res.status(400).json({ error: 'Password must be at least 12 characters' });
  const hash = await bcrypt.hash(password, 12);
  db.prepare('INSERT INTO users (name) VALUES (?)').run(email);
  res.json({ id: 1, message: 'Registered. Password hashed with bcrypt cost=12.' });
});

// === DEMO 4: CSRF protection with SameSite cookies ===
app.use((req, res, next) => {
  // SameSite=Strict prevents CSRF entirely: cookie never sent cross-origin
  res.cookie('session', 'demo-session', { httpOnly: true, secure: true, sameSite: 'strict' });
  next();
});

// === DEMO 5: Brute force protection ===
const loginAttempts = new Map(); // IP -> { count, lastAttempt }
app.post('/login', (req, res) => {
  const ip = req.ip;
  const entry = loginAttempts.get(ip) || { count: 0, lastAttempt: 0 };
  if (entry.count >= 5 && Date.now() - entry.lastAttempt < 60000) {
    return res.status(429).json({ error: 'Too many attempts. Wait 1 minute.' });
  }
  // ... verify password ...
  if (Date.now() - entry.lastAttempt > 60000) entry.count = 0;
  entry.count++; entry.lastAttempt = Date.now();
  loginAttempts.set(ip, entry);
  res.json({ message: 'Login attempt recorded' });
});

// === DEMO 6: Security headers (Helmet) ===
app.get('/headers', (req, res) => {
  res.json({
    'X-Content-Type-Options': res.getHeader('X-Content-Type-Options'),
    'X-Frame-Options': res.getHeader('X-Frame-Options'),
    'Strict-Transport-Security': res.getHeader('Strict-Transport-Security'),
    'Content-Security-Policy': res.getHeader('Content-Security-Policy')?.slice(0, 60) + '...',
  });
});

app.listen(3000, () => console.log('Security demo :3000'));
module.exports = app;
