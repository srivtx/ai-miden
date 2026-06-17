// 05-refunds: Refund a charge. Full or partial. Track the reason.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE charges (id TEXT PRIMARY KEY, amount_cents INTEGER, refunded_cents INTEGER DEFAULT 0, status TEXT DEFAULT 'succeeded')`);
db.exec(`CREATE TABLE refunds (id TEXT PRIMARY KEY, charge_id TEXT, amount_cents INTEGER, reason TEXT, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT (datetime('now')))`);

// Seed
db.prepare("INSERT INTO charges VALUES ('ch_seed', 10000, 0, 'succeeded')");

// Refund a charge (full or partial)
app.post('/refunds', (req, res) => {
  const { charge_id, amount_cents, reason } = req.body;
  if (!charge_id) return res.status(422).json({ error: 'charge_id required' });
  const charge = db.prepare('SELECT * FROM charges WHERE id = ?').get(charge_id);
  if (!charge) return res.status(404).json({ error: 'charge not found' });
  if (charge.status !== 'succeeded') return res.status(409).json({ error: 'charge not refundable' });

  const remaining = charge.amount_cents - charge.refunded_cents;
  const refundAmount = amount_cents || remaining;  // default: full refund
  if (refundAmount > remaining) return res.status(422).json({ error: 'refund exceeds remaining', remaining });
  if (refundAmount <= 0) return res.status(422).json({ error: 'refund must be positive' });

  const id = 're_' + crypto.randomBytes(4).toString('hex');
  db.prepare("INSERT INTO refunds (id, charge_id, amount_cents, reason, status) VALUES (?, ?, ?, ?, 'succeeded')").run(id, charge_id, refundAmount, reason || 'requested_by_customer');
  // Update charge
  const newRefunded = charge.refunded_cents + refundAmount;
  const newStatus = newRefunded >= charge.amount_cents ? 'refunded' : 'partially_refunded';
  db.prepare('UPDATE charges SET refunded_cents = ?, status = ? WHERE id = ?').run(newRefunded, newStatus, charge_id);
  res.status(201).json({ id, charge_id, amount_cents: refundAmount, status: 'succeeded', new_charge_status: newStatus });
});

app.get('/charges/:id', (req, res) => {
  const charge = db.prepare('SELECT * FROM charges WHERE id = ?').get(req.params.id);
  if (!charge) return res.status(404).json({ error: 'not found' });
  charge.refunds = db.prepare('SELECT * FROM refunds WHERE charge_id = ?').all(charge.id);
  res.json(charge);
});

app.listen(3000, () => console.log('05-refunds on :3000'));
