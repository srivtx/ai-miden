// 08-payouts: Get your money. Stripe-style: balance → payout → bank.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE balance (id INTEGER PRIMARY KEY, available_cents INTEGER, pending_cents INTEGER)`);
db.exec(`CREATE TABLE payouts (id TEXT PRIMARY KEY, amount_cents INTEGER, status TEXT DEFAULT 'pending', bank_account TEXT, arrival_date TEXT, created_at TEXT DEFAULT (datetime('now')))`);

// Seed
db.prepare('INSERT INTO balance VALUES (1, 100000, 25000)');

// Get balance
app.get('/balance', (req, res) => {
  const b = db.prepare('SELECT * FROM balance WHERE id = 1').get();
  res.json({ available_cents: b.available_cents, pending_cents: b.pending_cents, total_cents: b.available_cents + b.pending_cents });
});

// Create a payout
app.post('/payouts', (req, res) => {
  const { amount_cents, bank_account } = req.body;
  if (!amount_cents || !bank_account) return res.status(422).json({ error: 'amount_cents and bank_account required' });
  if (amount_cents < 100) return res.status(422).json({ error: 'minimum payout is $1' });

  const balance = db.prepare('SELECT * FROM balance WHERE id = 1').get();
  if (amount_cents > balance.available_cents) return res.status(422).json({ error: 'insufficient balance', available: balance.available_cents };

  // Deduct from balance
  db.prepare('UPDATE balance SET available_cents = available_cents - ? WHERE id = 1').run(amount_cents);

  const id = 'po_' + crypto.randomBytes(4).toString('hex');
  const arrival = new Date(Date.now() + 2 * 86400000).toISOString();  // 2 business days
  db.prepare("INSERT INTO payouts VALUES (?, ?, 'in_transit', ?, ?, ?)").run(id, amount_cents, bank_account, arrival, new Date().toISOString());
  res.status(201).json({ id, amount_cents, status: 'in_transit', arrival_date: arrival });
});

// Mark as paid (when bank confirms)
app.post('/payouts/:id/paid', (req, res) => {
  const r = db.prepare("UPDATE payouts SET status = 'paid' WHERE id = ?").run(req.params.id);
  r.changes ? res.json({ paid: true }) : res.status(404).json({ error: 'not found' });
});

app.get('/payouts', (req, res) => {
  res.json({ payouts: db.prepare('SELECT * FROM payouts ORDER BY created_at DESC').all() });
});

app.listen(3000, () => console.log('08-payouts on :3000 (2 day arrival)'));
