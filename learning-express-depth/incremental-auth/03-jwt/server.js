// 03-jwt: Issue signed tokens on login. Verify them on every protected endpoint.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET = process.env.JWT_SECRET || 'dev-secret-not-for-prod';
const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT)`);

function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  return { hash: crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex'), salt };
}
function verifyPassword(password, hash, salt) {
  const test = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return test.length === hash.length && crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(hash, 'hex'));
}

// Auth middleware
function auth(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) return res.status(401).json({ error: 'missing_token' });
  const token = auth.slice(7);
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (e) {
    return res.status(401).json({ error: 'invalid_token', reason: e.message });
  }
}

// Signup
app.post('/auth/signup', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password || password.length < 8) return res.status(422).json({ error: 'invalid_input' });
  const id = 'u_' + crypto.randomBytes(8).toString('hex');
  const { hash, salt } = hashPassword(password);
  try {
    db.prepare('INSERT INTO users (id, email, password_hash, salt) VALUES (?, ?, ?, ?)').run(id, email, hash, salt);
    res.status(201).json({ id, email });
  } catch { res.status(409).json({ error: 'email_taken' }); }
});

// Login — now returns a JWT
app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  if (!user || !verifyPassword(password, user.password_hash, user.salt)) {
    return res.status(401).json({ error: 'invalid_credentials' });
  }
  const token = jwt.sign(
    { sub: user.id, email: user.email },
    SECRET,
    { expiresIn: '1h' }
  );
  res.json({
    user: { id: user.id, email: user.email },
    token,
    expires_in: 3600,
  });
});

// Protected endpoint
app.get('/me', auth, (req, res) => {
  const user = db.prepare('SELECT id, email FROM users WHERE id = ?').get(req.user.sub);
  res.json({ user });
});

app.listen(3000, () => console.log('03-jwt on :3000'));
