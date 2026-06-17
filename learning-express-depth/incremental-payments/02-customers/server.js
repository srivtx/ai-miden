// 02-customers: Customer records. Save cards for future use.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE customers (id TEXT PRIMARY KEY, email TEXT UNIQUE, name TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE payment_methods (id TEXT PRIMARY KEY, customer_id TEXT, card_last4 TEXT, card_brand TEXT, exp_month INTEGER, exp_year INTEGER, is_default INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);

function detectBrand(cardNumber) {
  if (cardNumber.startsWith('4')) return 'visa';
  if (/^5[1-5]/.test(cardNumber)) return 'mastercard';
  if (/^3[47]/.test(cardNumber)) return 'amex';
  if (/^6/.test(cardNumber)) return 'discover';
  return 'unknown';
}

// Create a customer
app.post('/customers', (req, res) => {
  const { email, name } = req.body;
  if (!email) return res.status(422).json({ error: 'email required' });
  const id = 'cus_' + crypto.randomBytes(4).toString('hex');
  try {
    db.prepare('INSERT INTO customers VALUES (?, ?, ?, ?)').run(id, email, name || null, new Date().toISOString());
    res.status(201).json({ id, email, name });
  } catch { res.status(409).json({ error: 'email exists' }); }
});

app.get('/customers/:id', (req, res) => {
  const c = db.prepare('SELECT * FROM customers WHERE id = ?').get(req.params.id);
  c ? res.json(c) : res.status(404).json({ error: 'not found' });
});

// Add a payment method
app.post('/customers/:id/payment-methods', (req, res) => {
  const customer = db.prepare('SELECT * FROM customers WHERE id = ?').get(req.params.id);
  if (!customer) return res.status(404).json({ error: 'not found' });
  const { card_number, exp_month, exp_year } = req.body;
  if (!card_number || !exp_month || !exp_year) return res.status(422).json({ error: 'card_number, exp_month, exp_year required' });
  const id = 'pm_' + crypto.randomBytes(4).toString('hex');
  const brand = detectBrand(card_number);
  // If first payment method, make it default
  const existing = db.prepare('SELECT COUNT(*) as c FROM payment_methods WHERE customer_id = ?').get(req.params.id).c;
  const isDefault = existing === 0 ? 1 : 0;
  db.prepare('INSERT INTO payment_methods VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(id, req.params.id, card_number.slice(-4), brand, exp_month, exp_year, isDefault, new Date().toISOString());
  res.status(201).json({ id, brand, last4: card_number.slice(-4), exp_month, exp_year, is_default: !!isDefault });
});

app.get('/customers/:id/payment-methods', (req, res) => {
  const methods = db.prepare('SELECT * FROM payment_methods WHERE customer_id = ?').all(req.params.id);
  res.json({ customer_id: req.params.id, methods });
});

app.listen(3000, () => console.log('02-customers on :3000'));
