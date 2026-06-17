// Audit Log Demo — Append-only log of who did what, when, from where, with diff.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE audit_log (
  id TEXT PRIMARY KEY,
  ts INTEGER,
  actor_id TEXT,
  actor_ip TEXT,
  action TEXT,
  resource_type TEXT,
  resource_id TEXT,
  before_state TEXT,
  after_state TEXT,
  metadata TEXT,
  request_id TEXT
)`);
db.exec(`CREATE INDEX idx_audit_actor ON audit_log(actor_id)`);
db.exec(`CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id)`);
db.exec(`CREATE INDEX idx_audit_ts ON audit_log(ts)`);

// === Data we audit ===
const resources = new Map(); // resourceType:resourceId -> { ...data }

function logAudit({ actorId, actorIp, action, resourceType, resourceId, before, after, metadata, requestId }) {
  const id = 'aud_' + crypto.randomBytes(6).toString('hex');
  const entry = {
    id, ts: Date.now(), actor_id: actorId, actor_ip: actorIp, action,
    resource_type: resourceType, resource_id: resourceId,
    before_state: before ? JSON.stringify(before) : null,
    after_state: after ? JSON.stringify(after) : null,
    metadata: metadata ? JSON.stringify(metadata) : null,
    request_id: requestId,
  };
  db.prepare(`INSERT INTO audit_log (id, ts, actor_id, actor_ip, action, resource_type, resource_id, before_state, after_state, metadata, request_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(entry.id, entry.ts, entry.actor_id, entry.actor_ip, entry.action, entry.resource_type, entry.resource_id, entry.before_state, entry.after_state, entry.metadata, entry.request_id);
  return id;
}

function diff(before, after) {
  if (!before) return { type: 'create', after };
  if (!after) return { type: 'delete', before };
  const changes = {};
  for (const key of new Set([...Object.keys(before), ...Object.keys(after)])) {
    if (JSON.stringify(before[key]) !== JSON.stringify(after[key])) changes[key] = { from: before[key], to: after[key] };
  }
  return { type: 'update', changes };
}

// === Middleware: extract actor + request ID ===
app.use((req, res, next) => {
  req.actor = { id: req.headers['x-actor-id'] || 'anonymous', ip: req.ip };
  req.reqId = req.headers['x-request-id'] || 'req_' + crypto.randomBytes(4).toString('hex');
  res.set('X-Request-Id', req.reqId);
  next();
});

// === Sample audited endpoints ===
app.post('/users', (req, res) => {
  const id = 'u_' + crypto.randomBytes(4).toString('hex');
  const user = { id, name: req.body.name, email: req.body.email, role: req.body.role || 'user' };
  resources.set('user:' + id, user);
  logAudit({ actorId: req.actor.id, actorIp: req.actor.ip, action: 'user.create', resourceType: 'user', resourceId: id, before: null, after: user, requestId: req.reqId, metadata: { source: 'api' } });
  res.status(201).json(user);
});

app.put('/users/:id', (req, res) => {
  const id = req.params.id;
  const before = resources.get('user:' + id);
  if (!before) return res.status(404).json({ error: 'not_found' });
  const after = { ...before, ...req.body };
  resources.set('user:' + id, after);
  logAudit({ actorId: req.actor.id, actorIp: req.actor.ip, action: 'user.update', resourceType: 'user', resourceId: id, before, after, requestId: req.reqId });
  res.json(after);
});

app.delete('/users/:id', (req, res) => {
  const id = req.params.id;
  const before = resources.get('user:' + id);
  if (!before) return res.status(404).json({ error: 'not_found' });
  resources.delete('user:' + id);
  logAudit({ actorId: req.actor.id, actorIp: req.actor.ip, action: 'user.delete', resourceType: 'user', resourceId: id, before, after: null, requestId: req.reqId });
  res.status(204).end();
});

// === Query the audit log ===
app.get('/admin/audit', (req, res) => {
  const { actor, resource, action, since, limit = 50 } = req.query;
  let query = 'SELECT * FROM audit_log WHERE 1=1';
  const params = [];
  if (actor) { query += ' AND actor_id = ?'; params.push(actor); }
  if (resource) { query += ' AND resource_type = ?'; params.push(resource); }
  if (action) { query += ' AND action = ?'; params.push(action); }
  if (since) { query += ' AND ts > ?'; params.push(parseInt(since)); }
  query += ' ORDER BY ts DESC LIMIT ?';
  params.push(parseInt(limit));
  const rows = db.prepare(query).all(...params);
  res.json({ count: rows.length, entries: rows.map(r => ({ ...r, before_state: r.before_state ? JSON.parse(r.before_state) : null, after_state: r.after_state ? JSON.parse(r.after_state) : null, metadata: r.metadata ? JSON.parse(r.metadata) : null, diff: r.before_state && r.after_state ? diff(JSON.parse(r.before_state), JSON.parse(r.after_state)) : null })) });
});

app.get('/admin/audit/resource/:type/:id', (req, res) => {
  const rows = db.prepare('SELECT * FROM audit_log WHERE resource_type = ? AND resource_id = ? ORDER BY ts ASC').all(req.params.type, req.params.id);
  res.json({ resource: `${req.params.type}:${req.params.id}`, history: rows.map(r => ({ action: r.action, actor: r.actor_id, at: new Date(r.ts).toISOString() })) });
});

app.get('/admin/audit/actor/:id', (req, res) => {
  const rows = db.prepare('SELECT * FROM audit_log WHERE actor_id = ? ORDER BY ts DESC LIMIT 50').all(req.params.id);
  res.json({ actor: req.params.id, count: rows.length, recent: rows });
});

app.listen(3000, () => console.log('Audit log demo :3000 — POST /users, GET /admin/audit?actor=...'));
module.exports = app;
