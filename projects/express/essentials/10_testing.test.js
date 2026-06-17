// 10_testing.test.js — Jest + Supertest: unit, integration, auth, edge cases, mock.
const request = require('supertest');
const express = require('express');
const jwt = require('jsonwebtoken');

function createApp() {
  const app = express();
  app.use(express.json());
  const items = [];

  // Helper (testable in isolation)
  app.locals.slugify = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

  app.get('/items', (req, res) => res.json(items));
  app.post('/items', (req, res) => {
    if (!req.body.title) return res.status(400).json({ error: 'title required' });
    const item = { id: items.length + 1, title: req.body.title, slug: app.locals.slugify(req.body.title) };
    items.push(item);
    res.status(201).json(item);
  });
  app.get('/items/:id', (req, res) => {
    const item = items.find(i => i.id === parseInt(req.params.id));
    item ? res.json(item) : res.status(404).json({ error: 'Not found' });
  });

  // Auth-protected
  app.get('/me', (req, res) => {
    const tok = req.headers.authorization?.split(' ')[1];
    if (!tok) return res.status(401).json({ error: 'No token' });
    try { res.json(jwt.verify(tok, 'secret')); }
    catch { res.status(401).json({ error: 'Invalid' }); }
  });

  return app;
}

// ---- TESTS ----
describe('Items CRUD', () => {
  test('GET /items returns empty array', async () => {
    const res = await request(createApp()).get('/items');
    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });

  test('POST /items creates item with slug', async () => {
    const res = await request(createApp()).post('/items').send({ title: 'Hello World!!!' });
    expect(res.status).toBe(201);
    expect(res.body.slug).toBe('hello-world');
    expect(res.body.id).toBe(1);
  });

  test('POST /items without title returns 400', async () => {
    const res = await request(createApp()).post('/items').send({});
    expect(res.status).toBe(400);
  });

  test('GET /items/:id returns 404 for missing', async () => {
    const res = await request(createApp()).get('/items/999');
    expect(res.status).toBe(404);
  });

  test('Full round-trip: create -> list -> get -> verify', async () => {
    const app = createApp();
    await request(app).post('/items').send({ title: 'A' });
    await request(app).post('/items').send({ title: 'B' });
    const list = await request(app).get('/items');
    expect(list.body).toHaveLength(2);
    const one = await request(app).get('/items/1');
    expect(one.body.title).toBe('A');
  });
});

describe('Auth', () => {
  test('GET /me without token returns 401', async () => {
    expect((await request(createApp()).get('/me')).status).toBe(401);
  });
  test('GET /me with valid token returns payload', async () => {
    const token = jwt.sign({ id: 1, role: 'user' }, 'secret');
    const res = await request(createApp()).get('/me').set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.body.role).toBe('user');
  });
});

describe('Slugify (unit test)', () => {
  const slugify = createApp().locals.slugify;
  test.each([
    ['Hello World', 'hello-world'],
    ['  Foo  Bar!!!  ', 'foo-bar'],
    ['UPPER CASE', 'upper-case'],
    ['single', 'single'],
    ['', ''],
  ])('slugify(%s) = %s', (input, expected) => expect(slugify(input)).toBe(expected));
});
