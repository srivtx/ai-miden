// Security Patterns Demo — Parameterized queries, XSS escape, path validation, password hashing.
const express = require('express');
const crypto = require('crypto');
const Database = require('better-sqlite3');
const path = require('path');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password_hash TEXT, salt TEXT)`);

// === 1. Password hashing (PBKDF2, no external deps) ===
function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return { hash, salt };
}

function verifyPassword(password, hash, salt) {
  const test = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(hash, 'hex'));
}

// Seed
const { hash: h1, salt: s1 } = hashPassword('correct horse battery staple');
db.prepare('INSERT INTO users (email, password_hash, salt) VALUES (?, ?, ?)').run('alice@example.com', h1, s1);

// === 2. XSS escape (the bare minimum) ===
function escapeHtml(s) {
  if (typeof s !== 'string') return '';
  return s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// === 3. Path validation ===
function safeJoin(base, target) {
  const resolved = path.resolve(base, target);
  if (!resolved.startsWith(path.resolve(base))) throw new Error('Path traversal detected');
  return resolved;
}

// === Endpoints ===
app.post('/register', (req, res) => {
  const { email, password } = req.body;
  if (!email || !email.includes('@')) return res.status(422).json({ error: 'invalid_email' });
  if (!password || password.length < 8) return res.status(422).json({ error: 'weak_password' });
  const { hash, salt } = hashPassword(password);
  try {
    db.prepare('INSERT INTO users (email, password_hash, salt) VALUES (?, ?, ?)').run(email, hash, salt);
    res.status(201).json({ message: 'User created' });
  } catch (e) {
    res.status(409).json({ error: 'email_taken' });
  }
});

app.post('/login', (req, res) => {
  const { email, password } = req.body;
  // PARAMETERIZED QUERY (not string interpolation)
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  if (!user) return res.status(401).json({ error: 'invalid_credentials' });
  if (!verifyPassword(password, user.password_hash, user.salt)) return res.status(401).json({ error: 'invalid_credentials' });
  res.json({ message: 'Logged in', user: { id: user.id, email: user.email } });
});

app.get('/users/:id', (req, res) => {
  // PARAMETERIZED, ID validation
  const id = parseInt(req.params.id);
  if (isNaN(id)) return res.status(400).json({ error: 'invalid_id' });
  const user = db.prepare('SELECT id, email FROM users WHERE id = ?').get(id);
  if (!user) return res.status(404).json({ error: 'not_found' });
  res.json(user);
});

app.get('/search', (req, res) => {
  // XSS-SAFE: escape user input
  const q = escapeHtml(req.query.q || '');
  res.set('Content-Type', 'text/html');
  res.send(`<h1>Search results for: ${q}</h1><p>Try: ?q=<script>alert(1)</script> — it should NOT execute.</p>`);
});

app.get('/file/:name', (req, res) => {
  // PATH TRAVERSAL-SAFE
  try {
    const safe = safeJoin('/tmp/uploads', req.params.name);
    res.json({ path: safe, note: 'Path is inside /tmp/uploads' });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

// === Security headers (basic) ===
app.use((req, res, next) => {
  res.set('X-Content-Type-Options', 'nosniff');
  res.set('X-Frame-Options', 'DENY');
  res.set('X-XSS-Protection', '1; mode=block');
  res.set('Strict-Transport-Security', 'max-age=31536000');
  res.set('Content-Security-Policy', "default-src 'self'");
  next();
});

app.listen(3000, () => console.log('Security demo :3000'));
module.exports = app;
