// Issue Tracker (Jira-like) — Projects, issues, comments, labels, status workflow.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const projects = []; const issues = []; const comments = []; const activity = [];
let pId = 1, iId = 1, cId = 1, aId = 1;
const STATUSES = ['open', 'in_progress', 'in_review', 'done', 'closed'];
const PRIORITIES = ['lowest', 'low', 'medium', 'high', 'highest'];
const TYPES = ['bug', 'feature', 'task', 'improvement'];

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }
function log(projectId, userId, action, target, details) { activity.push({ id: aId++, projectId, userId, action, target, details: details || {}, time: new Date().toISOString() }); }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Projects
app.post('/projects', auth, (req, res) => {
  const { key, name, description, members } = req.body;
  if (!key || !name) return res.status(400).json({ error: 'key and name required' });
  if (projects.find(p => p.key === key.toUpperCase())) return res.status(409).json({ error: 'Project key exists' });
  const p = { id: pId++, key: key.toUpperCase(), name, description: description || '', members: members || [req.user.id], issueCount: 0, createdAt: new Date().toISOString() };
  projects.push(p);
  res.status(201).json(p);
});

app.get('/projects', auth, (req, res) => res.json(projects.filter(p => p.members.includes(req.user.id))));

// Issues
app.post('/projects/:key/issues', auth, (req, res) => {
  const project = projects.find(p => p.key === req.params.key.toUpperCase());
  if (!project) return res.status(404).json({ error: 'Project not found' });
  if (!project.members.includes(req.user.id)) return res.status(403).json({ error: 'Not a project member' });
  const { title, description, type, priority, assigneeId, labels, dueDate } = req.body;
  if (!title) return res.status(400).json({ error: 'title required' });
  const issue = { id: iId++, projectId: project.id, key: `${project.key}-${project.issueCount + 1}`, title, description: description || '', type: TYPES.includes(type) ? type : 'task', priority: PRIORITIES.includes(priority) ? priority : 'medium', status: 'open', reporterId: req.user.id, assigneeId: assigneeId || null, labels: labels || [], dueDate: dueDate || null, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  issues.push(issue);
  project.issueCount++;
  log(project.id, req.user.id, 'created_issue', issue.key);
  res.status(201).json(issue);
});

app.get('/projects/:key/issues', auth, (req, res) => {
  const project = projects.find(p => p.key === req.params.key.toUpperCase());
  if (!project) return res.status(404).json({ error: 'Not found' });
  let result = issues.filter(i => i.projectId === project.id);
  if (req.query.status) result = result.filter(i => i.status === req.query.status);
  if (req.query.assignee) result = result.filter(i => i.assigneeId === parseInt(req.query.assignee));
  if (req.query.reporter) result = result.filter(i => i.reporterId === parseInt(req.query.reporter));
  if (req.query.type) result = result.filter(i => i.type === req.query.type);
  if (req.query.priority) result = result.filter(i => i.priority === req.query.priority);
  if (req.query.label) result = result.filter(i => i.labels.includes(req.query.label));
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(i => i.title.toLowerCase().includes(q) || i.description.toLowerCase().includes(q)); }
  const sortField = ['priority', 'createdAt', 'updatedAt'].includes(req.query.sort) ? req.query.sort : 'createdAt';
  result.sort((a, b) => (a[sortField] > b[sortField] ? 1 : -1) * (req.query.order === 'asc' ? 1 : -1));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 20;
  const total = result.length;
  res.json({ total, page, data: result.slice((page - 1) * limit, page * limit) });
});

app.patch('/issues/:key', auth, (req, res) => {
  const issue = issues.find(i => i.key === req.params.key);
  if (!issue) return res.status(404).json({ error: 'Not found' });
  const project = projects.find(p => p.id === issue.projectId);
  if (!project.members.includes(req.user.id)) return res.status(403).json({ error: 'Not a member' });
  if (req.body.title) issue.title = req.body.title;
  if (req.body.description !== undefined) issue.description = req.body.description;
  if (req.body.status) { if (!STATUSES.includes(req.body.status)) return res.status(400).json({ error: `Invalid status. Use: ${STATUSES.join(', ')}` }); if (issue.status !== req.body.status) { log(issue.projectId, req.user.id, 'status_change', issue.key, { from: issue.status, to: req.body.status }); issue.status = req.body.status; } }
  if (req.body.priority) issue.priority = req.body.priority;
  if (req.body.assigneeId !== undefined) { log(issue.projectId, req.user.id, 'assignee_change', issue.key, { from: issue.assigneeId, to: req.body.assigneeId }); issue.assigneeId = req.body.assigneeId; }
  if (req.body.labels) issue.labels = req.body.labels;
  issue.updatedAt = new Date().toISOString();
  res.json(issue);
});

app.post('/issues/:key/comments', auth, (req, res) => {
  const issue = issues.find(i => i.key === req.params.key);
  if (!issue) return res.status(404).json({ error: 'Not found' });
  if (!req.body.body) return res.status(400).json({ error: 'body required' });
  const c = { id: cId++, issueId: issue.id, authorId: req.user.id, body: req.body.body, createdAt: new Date().toISOString() };
  comments.push(c);
  res.status(201).json({ ...c, author: users.find(u => u.id === req.user.id)?.name });
});

app.get('/projects/:key/activity', auth, (req, res) => {
  const project = projects.find(p => p.key === req.params.key.toUpperCase());
  if (!project) return res.status(404).json({ error: 'Not found' });
  res.json(activity.filter(a => a.projectId === project.id).slice(-30).reverse().map(a => ({ ...a, user: users.find(u => u.id === a.userId)?.name })));
});

app.listen(3000, () => console.log('Issue Tracker :3000'));
module.exports = app;
