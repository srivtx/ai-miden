// 07-todo-audit: Log every change to a separate audit_log table. Who, what, when, from where.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0, version INTEGER DEFAULT 1, created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_type TEXT, entity_id TEXT, action TEXT, actor_id TEXT, actor_ip TEXT, before_state TEXT, after_state TEXT, request_id TEXT, ts TEXT DEFAULT (datetime('now')));
`);

function audit({ entityType, entityId, action, actorId, actorIp, before, after, requestId }) {
  db.prepare(`INSERT INTO audit_log (entity_type, entity_id, action, actor_id, actor_ip, before_state, after_state, request_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`)
    .run(entityType, String(entityId), action, actorId || null, actorIp || null,
         before ? JSON.stringify(before) : null,
         after ? JSON.stringify(after) : null,
         requestId || null);
}

app.use((req, res, next) => {
  req.requestId = req.headers['x-request-id'] || 'req_' + crypto.randomBytes(4).toString('hex');
  res.set('X-Request-Id', req.requestId);
  next();
});

app.post('/todos', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const r = db.prepare('INSERT INTO todos (title) VALUES (?)').run(req.body.title);
  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(r.lastInsertRowid);
  audit({ entityType: 'todo', entityId: todo.id, action: 'create', actorId: req.body.actorId, actorIp: req.ip, after: todo, requestId: req.requestId });
  res.status(201).json(todo);
});

app.patch('/todos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const before = db.prepare('SELECT * FROM todos WHERE id = ?').get(id);
  if (!before) return res.status(404).json({ error: 'not found' });
  const updates = [];
  const params = [];
  if (req.body.title !== undefined) { updates.push('title = ?'); params.push(req.body.title); }
  if (req.body.done !== undefined) { updates.push('done = ?'); params.push(req.body.done ? 1 : 0); }
  if (!updates.length) return res.status(422).json({ error: 'no updates' });
  updates.push('version = version + 1');
  params.push(id);
  db.prepare(`UPDATE todos SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  const after = db.prepare('SELECT * FROM todos WHERE id = ?').get(id);
  audit({ entityType: 'todo', entityId: id, action: 'update', actorId: req.body.actorId, actorIp: req.ip, before, after, requestId: req.requestId });
  res.json(after);
});

app.delete('/todos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const before = db.prepare('SELECT * FROM todos WHERE id = ?').get(id);
  if (!before) return res.status(404).json({ error: 'not found' });
  db.prepare('DELETE FROM todos WHERE id = ?').run(id);
  audit({ entityType: 'todo', entityId: id, action: 'delete', actorId: req.body.actorId, actorIp: req.ip, before, requestId: req.requestId });
  res.status(204).end();
});

// Query the audit log
app.get('/audit', (req, res) => {
  const { entity_id, action, actor_id } = req.query;
  let query = 'SELECT * FROM audit_log WHERE 1=1';
  const params = [];
  if (entity_id) { query += ' AND entity_id = ?'; params.push(entity_id); }
  if (action) { query += ' AND action = ?'; params.push(action); }
  if (actor_id) { query += ' AND actor_id = ?'; params.push(actor_id); }
  query += ' ORDER BY id DESC LIMIT 100';
  const entries = db.prepare(query).all(...params).map(e => ({
    ...e,
    before_state: e.before_state ? JSON.parse(e.before_state) : null,
    after_state: e.after_state ? JSON.parse(e.after_state) : null,
  }));
  res.json({ count: entries.length, entries });
});

app.listen(3000, () => console.log('07-todo-audit on :3000'));
