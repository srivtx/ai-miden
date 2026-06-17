// 56 — CSRF Protection
// NEW CONCEPT: cross-site request forgery protection.
// Without protection, a malicious site can submit forms to your site using the user's cookies.
const express = require('express');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');
const app = express();
app.use(express.json());
app.use(cookieParser());

const SECRET = 'csrf-secret';

function generateCsrfToken() {
  return crypto.randomBytes(16).toString('hex');
}

// Set a CSRF cookie on first visit
app.get('/csrf-token', (req, res) => {
  const token = generateCsrfToken();
  res.cookie('csrf_token', token, { httpOnly: false, sameSite: 'strict' });
  res.json({ csrfToken: token });
});

// Middleware: verify CSRF token on state-changing requests
function verifyCsrf(req, res, next) {
  if (req.method === 'GET' || req.method === 'HEAD') return next();  // GET is safe

  const tokenFromHeader = req.headers['x-csrf-token'];
  const tokenFromCookie = req.cookies.csrf_token;
  const tokenFromBody = req.body && req.body._csrf;

  const provided = tokenFromHeader || tokenFromBody;
  if (!provided || provided !== tokenFromCookie) {
    return res.status(403).json({ error: 'Invalid CSRF token' });
  }
  next();
}

app.post('/transfer', verifyCsrf, (req, res) => {
  res.json({ message: `Transferred $${req.body.amount} to ${req.body.to}` });
});

app.listen(3000, () => console.log('CSRF demo on http://localhost:3000'));
