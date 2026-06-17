// 06_error_handling.js — Error taxonomy, async wrapper, custom error classes.
const express = require('express');
const app = express();
app.use(express.json());

class AppError extends Error {
  constructor(message, statusCode, code) { super(message); this.statusCode = statusCode; this.code = code; }
}
class NotFoundError extends AppError { constructor(msg) { super(msg || 'Not found', 404, 'NOT_FOUND'); } }
class ValidationError extends AppError { constructor(msg) { super(msg, 400, 'VALIDATION'); } }

// Wrap async route handlers to catch errors
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

const users = [];

app.get('/users/:id', asyncHandler(async (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (!user) throw new NotFoundError(`User ${req.params.id} not found`);
  res.json(user);
}));

app.post('/users', asyncHandler(async (req, res) => {
  if (!req.body.email) throw new ValidationError('email is required');
  if (!req.body.email.includes('@')) throw new ValidationError('email is invalid');
  const user = { id: users.length + 1, ...req.body };
  users.push(user);
  res.status(201).json(user);
}));

// Simulated external API call
app.get('/external', asyncHandler(async (req, res) => {
  throw Object.assign(new Error('fetch failed'), { code: 'ECONNREFUSED' });
}));

// Central error handler — catches ALL errors
app.use((err, req, res, next) => {
  // Known error (our AppError)
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({ error: { code: err.code, message: err.message } });
  }

  // Node.js system error (file not found, connection refused)
  if (err.code === 'ENOENT') return res.status(404).json({ error: { code: 'FILE_NOT_FOUND', message: 'File not found' } });
  if (err.code === 'ECONNREFUSED') return res.status(502).json({ error: { code: 'UPSTREAM_DOWN', message: 'Service unavailable' } });

  // JWT errors
  if (err.name === 'JsonWebTokenError') return res.status(401).json({ error: { code: 'INVALID_TOKEN', message: 'Invalid token' } });
  if (err.name === 'TokenExpiredError') return res.status(401).json({ error: { code: 'TOKEN_EXPIRED', message: 'Token expired' } });

  // Unknown — log and return generic
  console.error('Unhandled:', err);
  res.status(500).json({ error: { code: 'INTERNAL', message: 'Something went wrong' } });
});

app.listen(3000, () => console.log('Error handling :3000'));
