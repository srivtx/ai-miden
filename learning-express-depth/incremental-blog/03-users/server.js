// 03-users: User accounts. Signup, login, profile, JWT.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT, display_name TEXT, bio TEXT, avatar_url TEXT, created_at TEXT DEFAULT (datetime('now')))`);

function hashPassword(pw, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  return { hash: crypto.pbkdf2Sync(pw, salt, 100000, 64, 'sha512').toString('hex'), salt };
}
function verifyPassword(pw, hash, salt) {
  const test = crypto.pbkdf2Sync(pw, salt, 100000, 64, 'sha512').toString('hex');
  return test.length === hash.length && crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(hash, 'hex'));
}
function auth(req, res, next) {
  const token = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  try { req.user = jwt.verify(token, SECRET); next(); }
  catch { res.status(401).json({ error: 'unauthorized' }); }
}

// Signup
app.post('/auth/signup', (req, res) => {
  const { email, password, display_name } = req.body;
  if (!email || !password || password.length < 8) return res.status(422).json({ error: 'invalid input' });
  const id = 'u_' + crypto.randomBytes(4).toString('hex');
  const { hash, salt } = hashPassword(password);
  try {
    db.prepare('INSERT INTO users (id, email, password_hash, salt, display_name) VALUES (?, ?, ?, ?, ?)').run(id, email, hash, salt, display_name || email.split('@')[0]);
    res.status(201).json({ user: { id, email, display_name: display_name || email.split('@')[0] }, token: jwt.sign({ sub: id, email }, SECRET, { expiresIn: '7d' }) });
  } catch { res.status(409).json({ error: 'email taken' }); }
});

app.post('/auth/login', (req, res) => {
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(req.body.email);
  if (!user || !verifyPassword(req.body.password, user.password_hash, user.salt)) return res.status(401).json({ error: 'invalid' });
  res.json({ user: { id: user.id, email: user.email, display_name: user.display_name }, token: jwt.sign({ sub: user.id, email: user.email }, SECRET, { expiresIn: '7d' }) });
});

// Profile (public)
app.get('/users/:id', (req, res) => {
  const user = db.prepare('SELECT id, display_name, bio, avatar_url, created_at FROM users WHERE id = ?').get(req.params.id);
  user ? res.json(user) : res.status(404).json({ error: 'not found' });
});

// Update own profile
app.patch('/users/me', auth, (req, res) => {
  const updates = [];
  const params = [];
  for (const f of ['display_name', 'bio', 'avatar_url']) {
    if (req.body[f] !== undefined) { updates.push(`${f} = ?`); params.push(req.body[f]); }
  }
  if (!updates.length) return res.status(422).json({ error: 'no updates' });
  params.push(req.user.sub);
  db.prepare(`UPDATE users SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  const user = db.prepare('SELECT id, display_name, bio, avatar_url FROM users WHERE id = ?').get(req.user.sub);
  res.json(user);
});

app.get('/me', auth, (req, res) => res.json({ user: req.user }));

app.listen(3000, () => console.log('03-users on :3000'));
