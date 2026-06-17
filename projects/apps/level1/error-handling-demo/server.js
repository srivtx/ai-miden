// Error Handling Demo — Typed errors, global handler, request IDs, structured responses.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// === Typed error class ===
class AppError extends Error {
  constructor(statusCode, code, message, details) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
  }
}

// === Request ID middleware ===
app.use((req, res, next) => {
  req.requestId = req.headers['x-request-id'] || 'req_' + crypto.randomBytes(8).toString('hex');
  res.set('X-Request-Id', req.requestId);
  next();
});

// === Routes that throw typed errors ===
app.get('/users/:id', (req, res, next) => {
  const id = parseInt(req.params.id);
  if (isNaN(id)) return next(new AppError(400, 'invalid_id', 'ID must be a number', { received: req.params.id }));
  if (id === 0) return next(new AppError(404, 'user_not_found', `User ${id} does not exist`));
  if (id === 999) return next(new AppError(403, 'forbidden', 'You cannot access this user'));
  res.json({ id, name: 'Alice' });
});

app.post('/login', (req, res, next) => {
  const { email, password } = req.body;
  if (!email) return next(new AppError(422, 'missing_email', 'Email is required'));
  if (!password) return next(new AppError(422, 'missing_password', 'Password is required'));
  if (password.length < 8) return next(new AppError(422, 'weak_password', 'Password must be at least 8 characters', { minLength: 8 }));
  res.json({ token: 'fake-jwt-token' });
});

app.get('/admin', (req, res, next) => {
  // Simulated unhandled error
  const data = null;
  try {
    return res.json({ name: data.name }); // Will throw
  } catch (err) {
    return next(err);
  }
});

// === 404 handler ===
app.use((req, res, next) => next(new AppError(404, 'route_not_found', `No route for ${req.method} ${req.path}`)));

// === Global error handler ===
app.use((err, req, res, next) => {
  if (err instanceof AppError) {
    // Known error: structured response
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        details: err.details,
        request_id: req.requestId,
        docs_url: `https://api.example.com/docs/errors#${err.code}`,
      }
    });
  }
  // Unknown error: log, return generic
  console.error(`[${req.requestId}] Unhandled error:`, err);
  res.status(500).json({
    error: {
      code: 'internal_error',
      message: 'An unexpected error occurred',
      request_id: req.requestId,
    }
  });
});

app.listen(3000, () => console.log('Error handling demo :3000'));
module.exports = app;
