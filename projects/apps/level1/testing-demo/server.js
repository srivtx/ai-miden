// Testing Demo — A testable endpoint and a small test runner (no jest/mocha).
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0, user_id INTEGER)`);

const insert = db.prepare('INSERT INTO todos (title, user_id) VALUES (?, ?)');
const select = db.prepare('SELECT * FROM todos WHERE id = ?');
const list = db.prepare('SELECT * FROM todos WHERE user_id = ?');
const update = db.prepare('UPDATE todos SET done = ? WHERE id = ?');
const del = db.prepare('DELETE FROM todos WHERE id = ?');

// === Endpoints (extracted for testability) ===
function routes(db) {
  const r = express.Router();
  r.post('/todos', (req, res) => {
    if (!req.body.title) return res.status(422).json({ error: 'missing_title' });
    const result = db.prepare('INSERT INTO todos (title, user_id) VALUES (?, ?)').run(req.body.title, req.body.user_id || 1);
    res.status(201).json({ id: result.lastInsertRowid, title: req.body.title });
  });
  r.get('/todos/:id', (req, res) => {
    const row = db.prepare('SELECT * FROM todos WHERE id = ?').get(parseInt(req.params.id));
    row ? res.json(row) : res.status(404).json({ error: 'not_found' });
  });
  r.get('/users/:userId/todos', (req, res) => {
    res.json(db.prepare('SELECT * FROM todos WHERE user_id = ?').all(parseInt(req.params.userId)));
  });
  r.patch('/todos/:id', (req, res) => {
    if (req.body.done === undefined) return res.status(422).json({ error: 'missing_done' });
    db.prepare('UPDATE todos SET done = ? WHERE id = ?').run(req.body.done ? 1 : 0, parseInt(req.params.id));
    res.json({ id: parseInt(req.params.id), done: req.body.done });
  });
  r.delete('/todos/:id', (req, res) => {
    db.prepare('DELETE FROM todos WHERE id = ?').run(parseInt(req.params.id));
    res.status(204).end();
  });
  return r;
}

app.use(routes(db));

// === Mini test runner ===
async function test(name, fn) {
  try { await fn(); console.log(`  PASS  ${name}`); return 0; }
  catch (e) { console.log(`  FAIL  ${name}\n         ${e.message}`); return 1; }
}

function assertEqual(actual, expected, msg = '') {
  if (actual !== expected) throw new Error(`${msg} expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
}

function assertStatus(res, expected) {
  if (res.status !== expected) throw new Error(`status: expected ${expected}, got ${res.status}`);
}

async function http(app, method, path, body) {
  return new Promise((resolve) => {
    const server = app.listen(0, () => {
      const port = server.address().port;
      const http = require('http');
      const data = body ? JSON.stringify(body) : null;
      const req = http.request({ port, path, method, headers: data ? { 'Content-Type': 'application/json', 'Content-Length': data.length } : {} }, (res) => {
        let chunks = '';
        res.on('data', c => chunks += c);
        res.on('end', () => {
          server.close();
          try { resolve({ status: res.statusCode, body: chunks ? JSON.parse(chunks) : null }); }
          catch { resolve({ status: res.statusCode, body: chunks }); }
        });
      });
      if (data) req.write(data);
      req.end();
    });
  });
}

// === Run tests when called with `node server.js test` ===
if (process.argv[2] === 'test') {
  console.log('\nRunning tests:\n');
  (async () => {
    const testApp = express();
    testApp.use(express.json());
    const testDb = new Database(':memory:');
    testDb.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0, user_id INTEGER)`);
    testApp.use(routes(testDb));
    let failed = 0;
    failed += await test('POST /todos creates a todo', async () => {
      const res = await http(testApp, 'POST', '/todos', { title: 'Buy milk', user_id: 1 });
      assertStatus(res, 201);
      assertEqual(res.body.title, 'Buy milk');
    });
    failed += await test('POST /todos rejects empty title', async () => {
      const res = await http(testApp, 'POST', '/todos', { title: '' });
      assertStatus(res, 422);
      assertEqual(res.body.error, 'missing_title');
    });
    failed += await test('GET /todos/:id returns the todo', async () => {
      const created = await http(testApp, 'POST', '/todos', { title: 'Test', user_id: 1 });
      const res = await http(testApp, 'GET', `/todos/${created.body.id}`);
      assertStatus(res, 200);
      assertEqual(res.body.title, 'Test');
    });
    failed += await test('PATCH /todos/:id marks done', async () => {
      const created = await http(testApp, 'POST', '/todos', { title: 'Mark', user_id: 1 });
      const res = await http(testApp, 'PATCH', `/todos/${created.body.id}`, { done: true });
      assertStatus(res, 200);
      const check = await http(testApp, 'GET', `/todos/${created.body.id}`);
      assertEqual(check.body.done, 1);
    });
    failed += await test('DELETE /todos/:id removes', async () => {
      const created = await http(testApp, 'POST', '/todos', { title: 'Delete', user_id: 1 });
      const res = await http(testApp, 'DELETE', `/todos/${created.body.id}`);
      assertStatus(res, 204);
      const check = await http(testApp, 'GET', `/todos/${created.body.id}`);
      assertStatus(check, 404);
    });
    console.log(`\n${failed === 0 ? 'All tests passed' : failed + ' test(s) failed'}\n`);
    process.exit(failed);
  })();
} else {
  app.listen(3000, () => console.log('Testing demo :3000 (run `node server.js test` to run tests)'));
}

module.exports = app;
