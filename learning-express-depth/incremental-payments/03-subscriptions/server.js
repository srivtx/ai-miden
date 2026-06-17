// 03-subscriptions: Recurring charges. Monthly/yearly. Auto-bill.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE subscriptions (id TEXT PRIMARY KEY, customer_id TEXT, plan TEXT, amount_cents INTEGER, interval TEXT, status TEXT DEFAULT 'active', current_period_start TEXT, current_period_end TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE invoices (id TEXT PRIMARY KEY, subscription_id TEXT, amount_cents INTEGER, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT (datetime('now')))`);

const INTERVAL_DAYS = { monthly: 30, yearly: 365 };

// Create a subscription
app.post('/subscriptions', (req, res) => {
  const { customer_id, plan, amount_cents, interval } = req.body;
  if (!customer_id || !plan || !amount_cents || !interval) return res.status(422).json({ error: 'missing fields' });
  if (!INTERVAL_DAYS[interval]) return res.status(422).json({ error: 'invalid interval', allowed: Object.keys(INTERVAL_DAYS) });
  const id = 'sub_' + crypto.randomBytes(4).toString('hex');
  const start = new Date();
  const end = new Date(start.getTime() + INTERVAL_DAYS[interval] * 86400000);
  db.prepare('INSERT INTO subscriptions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)').run(id, customer_id, plan, amount_cents, interval, 'active', start.toISOString(), end.toISOString(), start.toISOString());
  res.status(201).json({ id, customer_id, plan, amount_cents, interval, current_period_end: end.toISOString() });
});

// Cancel
app.delete('/subscriptions/:id', (req, res) => {
  const r = db.prepare("UPDATE subscriptions SET status = 'cancelled' WHERE id = ?").run(req.params.id);
  r.changes ? res.json({ cancelled: true }) : res.status(404).json({ error: 'not found' });
});

// Renew: creates a new invoice and extends the period
app.post('/subscriptions/:id/renew', (req, res) => {
  const sub = db.prepare('SELECT * FROM subscriptions WHERE id = ?').get(req.params.id);
  if (!sub) return res.status(404).json({ error: 'not found' });
  if (sub.status !== 'active') return res.status(409).json({ error: 'subscription not active' });
  // Charge (simulated)
  const invoiceId = 'inv_' + crypto.randomBytes(4).toString('hex');
  db.prepare("INSERT INTO invoices (id, subscription_id, amount_cents, status) VALUES (?, ?, ?, 'paid')").run(invoiceId, sub.id, sub.amount_cents);
  // Extend period
  const newEnd = new Date(new Date(sub.current_period_end).getTime() + INTERVAL_DAYS[sub.interval] * 86400000);
  db.prepare("UPDATE subscriptions SET current_period_start = ?, current_period_end = ? WHERE id = ?").run(sub.current_period_end, newEnd.toISOString(), sub.id);
  res.json({ renewed: true, invoice_id: invoiceId, new_period_end: newEnd.toISOString() });
});

app.get('/subscriptions/:id', (req, res) => {
  const sub = db.prepare('SELECT * FROM subscriptions WHERE id = ?').get(req.params.id);
  if (!sub) return res.status(404).json({ error: 'not found' });
  sub.invoices = db.prepare('SELECT * FROM invoices WHERE subscription_id = ?').all(sub.id);
  res.json(sub);
});

app.listen(3000, () => console.log('03-subscriptions on :3000 (monthly/yearly)'));
