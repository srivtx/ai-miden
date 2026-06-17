// Expense Tracker — Log expenses, categorize, date range, monthly totals, budgets.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const expenses = [];
const categories = ['food', 'transport', 'housing', 'utilities', 'entertainment', 'health', 'shopping', 'other'];
let expId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), monthlyBudget: { food: 500, transport: 200, housing: 1500, utilities: 300, entertainment: 200, health: 100, shopping: 300, other: 200 } };
  users.push(user);
  res.status(201).json({ user: { id: user.id, name, email }, token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

app.post('/expenses', auth, (req, res) => {
  const { amount, category, description, date } = req.body;
  if (!amount || amount <= 0) return res.status(400).json({ error: 'Valid amount required' });
  if (!categories.includes(category)) return res.status(400).json({ error: `Invalid category. Use: ${categories.join(', ')}` });
  const exp = { id: expId++, userId: req.user.id, amount: parseFloat(amount), category, description: description || '', date: date || new Date().toISOString(), createdAt: new Date().toISOString() };
  expenses.push(exp);
  res.status(201).json(exp);
});

app.get('/expenses', auth, (req, res) => {
  let result = expenses.filter(e => e.userId === req.user.id);
  if (req.query.category) result = result.filter(e => e.category === req.query.category);
  if (req.query.startDate) result = result.filter(e => e.date >= req.query.startDate);
  if (req.query.endDate) result = result.filter(e => e.date <= req.query.endDate);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(e => e.description.toLowerCase().includes(q)); }
  if (req.query.minAmount) result = result.filter(e => e.amount >= parseFloat(req.query.minAmount));
  if (req.query.maxAmount) result = result.filter(e => e.amount <= parseFloat(req.query.maxAmount));
  result.sort((a, b) => new Date(b.date) - new Date(a.date));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 50;
  const total = result.length; result = result.slice((page - 1) * limit, page * limit);
  res.json({ total, page, pages: Math.ceil(total / limit), data: result });
});

app.get('/expenses/summary', auth, (req, res) => {
  const userExpenses = expenses.filter(e => e.userId === req.user.id);
  const now = new Date(); const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
  const thisMonth = userExpenses.filter(e => e.date >= monthStart);
  const byCategory = {}; categories.forEach(c => byCategory[c] = { total: 0, count: 0, thisMonth: 0 });
  userExpenses.forEach(e => { byCategory[e.category].total += e.amount; byCategory[e.category].count++; });
  thisMonth.forEach(e => byCategory[e.category].thisMonth += e.amount);
  const user = users.find(u => u.id === req.user.id);
  const budgetStatus = {};
  categories.forEach(c => { const spent = byCategory[c].thisMonth; const budget = user.monthlyBudget[c] || 0; budgetStatus[c] = { spent, budget, remaining: budget - spent, overBudget: spent > budget }; });
  res.json({ totalAllTime: userExpenses.reduce((s, e) => s + e.amount, 0), totalThisMonth: thisMonth.reduce((s, e) => s + e.amount, 0), count: userExpenses.length, byCategory, budget: budgetStatus });
});

app.patch('/expenses/:id', auth, (req, res) => {
  const exp = expenses.find(e => e.id === parseInt(req.params.id) && e.userId === req.user.id);
  if (!exp) return res.status(404).json({ error: 'Not found' });
  if (req.body.amount) exp.amount = req.body.amount;
  if (req.body.category && categories.includes(req.body.category)) exp.category = req.body.category;
  if (req.body.description !== undefined) exp.description = req.body.description;
  res.json(exp);
});

app.delete('/expenses/:id', auth, (req, res) => {
  const idx = expenses.findIndex(e => e.id === parseInt(req.params.id) && e.userId === req.user.id);
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  expenses.splice(idx, 1);
  res.status(204).send();
});

app.listen(3000, () => console.log('Expense Tracker :3000'));
module.exports = app;
