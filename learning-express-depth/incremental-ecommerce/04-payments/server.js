// 04-payments: Simulated payment gateway. Charge, refund, status.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE orders (id TEXT PRIMARY KEY, user_id TEXT, total_cents INTEGER, status TEXT DEFAULT 'pending');
  CREATE TABLE payments (id TEXT PRIMARY KEY, order_id TEXT, amount_cents INTEGER, status TEXT, method TEXT, created_at TEXT DEFAULT (datetime('now')));
`);

// Seed an order
db.prepare('INSERT INTO orders (id, user_id, total_cents) VALUES (?, ?, ?)').run('ord_001', 'alice', 107800);
db.prepare('INSERT INTO orders (id, user_id, total_cents) VALUES (?, ?, ?)').run('ord_002', 'bob', 59900);

// Simulated payment processor
async function processPayment({ amount, method, cardNumber }) {
  // In real life: call Stripe/PayPal/etc.
  await new Promise(r => setTimeout(r, 100));
  // Simulate failure for cards ending in "0000"
  if (cardNumber && cardNumber.endsWith('0000')) {
    return { success: false, error: 'card_declined' };
  }
  return { success: true, transactionId: 'txn_' + crypto.randomBytes(6).toString('hex') };
}

// Charge an order
app.post('/orders/:id/pay', async (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'order not found' });
  if (order.status === 'paid') return res.status(409).json({ error: 'already paid' });
  if (order.status === 'cancelled') return res.status(409).json({ error: 'order cancelled' });

  const { method = 'card', card_number } = req.body;
  if (!card_number) return res.status(422).json({ error: 'card_number required' });

  const paymentId = 'pay_' + crypto.randomBytes(6).toString('hex');
  const result = await processPayment({ amount: order.total_cents, method, cardNumber: card_number });

  if (!result.success) {
    db.prepare('INSERT INTO payments (id, order_id, amount_cents, status, method) VALUES (?, ?, ?, ?, ?)').run(paymentId, order.id, order.total_cents, 'failed', method);
    return res.status(402).json({ error: result.error, payment_id: paymentId });
  }

  // Update order and payment
  db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('paid', order.id);
  db.prepare('INSERT INTO payments (id, order_id, amount_cents, status, method) VALUES (?, ?, ?, ?, ?)').run(paymentId, order.id, order.total_cents, 'succeeded', method);

  res.json({ order_id: order.id, status: 'paid', payment_id: paymentId, transaction_id: result.transactionId });
});

// Refund a payment
app.post('/payments/:id/refund', (req, res) => {
  const payment = db.prepare('SELECT * FROM payments WHERE id = ?').get(req.params.id);
  if (!payment) return res.status(404).json({ error: 'payment not found' });
  if (payment.status !== 'succeeded') return res.status(409).json({ error: 'cannot refund' });

  db.prepare('UPDATE payments SET status = ? WHERE id = ?').run('refunded', payment.id);
  db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('refunded', payment.order_id);
  res.json({ payment_id: payment.id, status: 'refunded' });
});

// Payment history for an order
app.get('/orders/:id/payments', (req, res) => {
  const payments = db.prepare('SELECT * FROM payments WHERE order_id = ? ORDER BY created_at DESC').all(req.params.id);
  res.json({ count: payments.length, payments });
});

app.listen(3000, () => console.log('04-payments on :3000'));
