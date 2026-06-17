// Subscription Billing — Plans, subscriptions, invoices, usage, upgrade/downgrade.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const plans = []; const subscriptions = []; const invoices = []; let pId = 1, subId = 1, invId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }
function generateInvoice(sub, amount, description) {
  const inv = { id: invId++, subscriptionId: sub.id, userId: sub.userId, amount, currency: 'usd', description, status: 'pending', dueDate: new Date(Date.now() + 7 * 86400000).toISOString(), createdAt: new Date().toISOString() };
  invoices.push(inv);
  return inv;
}

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), currentPlan: 'free' });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Plans
app.post('/plans', auth, (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
  const { name, price, interval, features, limits } = req.body;
  if (!name || price === undefined) return res.status(400).json({ error: 'name and price required' });
  const p = { id: pId++, name, price: parseFloat(price), interval: interval || 'month', features: features || [], limits: limits || {}, subscribers: 0 };
  plans.push(p);
  res.status(201).json(p);
});

app.get('/plans', (req, res) => res.json(plans));

// Subscribe
app.post('/subscribe', auth, (req, res) => {
  const { planId } = req.body;
  const plan = plans.find(p => p.id === parseInt(planId));
  if (!plan) return res.status(404).json({ error: 'Plan not found' });
  if (subscriptions.find(s => s.userId === req.user.id && s.status === 'active')) return res.status(409).json({ error: 'Already have active subscription' });
  const sub = { id: subId++, userId: req.user.id, planId: plan.id, status: 'active', startDate: new Date().toISOString(), nextBillingDate: new Date(Date.now() + 30 * 86400000).toISOString(), createdAt: new Date().toISOString() };
  subscriptions.push(sub);
  plan.subscribers++;
  users.find(u => u.id === req.user.id).currentPlan = plan.name;
  // Generate first invoice
  generateInvoice(sub, plan.price, `Initial subscription to ${plan.name}`);
  res.status(201).json(sub);
});

app.get('/my-subscription', auth, (req, res) => {
  const sub = subscriptions.find(s => s.userId === req.user.id && s.status === 'active');
  if (!sub) return res.status(404).json({ error: 'No active subscription' });
  res.json({ ...sub, plan: plans.find(p => p.id === sub.planId), invoices: invoices.filter(i => i.subscriptionId === sub.id) });
});

// Cancel
app.post('/my-subscription/cancel', auth, (req, res) => {
  const sub = subscriptions.find(s => s.userId === req.user.id && s.status === 'active');
  if (!sub) return res.status(404).json({ error: 'No active subscription' });
  sub.status = 'cancelled';
  sub.cancelledAt = new Date().toISOString();
  users.find(u => u.id === req.user.id).currentPlan = 'free';
  res.json(sub);
});

// Upgrade/downgrade
app.post('/my-subscription/change-plan', auth, (req, res) => {
  const sub = subscriptions.find(s => s.userId === req.user.id && s.status === 'active');
  if (!sub) return res.status(404).json({ error: 'No active subscription' });
  const newPlan = plans.find(p => p.id === parseInt(req.body.planId));
  if (!newPlan) return res.status(404).json({ error: 'Plan not found' });
  const oldPlan = plans.find(p => p.id === sub.planId);
  sub.planId = newPlan.id;
  sub.upgradedAt = new Date().toISOString();
  const isUpgrade = newPlan.price > oldPlan.price;
  generateInvoice(sub, isUpgrade ? newPlan.price - oldPlan.price : oldPlan.price - newPlan.price, isUpgrade ? `Upgrade proration` : `Downgrade credit`);
  res.json(sub);
});

// Invoices
app.get('/my-invoices', auth, (req, res) => res.json(invoices.filter(i => i.userId === req.user.id)));
app.post('/invoices/:id/pay', auth, (req, res) => {
  const inv = invoices.find(i => i.id === parseInt(req.params.id) && i.userId === req.user.id);
  if (!inv) return res.status(404).json({ error: 'Not found' });
  if (inv.status === 'paid') return res.status(409).json({ error: 'Already paid' });
  inv.status = 'paid'; inv.paidAt = new Date().toISOString();
  res.json(inv);
});

app.listen(3000, () => console.log('Subscription Billing :3000'));
module.exports = app;
