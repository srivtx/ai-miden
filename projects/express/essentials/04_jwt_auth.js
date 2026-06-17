// 04_jwt_auth.js — Register, login, JWT, protected routes, refresh token.

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());

const SECRET = 'secret-key';
const REFRESH_SECRET = 'refresh-secret';
const users = [];
const refreshTokens = new Set();

app.post('/register', async (req, res) => {
  const { email, password } = req.body;
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Exists' });
  const hash = await bcrypt.hash(password, 10);
  const user = { id: users.length + 1, email, password: hash, role: 'user' };
  users.push(user);
  const access = jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '15m' });
  const refresh = jwt.sign({ id: user.id }, REFRESH_SECRET, { expiresIn: '7d' });
  refreshTokens.add(refresh);
  res.status(201).json({ user: { id: user.id, email }, accessToken: access, refreshToken: refresh });
});

app.post('/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password)))
    return res.status(401).json({ error: 'Invalid credentials' });
  const access = jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '15m' });
  const refresh = jwt.sign({ id: user.id }, REFRESH_SECRET, { expiresIn: '7d' });
  refreshTokens.add(refresh);
  res.json({ accessToken: access, refreshToken: refresh });
});

app.post('/refresh', (req, res) => {
  const { refreshToken } = req.body;
  if (!refreshToken || !refreshTokens.has(refreshToken)) return res.status(401).json({ error: 'Invalid' });
  try {
    const { id } = jwt.verify(refreshToken, REFRESH_SECRET);
    const user = users.find(u => u.id === id);
    const access = jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '15m' });
    res.json({ accessToken: access });
  } catch { res.status(401).json({ error: 'Expired' }); }
});

app.post('/logout', (req, res) => {
  refreshTokens.delete(req.body.refreshToken);
  res.json({ msg: 'Logged out' });
});

function guard(req, res, next) {
  try {
    req.user = jwt.verify(req.headers.authorization?.split(' ')[1], SECRET);
    next();
  } catch { res.status(401).json({ error: 'Invalid token' }); }
}

app.get('/me', guard, (req, res) => res.json({ user: req.user }));
app.get('/admin', guard, (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Forbidden' });
  res.json({ msg: 'Admin' });
});

app.listen(3000, () => console.log('JWT auth :3000'));
