// 12-todo-webhooks: Subscribe to events. When a todo changes, we POST to your URL.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const SECRET = 'webhook-secret';
const db = new Database(':memory:');
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0)`);
db.exec(`CREATE TABLE webhooks (id TEXT PRIMARY KEY, url TEXT, secret TEXT, events TEXT)`);
db.exec(`CREATE TABLE deliveries (id INTEGER PRIMARY KEY AUTOINCREMENT, webhook_id TEXT, event TEXT, payload TEXT, status TEXT, attempts INTEGER DEFAULT 0, last_error TEXT, created_at TEXT DEFAULT (datetime('now')))`);

function sign(payload, secret) {
  return 'sha256=' + crypto.createHmac('sha256', secret).update(payload).digest('hex');
}

// Simulated webhook delivery
async function deliver(webhookId, url, secret, event, payload) {
  const body = JSON.stringify({ event, data: payload, ts: Date.now() });
  const sig = sign(body, secret);
  const deliveryId = db.prepare('INSERT INTO deliveries (webhook_id, event, payload, status) VALUES (?, ?, ?, ?)').run(webhookId, event, body, 'pending').lastInsertRowid;
  console.log(`[webhook] Would POST to ${url}`);
  console.log(`[webhook]   X-Signature: ${sig}`);
  console.log(`[webhook]   Body: ${body}`);
  db.prepare('UPDATE deliveries SET status = ?, attempts = attempts + 1 WHERE id = ?').run('delivered', deliveryId);
  return { ok: true };
}

// Subscribe to events
app.post('/webhooks', (req, res) => {
  const { url, events } = req.body;
  if (!url) return res.status(422).json({ error: 'url required' });
  const id = 'wh_' + crypto.randomBytes(4).toString('hex');
  const secret = crypto.randomBytes(8).toString('hex');
  db.prepare('INSERT INTO webhooks (id, url, secret, events) VALUES (?, ?, ?, ?)').run(id, url, secret, JSON.stringify(events || ['*']));
  res.status(201).json({ id, url, events: events || ['*'], secret });
});

app.get('/webhooks', (req, res) => res.json({ webhooks: db.prepare('SELECT id, url, events FROM webhooks').all() }));

// Trigger an event
async function fire(event, payload) {
  const webhooks = db.prepare('SELECT * FROM webhooks').all();
  for (const wh of webhooks) {
    const events = JSON.parse(wh.events);
    if (events.includes('*') || events.includes(event)) {
      await deliver(wh.id, wh.url, wh.secret, event, payload);
    }
  }
}

// CRUD with webhook firing
app.post('/todos', async (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const r = db.prepare('INSERT INTO todos (title) VALUES (?)').run(req.body.title);
  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(r.lastInsertRowid);
  await fire('todo.created', todo);
  res.status(201).json(todo);
});

app.patch('/todos/:id', async (req, res) => {
  const id = parseInt(req.params.id);
  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(id);
  if (!todo) return res.status(404).json({ error: 'not found' });
  const updates = [];
  const params = [];
  if (req.body.title !== undefined) { updates.push('title = ?'); params.push(req.body.title); }
  if (req.body.done !== undefined) { updates.push('done = ?'); params.push(req.body.done ? 1 : 0); }
  if (!updates.length) return res.status(422).json({ error: 'no updates' });
  params.push(id);
  db.prepare(`UPDATE todos SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  const updated = db.prepare('SELECT * FROM todos WHERE id = ?').get(id);
  await fire('todo.updated', updated);
  res.json(updated);
});

// See deliveries
app.get('/webhooks/:id/deliveries', (req, res) => {
  const rows = db.prepare('SELECT * FROM deliveries WHERE webhook_id = ? ORDER BY id DESC LIMIT 50').all(req.params.id);
  res.json({ count: rows.length, deliveries: rows });
});

app.listen(3000, () => console.log('12-todo-webhooks on :3000'));
