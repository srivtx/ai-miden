// 05_jwt_auth.js — Register, login, protected routes. Learn: JWT, bcrypt, auth middleware.

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());

const SECRET = process.env.JWT_SECRET || 'dev-secret-change-in-production';
const TOKEN_EXPIRY = '1h';

// ---- Simulated user database ----
const users = [];

// ---- Middleware: verify JWT on protected routes ----
function authenticate(req, res, next) {
  const header = req.headers.authorization;
  if (!header || !header.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing Bearer token' });
  }
  try {
    const payload = jwt.verify(header.split(' ')[1], SECRET);
    req.user = payload; // { id, email, iat, exp }
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') return res.status(401).json({ error: 'Token expired' });
    return res.status(401).json({ error: 'Invalid token' });
  }
}

// ---- Middleware: role check ----
function requireRole(role) {
  return (req, res, next) => {
    if (req.user.role !== role) return res.status(403).json({ error: `Requires ${role} role` });
    next();
  };
}

// ---- Routes ----

// REGISTER
app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email and password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });

  const hash = await bcrypt.hash(password, 10);
  const user = { id: users.length + 1, name, email, password: hash, role: 'user' };
  users.push(user);

  const token = jwt.sign({ id: user.id, email: user.email, role: user.role }, SECRET, { expiresIn: TOKEN_EXPIRY });
  res.status(201).json({ user: { id: user.id, name, email, role: user.role }, token });
});

// LOGIN
app.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = users.find(u => u.email === email);
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });

  const match = await bcrypt.compare(password, user.password);
  if (!match) return res.status(401).json({ error: 'Invalid credentials' });

  const token = jwt.sign({ id: user.id, email: user.email, role: user.role }, SECRET, { expiresIn: TOKEN_EXPIRY });
  res.json({ user: { id: user.id, name: user.name, email, role: user.role }, token });
});

// PROTECTED: any authenticated user
app.get('/me', authenticate, (req, res) => {
  res.json({ user: req.user });
});

// PROTECTED + ROLE: admin only
app.get('/admin', authenticate, requireRole('admin'), (req, res) => {
  res.json({ message: 'Admin dashboard', user: req.user });
});

app.listen(3000, () => console.log('Auth API on :3000'));
/*
Test:
  # Register
  curl -X POST localhost:3000/auth/register -H "Content-Type: application/json" \
    -d '{"name":"Zen","email":"z@t.com","password":"secret123"}'
  # Login (save the token)
  TOKEN=$(curl -s -X POST localhost:3000/auth/login -H "Content-Type: application/json" \
    -d '{"email":"z@t.com","password":"secret123"}' | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
  # Protected route
  curl -H "Authorization: Bearer $TOKEN" localhost:3000/me
  # Admin route (fails — user role is 'user')
  curl -H "Authorization: Bearer $TOKEN" localhost:3000/admin
*/
