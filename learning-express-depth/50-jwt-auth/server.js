// 50 — JWT Auth
// NEW CONCEPT: authentication with JSON Web Tokens.
// When a user logs in, we give them a signed token. They send it with every request.
const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET = 'my-secret-key';  // In production, use env var

// Fake user database
const users = [
  { id: 1, email: 'alice@example.com', password: 'password123' },
  { id: 2, email: 'bob@example.com', password: 'password456' },
];

// Login: return a token
app.post('/login', (req, res) => {
  const { email, password } = req.body;
  const user = users.find(u => u.email === email && u.password === password);
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });

  const token = jwt.sign(
    { sub: user.id, email: user.email },  // payload
    SECRET,
    { expiresIn: '1h' }                  // expires in 1 hour
  );
  res.json({ token, user: { id: user.id, email: user.email } });
});

// Middleware: verify the token
function authMiddleware(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid Authorization header' });
  }
  const token = auth.slice(7);  // Remove "Bearer "
  try {
    const payload = jwt.verify(token, SECRET);
    req.user = payload;  // { sub, email, iat, exp }
    next();
  } catch (e) {
    res.status(401).json({ error: 'Invalid or expired token' });
  }
}

// Protected endpoint
app.get('/me', authMiddleware, (req, res) => {
  res.json({ user: req.user });
});

app.get('/admin/users', authMiddleware, (req, res) => {
  res.json({ users: users.map(u => ({ id: u.id, email: u.email })) });
});

app.listen(3000, () => console.log('JWT auth on http://localhost:3000'));
