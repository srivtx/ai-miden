// Multi-Tenancy Demo — Tenant isolation via row-level scoping, shared schema.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.pragma('foreign_keys = ON');
db.exec(`
  CREATE TABLE tenants (id TEXT PRIMARY KEY, name TEXT, plan TEXT DEFAULT 'free', created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE projects (id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL REFERENCES tenants(id), name TEXT, created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE tasks (id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL REFERENCES tenants(id), project_id TEXT REFERENCES projects(id), title TEXT, done INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')));
  CREATE INDEX idx_projects_tenant ON projects(tenant_id);
  CREATE INDEX idx_tasks_tenant ON tasks(tenant_id);
`);

// === Seed ===
const acme = { id: 't_' + crypto.randomBytes(4).toString('hex'), name: 'Acme Corp' };
const beta = { id: 't_' + crypto.randomBytes(4).toString('hex'), name: 'Beta Inc' };
db.prepare('INSERT INTO tenants (id, name, plan) VALUES (?, ?, ?)').run(acme.id, acme.name, 'pro');
db.prepare('INSERT INTO tenants (id, name, plan) VALUES (?, ?, ?)').run(beta.id, beta.name, 'free');
const acmeProj = 'p_' + crypto.randomBytes(4).toString('hex');
const betaProj = 'p_' + crypto.randomBytes(4).toString('hex');
db.prepare('INSERT INTO projects (id, tenant_id, name) VALUES (?, ?, ?)').run(acmeProj, acme.id, 'Acme Website');
db.prepare('INSERT INTO projects (id, tenant_id, name) VALUES (?, ?, ?)').run(betaProj, beta.id, 'Beta Mobile App');
for (let i = 0; i < 5; i++) db.prepare('INSERT INTO tasks (id, tenant_id, project_id, title) VALUES (?, ?, ?, ?)').run('tk_' + crypto.randomBytes(3).toString('hex'), acme.id, acmeProj, `Acme task ${i}`);
for (let i = 0; i < 5; i++) db.prepare('INSERT INTO tasks (id, tenant_id, project_id, title) VALUES (?, ?, ?, ?)').run('tk_' + crypto.randomBytes(3).toString('hex'), beta.id, betaProj, `Beta task ${i}`);

// === Tenant resolution middleware ===
// Tenant comes from header X-Tenant-Id, subdomain, or JWT claim
function tenantMiddleware(req, res, next) {
  const tenantId = req.headers['x-tenant-id'];
  if (!tenantId) return res.status(400).json({ error: 'missing_tenant', hint: 'set X-Tenant-Id header' });
  const tenant = db.prepare('SELECT * FROM tenants WHERE id = ?').get(tenantId);
  if (!tenant) return res.status(404).json({ error: 'tenant_not_found' });
  req.tenant = tenant;
  next();
}

// === Helper: scope every query by tenant_id ===
function tenantQuery(tenantId, table) {
  return db.prepare(`SELECT * FROM ${table} WHERE tenant_id = ?`);
}

function tenantInsert(tenantId, table, data) {
  const cols = Object.keys(data);
  const placeholders = cols.map(() => '?').join(', ');
  const values = cols.map(c => data[c]);
  return db.prepare(`INSERT INTO ${table} (tenant_id, ${cols.join(', ')}) VALUES (?, ${placeholders})`).run(tenantId, ...values);
}

// === Endpoints ===
app.get('/me', tenantMiddleware, (req, res) => res.json({ tenant: req.tenant }));

app.get('/projects', tenantMiddleware, (req, res) => {
  const projects = tenantQuery(req.tenant.id, 'projects').all(req.tenant.id);
  res.json({ tenant: req.tenant.name, count: projects.length, projects });
});

app.post('/projects', tenantMiddleware, (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'p_' + crypto.randomBytes(4).toString('hex');
  tenantInsert(req.tenant.id, 'projects', { id, name: req.body.name });
  res.status(201).json({ id, name: req.body.name, tenant_id: req.tenant.id });
});

app.get('/tasks', tenantMiddleware, (req, res) => {
  const tasks = tenantQuery(req.tenant.id, 'tasks').all(req.tenant.id);
  res.json({ tenant: req.tenant.name, count: tasks.length, tasks });
});

// === Isolation test: try to access another tenant's data ===
app.get('/tasks/:id', tenantMiddleware, (req, res) => {
  const task = db.prepare('SELECT * FROM tasks WHERE id = ? AND tenant_id = ?').get(req.params.id, req.tenant.id);
  task ? res.json(task) : res.status(404).json({ error: 'not_found_or_not_yours' });
});

app.get('/admin/tenants', (req, res) => res.json({ tenants: db.prepare('SELECT * FROM tenants').all() }));

app.listen(3000, () => console.log(`Multi-tenancy demo :3000 — use X-Tenant-Id: ${acme.id} or ${beta.id}`));
module.exports = app;
