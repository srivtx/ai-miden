// Helpdesk API — Step 16. Adds: tickets, agents, assignments, SLA tracking, priority.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE agents (id TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE, role TEXT DEFAULT 'agent')`);
db.exec(`CREATE TABLE tickets (id TEXT PRIMARY KEY, requester_id TEXT, assignee_id TEXT, subject TEXT, body TEXT, status TEXT DEFAULT 'open', priority TEXT DEFAULT 'normal', category TEXT, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')), resolved_at TEXT)`);
db.exec(`CREATE TABLE ticket_events (id TEXT PRIMARY KEY, ticket_id TEXT, type TEXT, from_value TEXT, to_value TEXT, actor_id TEXT, body TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE INDEX idx_tickets_status ON tickets(status, priority)`);
db.exec(`CREATE INDEX idx_tickets_assignee ON tickets(assignee_id)`);

const SLA_HOURS = { critical: 1, high: 4, normal: 24, low: 72 };

app.get('/agents', (req, res) => res.json({ agents: db.prepare('SELECT a.*, (SELECT COUNT(*) FROM tickets WHERE assignee_id = a.id AND status != "closed") as open_tickets FROM agents a').all() }));

app.post('/agents', (req, res) => {
  if (!req.body.name || !req.body.email) return res.status(422).json({ error: 'missing_fields' });
  const id = 'ag_' + crypto.randomBytes(4).toString('hex');
  try { db.prepare('INSERT INTO agents (id, name, email, role) VALUES (?, ?, ?, ?)').run(id, req.body.name, req.body.email, req.body.role || 'agent'); res.status(201).json({ id }); }
  catch { res.status(409).json({ error: 'email_taken' }); }
});

// === Public: anyone can create a ticket ===
app.post('/tickets', (req, res) => {
  if (!req.body.subject) return res.status(422).json({ error: 'missing_subject' });
  const priority = ['low', 'normal', 'high', 'critical'].includes(req.body.priority) ? req.body.priority : 'normal';
  const id = 'tk_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO tickets (id, requester_id, subject, body, priority, category) VALUES (?, ?, ?, ?, ?, ?)').run(id, req.body.requester_id || 'anon', req.body.subject, req.body.body || '', priority, req.body.category || null);
  db.prepare('INSERT INTO ticket_events (id, ticket_id, type, to_value, actor_id) VALUES (?, ?, ?, ?, ?)').run('ev_' + crypto.randomBytes(3).toString('hex'), id, 'created', priority, req.body.requester_id || 'anon');
  res.status(201).json(db.prepare('SELECT * FROM tickets WHERE id = ?').get(id));
});

app.get('/tickets', (req, res) => {
  const { status, priority, assignee, breached } = req.query;
  let query = 'SELECT t.*, a.name as assignee_name FROM tickets t LEFT JOIN agents a ON a.id = t.assignee_id WHERE 1=1';
  const params = [];
  if (status) { query += ' AND t.status = ?'; params.push(status); }
  if (priority) { query += ' AND t.priority = ?'; params.push(priority); }
  if (assignee) { query += ' AND a.name LIKE ?'; params.push('%' + assignee + '%'); }
  let tickets = db.prepare(query).all(...params);
  // Calculate SLA status
  for (const t of tickets) {
    const slaMs = (SLA_HOURS[t.priority] || 24) * 3600000;
    const elapsed = Date.now() - new Date(t.created_at + 'Z').getTime();
    t.sla = { hoursAllowed: SLA_HOURS[t.priority], hoursElapsed: Math.round(elapsed / 3600000 * 10) / 10, breached: t.status !== 'closed' && elapsed > slaMs };
  }
  if (breached === 'true') tickets = tickets.filter(t => t.sla.breached);
  res.json({ count: tickets.length, tickets });
});

app.get('/tickets/:id', (req, res) => {
  const ticket = db.prepare('SELECT t.*, a.name as assignee_name FROM tickets t LEFT JOIN agents a ON a.id = t.assignee_id WHERE t.id = ?').get(req.params.id);
  if (!ticket) return res.status(404).json({ error: 'not_found' });
  ticket.events = db.prepare('SELECT * FROM ticket_events WHERE ticket_id = ? ORDER BY created_at ASC').all(ticket.id);
  res.json(ticket);
});

// === Agent actions ===
app.post('/tickets/:id/assign', (req, res) => {
  if (!req.agentId) return res.status(401).json({ error: 'agent_auth_required' });
  const ticket = db.prepare('SELECT * FROM tickets WHERE id = ?').get(req.params.id);
  if (!ticket) return res.status(404).json({ error: 'not_found' });
  const agent = db.prepare('SELECT * FROM agents WHERE id = ?').get(req.body.assignee_id);
  if (!agent) return res.status(422).json({ error: 'invalid_assignee' });
  db.prepare('UPDATE tickets SET assignee_id = ?, updated_at = ? WHERE id = ?').run(agent.id, new Date().toISOString(), ticket.id);
  db.prepare('INSERT INTO ticket_events (id, ticket_id, type, from_value, to_value, actor_id) VALUES (?, ?, ?, ?, ?, ?)').run('ev_' + crypto.randomBytes(3).toString('hex'), ticket.id, 'assigned', ticket.assignee_id, agent.id, req.agentId);
  res.json({ ticket_id: ticket.id, assignee: agent.name });
});

app.post('/tickets/:id/comment', (req, res) => {
  if (!req.agentId) return res.status(401).json({ error: 'agent_auth_required' });
  if (!req.body.body) return res.status(422).json({ error: 'missing_body' });
  db.prepare('INSERT INTO ticket_events (id, ticket_id, type, body, actor_id) VALUES (?, ?, ?, ?, ?)').run('ev_' + crypto.randomBytes(3).toString('hex'), req.params.id, 'comment', req.body.body, req.agentId);
  db.prepare('UPDATE tickets SET updated_at = ? WHERE id = ?').run(new Date().toISOString(), req.params.id);
  res.status(201).json({ added: true });
});

app.post('/tickets/:id/resolve', (req, res) => {
  if (!req.agentId) return res.status(401).json({ error: 'agent_auth_required' });
  const now = new Date().toISOString();
  db.prepare('UPDATE tickets SET status = ?, resolved_at = ?, updated_at = ? WHERE id = ?').run('resolved', now, now, req.params.id);
  db.prepare('INSERT INTO ticket_events (id, ticket_id, type, to_value, actor_id) VALUES (?, ?, ?, ?, ?)').run('ev_' + crypto.randomBytes(3).toString('hex'), req.params.id, 'resolved', 'resolved', req.agentId);
  res.json({ resolved: true });
});

app.use((req, res, next) => { req.agentId = req.headers['x-agent-id']; next(); });

app.listen(3000, () => console.log('Helpdesk API :3000 — X-Agent-Id header for agent actions'));
module.exports = app;
