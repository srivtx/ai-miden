// 05-todo-multi-tenant: Users belong to tenants (teams/workspaces). Data isolation by tenant.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
const db = new Database(':memory:');
db.exec(`
  CREATE TABLE tenants (id TEXT PRIMARY KEY, name TEXT);
  CREATE TABLE users (id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, email TEXT, role TEXT DEFAULT 'member');
  CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL, user_id TEXT, title TEXT, done INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')));
`);

// Tenant resolution: from header
function tenantMiddleware(req, res, next) {
  const tenantId = req.headers['x-tenant-id'];
  if (!tenantId) return res.status(400).json({ error: 'missing X-Tenant-Id' });
  req.tenantId = tenantId;
  next();
}

// Auth
function auth(req, res, next) {
  const token = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  try { req.user = jwt.verify(token, SECRET); next(); }
  catch { res.status(401).json({ error: 'unauthorized' }); }
}

// Create a tenant (would be admin-only in real apps)
app.post('/tenants', (req, res) => {
  const id = 't_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO tenants (id, name) VALUES (?, ?)').run(id, req.body.name);
  res.status(201).json({ id, name: req.body.name });
});

// Add a user to a tenant
app.post('/tenants/:tenantId/users', (req, res) => {
  const tenantId = req.params.tenantId;
  const id = 'u_' + crypto.randomBytes(4).toString('hex');
  const token = jwt.sign({ sub: id, tenantId, role: req.body.role || 'member' }, SECRET, { expiresIn: '7d' });
  db.prepare('INSERT INTO users (id, tenant_id, email, role) VALUES (?, ?, ?, ?)').run(id, tenantId, req.body.email, req.body.role || 'member');
  res.status(201).json({ id, token, tenantId, role: req.body.role || 'member' });
});

// Todos — filtered by tenant
app.get('/todos', auth, tenantMiddleware, (req, res) => {
  if (req.user.tenantId !== req.tenantId) return res.status(403).json({ error: 'wrong tenant' });
  const todos = db.prepare('SELECT * FROM todos WHERE tenant_id = ? ORDER BY id DESC').all(req.tenantId);
  res.json({ count: todos.length, todos });
});

app.post('/todos', auth, tenantMiddleware, (req, res) => {
  if (req.user.tenantId !== req.tenantId) return res.status(403).json({ error: 'wrong tenant' });
  const r = db.prepare('INSERT INTO todos (tenant_id, user_id, title) VALUES (?, ?, ?)').run(req.tenantId, req.user.sub, req.body.title);
  res.status(201).json(db.prepare('SELECT * FROM todos WHERE id = ?').get(r.lastInsertRowid));
});

app.listen(3000, () => console.log('05-todo-multi-tenant on :3000 (use X-Tenant-Id header)'));
