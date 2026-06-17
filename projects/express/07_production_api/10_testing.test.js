// 10_testing.test.js — Jest + Supertest. Learn: unit tests, API tests, mock, coverage.

// Run: npx jest 10_testing.test.js

const request = require('supertest');
const express = require('express');

// ---- The app under test ----
function createApp() {
  const app = express();
  app.use(express.json());

  // Utility function (tested in isolation)
  app.locals.isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  // GET health
  app.get('/health', (req, res) => res.json({ status: 'ok' }));

  // POST user
  app.post('/users', (req, res) => {
    const { name, email } = req.body;
    if (!name) return res.status(400).json({ error: 'name required' });
    if (!app.locals.isValidEmail(email)) return res.status(400).json({ error: 'invalid email' });
    res.status(201).json({ id: 1, name, email });
  });

  // Protected route
  app.get('/me', (req, res) => {
    const token = req.headers.authorization;
    if (!token || !token.startsWith('Bearer ')) return res.status(401).json({ error: 'unauthorized' });
    res.json({ id: 1, name: 'Test User' });
  });

  return app;
}

// ---- Tests ----

describe('Health endpoint', () => {
  test('GET /health returns 200', async () => {
    const res = await request(createApp()).get('/health');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: 'ok' });
  });
});

describe('User creation', () => {
  test('POST /users with valid data returns 201', async () => {
    const res = await request(createApp())
      .post('/users')
      .send({ name: 'Zen', email: 'zen@test.com' });
    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('id');
    expect(res.body.name).toBe('Zen');
  });

  test('POST /users without name returns 400', async () => {
    const res = await request(createApp())
      .post('/users')
      .send({ email: 'zen@test.com' });
    expect(res.status).toBe(400);
  });

  test('POST /users with invalid email returns 400', async () => {
    const res = await request(createApp())
      .post('/users')
      .send({ name: 'Zen', email: 'not-an-email' });
    expect(res.status).toBe(400);
  });
});

describe('Auth middleware', () => {
  test('GET /me without token returns 401', async () => {
    const res = await request(createApp()).get('/me');
    expect(res.status).toBe(401);
  });

  test('GET /me with valid token returns user', async () => {
    const res = await request(createApp())
      .get('/me')
      .set('Authorization', 'Bearer valid-token');
    expect(res.status).toBe(200);
    expect(res.body.name).toBe('Test User');
  });
});

describe('Email validation (unit test)', () => {
  const isValidEmail = createApp().locals.isValidEmail;
  test('valid email', () => expect(isValidEmail('a@b.com')).toBe(true));
  test('invalid email', () => expect(isValidEmail('not-email')).toBe(false));
  test('empty string', () => expect(isValidEmail('')).toBe(false));
});
