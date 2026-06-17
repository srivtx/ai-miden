// 01-charges: Charge a customer. Card, amount, currency. Status tracking.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE charges (id TEXT PRIMARY KEY, customer_id TEXT, amount_cents INTEGER, currency TEXT DEFAULT 'usd', status TEXT DEFAULT 'pending', card_last4 TEXT, failure_reason TEXT, created_at TEXT DEFAULT (datetime('now')), captured_at TEXT)`);

// Simulated card processing
async function processCardPayment(amount, cardNumber) {
  await new Promise(r => setTimeout(r, 50));
  // Test cards: 4242 succeeds, 0002 declines, 9995 insufficient funds
  const last4 = cardNumber.slice(-4);
  if (cardNumber === '4000000000000002') return { success: false, decline_code: 'card_declined' };
  if (cardNumber === '4000000000009995') return { success: false, decline_code: 'insufficient_funds' };
  if (!/^\d{16}$/.test(cardNumber.replace(/\s/g, ''))) return { success: false, decline_code: 'invalid_card' };
  return { success: true, transactionId: 'ch_' + crypto.randomBytes(8).toString('hex') };
}

// Create a charge
app.post('/charges', async (req, res) => {
  const { customer_id, amount_cents, currency, card_number } = req.body;
  if (!customer_id || !amount_cents || !card_number) return res.status(422).json({ error: 'customer_id, amount_cents, card_number required' });
  if (amount_cents < 50) return res.status(422).json({ error: 'amount_too_small', min: 50 });

  const id = 'ch_' + crypto.randomBytes(8).toString('hex');
  const result = await processCardPayment(amount_cents, card_number);

  if (!result.success) {
    db.prepare("INSERT INTO charges (id, customer_id, amount_cents, currency, status, card_last4, failure_reason) VALUES (?, ?, ?, ?, ?, ?, ?)").run(id, customer_id, amount_cents, currency || 'usd', 'failed', card_number.slice(-4), result.decline_code);
    return res.status(402).json({ error: result.decline_code, charge_id: id });
  }

  db.prepare("INSERT INTO charges (id, customer_id, amount_cents, currency, status, card_last4, captured_at) VALUES (?, ?, ?, ?, 'succeeded', ?, datetime('now'))").run(id, customer_id, amount_cents, currency || 'usd', card_number.slice(-4));
  res.status(201).json({ id, status: 'succeeded', amount_cents, currency: currency || 'usd' });
});

app.get('/charges/:id', (req, res) => {
  const c = db.prepare('SELECT * FROM charges WHERE id = ?').get(req.params.id);
  c ? res.json(c) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('01-charges on :3000 (test card: 4242424242424242)'));
