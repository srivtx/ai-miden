// Customer Support / Ticketing — Tickets, agents, customers, replies, status workflow.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const tickets = []; const messages = []; const customers = []; let tId = 1, mId = 1, custId = 1;
const STATUSES = ['new', 'open', 'pending', 'on_hold', 'solved', 'closed'];
const PRIORITIES = ['low', 'normal', 'high', 'urgent'];

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }
function role(r) { return (req, res, next) => req.user.role === r ? next() : res.status(403).json({ error: 'Forbidden' }); }

app.post('/auth/register', async (req, res) => {
  const { name, email, password, role: r } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), role: r === 'agent' ? 'agent' : 'customer' };
  users.push(user);
  if (user.role === 'customer') customers.push({ id: custId++, userId: user.id, tickets: 0 });
  res.status(201).json({ user: { id: user.id, name, email, role: user.role }, token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ user: { id: user.id, name: user.name, email: user.email, role: user.role }, token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '24h' }) });
});

// Tickets
app.post('/tickets', auth, (req, res) => {
  const { subject, message, priority, category, tags } = req.body;
  if (!subject || !message) return res.status(400).json({ error: 'subject and message required' });
  const t = { id: tId++, number: tId, customerId: req.user.id, subject, status: 'new', priority: PRIORITIES.includes(priority) ? priority : 'normal', category: category || 'general', tags: tags || [], assigneeId: null, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  tickets.push(t);
  messages.push({ id: mId++, ticketId: t.id, authorId: req.user.id, body: message, isInternal: false, createdAt: new Date().toISOString() });
  const c = customers.find(c => c.userId === req.user.id); if (c) c.tickets++;
  res.status(201).json(t);
});

app.get('/tickets', auth, (req, res) => {
  let result = tickets;
  // Customers see their own. Agents see all.
  if (req.user.role === 'customer') result = result.filter(t => t.customerId === req.user.id);
  if (req.query.status) result = result.filter(t => t.status === req.query.status);
  if (req.query.priority) result = result.filter(t => t.priority === req.query.priority);
  if (req.query.assignee) result = result.filter(t => t.assigneeId === parseInt(req.query.assignee));
  if (req.query.unassigned === 'true') result = result.filter(t => !t.assigneeId);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(t => t.subject.toLowerCase().includes(q) || t.number.toString().includes(q)); }
  result.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  res.json(result);
});

app.get('/tickets/:id', auth, (req, res) => {
  const t = tickets.find(t => t.id === parseInt(req.params.id));
  if (!t) return res.status(404).json({ error: 'Not found' });
  if (req.user.role === 'customer' && t.customerId !== req.user.id) return res.status(403).json({ error: 'Not your ticket' });
  res.json({ ...t, customer: users.find(u => u.id === t.customerId)?.name, assignee: t.assigneeId ? users.find(u => u.id === t.assigneeId)?.name : null, messages: messages.filter(m => m.ticketId === t.id && (req.user.role === 'agent' || !m.isInternal)).map(m => ({ ...m, author: users.find(u => u.id === m.authorId)?.name })) });
});

app.post('/tickets/:id/messages', auth, (req, res) => {
  const t = tickets.find(t => t.id === parseInt(req.params.id));
  if (!t) return res.status(404).json({ error: 'Not found' });
  if (req.user.role === 'customer' && t.customerId !== req.user.id) return res.status(403).json({ error: 'Not your ticket' });
  if (!req.body.body) return res.status(400).json({ error: 'message body required' });
  const m = { id: mId++, ticketId: t.id, authorId: req.user.id, body: req.body.body, isInternal: req.body.internal === true && req.user.role === 'agent', createdAt: new Date().toISOString() };
  messages.push(m);
  t.updatedAt = new Date().toISOString();
  if (t.status === 'new' && req.user.role === 'agent') t.status = 'open';
  res.status(201).json(m);
});

app.patch('/tickets/:id', auth, role('agent'), (req, res) => {
  const t = tickets.find(t => t.id === parseInt(req.params.id));
  if (!t) return res.status(404).json({ error: 'Not found' });
  if (req.body.status && !STATUSES.includes(req.body.status)) return res.status(400).json({ error: `Invalid status. Use: ${STATUSES.join(', ')}` });
  if (req.body.status) t.status = req.body.status;
  if (req.body.priority) t.priority = req.body.priority;
  if (req.body.assigneeId !== undefined) t.assigneeId = req.body.assigneeId;
  if (req.body.tags) t.tags = req.body.tags;
  t.updatedAt = new Date().toISOString();
  res.json(t);
});

// Agent dashboard
app.get('/agents/stats', auth, role('agent'), (req, res) => {
  const myTickets = tickets.filter(t => t.assigneeId === req.user.id);
  res.json({ assignedToMe: myTickets.length, open: tickets.filter(t => t.status === 'open').length, pending: tickets.filter(t => t.status === 'pending').length, unassigned: tickets.filter(t => !t.assigneeId && t.status === 'open').length, urgent: tickets.filter(t => t.priority === 'urgent' && t.status !== 'closed').length, total: tickets.length });
});

app.listen(3000, () => console.log('Support Tickets :3000'));
module.exports = app;
