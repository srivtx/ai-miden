// Task Manager API — Full REST app. Auth, CRUD, filter, sort, paginate, tests.
// Run: npm start   Test: npm test

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const Joi = require('joi');

const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
// ---- Database (in-memory) ----
const users = [];
const tasks = [];
let taskId = 1;

// ---- Helpers ----
function generateToken(user) { return jwt.sign({ id: user.id }, SECRET, { expiresIn: '1h' }); }

function asyncHandler(fn) { return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next); }

// ---- Auth Middleware ----
function auth(req, res, next) {
  try {
    req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET);
    next();
  } catch { res.status(401).json({ error: 'Authentication required' }); }
}

// ---- Validation Schemas ----
const schemas = {
  register: Joi.object({ name: Joi.string().min(2).max(50).required(), email: Joi.string().email().required(), password: Joi.string().min(6).required() }),
  login: Joi.object({ email: Joi.string().email().required(), password: Joi.string().required() }),
  task: Joi.object({ title: Joi.string().min(1).max(200).required(), description: Joi.string().max(1000).allow(''), priority: Joi.string().valid('low', 'medium', 'high').default('medium'), status: Joi.string().valid('todo', 'in_progress', 'done').default('todo'), dueDate: Joi.date().iso().allow(null) }),
  taskUpdate: Joi.object({ title: Joi.string().min(1).max(200), description: Joi.string().max(1000).allow(''), priority: Joi.string().valid('low', 'medium', 'high'), status: Joi.string().valid('todo', 'in_progress', 'done'), dueDate: Joi.date().iso().allow(null) }),
};

function validate(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, { abortEarly: false, stripUnknown: true });
    if (error) return res.status(400).json({ errors: error.details.map(d => d.message) });
    req.body = value;
    next();
  };
}

// ---- AUTH ROUTES ----
app.post('/auth/register', validate(schemas.register), asyncHandler(async (req, res) => {
  if (users.find(u => u.email === req.body.email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name: req.body.name, email: req.body.email, password: await bcrypt.hash(req.body.password, 10) };
  users.push(user);
  res.status(201).json({ user: { id: user.id, name: user.name, email: user.email }, token: generateToken(user) });
}));

app.post('/auth/login', validate(schemas.login), asyncHandler(async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid credentials' });
  res.json({ user: { id: user.id, name: user.name, email: user.email }, token: generateToken(user) });
}));

// ---- TASK ROUTES (protected) ----
app.post('/tasks', auth, validate(schemas.task), (req, res) => {
  const task = { id: taskId++, userId: req.user.id, ...req.body, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  tasks.push(task);
  res.status(201).json(task);
});

app.get('/tasks', auth, (req, res) => {
  let result = tasks.filter(t => t.userId === req.user.id);

  // Filters
  if (req.query.status) result = result.filter(t => t.status === req.query.status);
  if (req.query.priority) result = result.filter(t => t.priority === req.query.priority);
  if (req.query.search) {
    const q = req.query.search.toLowerCase();
    result = result.filter(t => t.title.toLowerCase().includes(q) || t.description.toLowerCase().includes(q));
  }
  if (req.query.dueBefore) result = result.filter(t => t.dueDate && new Date(t.dueDate) <= new Date(req.query.dueBefore));
  if (req.query.overdue === 'true') result = result.filter(t => t.dueDate && new Date(t.dueDate) < new Date() && t.status !== 'done');

  // Sort
  const sortField = ['title', 'priority', 'status', 'dueDate', 'createdAt'].includes(req.query.sort) ? req.query.sort : 'createdAt';
  const order = req.query.order === 'asc' ? 1 : -1;
  result.sort((a, b) => {
    const av = a[sortField] || ''; const bv = b[sortField] || '';
    return (av > bv ? 1 : -1) * order;
  });

  // Paginate
  const page = Math.max(1, parseInt(req.query.page) || 1);
  const limit = Math.min(100, Math.max(1, parseInt(req.query.limit) || 20));
  const total = result.length;
  result = result.slice((page - 1) * limit, page * limit);

  res.json({ total, page, pages: Math.ceil(total / limit), data: result });
});

app.get('/tasks/:id', auth, (req, res) => {
  const task = tasks.find(t => t.id === parseInt(req.params.id) && t.userId === req.user.id);
  if (!task) return res.status(404).json({ error: 'Task not found' });
  res.json(task);
});

app.patch('/tasks/:id', auth, validate(schemas.taskUpdate), (req, res) => {
  const task = tasks.find(t => t.id === parseInt(req.params.id) && t.userId === req.user.id);
  if (!task) return res.status(404).json({ error: 'Task not found' });
  Object.assign(task, req.body, { updatedAt: new Date().toISOString() });
  res.json(task);
});

app.delete('/tasks/:id', auth, (req, res) => {
  const idx = tasks.findIndex(t => t.id === parseInt(req.params.id) && t.userId === req.user.id);
  if (idx === -1) return res.status(404).json({ error: 'Task not found' });
  tasks.splice(idx, 1);
  res.status(204).send();
});

// ---- Stats (extra endpoint) ----
app.get('/tasks/stats/summary', auth, (req, res) => {
  const userTasks = tasks.filter(t => t.userId === req.user.id);
  res.json({
    total: userTasks.length,
    byStatus: { todo: userTasks.filter(t => t.status === 'todo').length, in_progress: userTasks.filter(t => t.status === 'in_progress').length, done: userTasks.filter(t => t.status === 'done').length },
    byPriority: { low: userTasks.filter(t => t.priority === 'low').length, medium: userTasks.filter(t => t.priority === 'medium').length, high: userTasks.filter(t => t.priority === 'high').length },
    overdue: userTasks.filter(t => t.dueDate && new Date(t.dueDate) < new Date() && t.status !== 'done').length,
  });
});

// ---- Error handler ----
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Task API: http://localhost:${PORT}`));

// Export for testing
module.exports = app;
