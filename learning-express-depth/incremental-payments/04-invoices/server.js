// 04-invoices: Generate invoices. Line items, subtotal, tax, total. PDF-ready.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE invoices (id TEXT PRIMARY KEY, customer_id TEXT, number TEXT UNIQUE, status TEXT DEFAULT 'draft', subtotal_cents INTEGER, tax_cents INTEGER, total_cents INTEGER, due_at TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE invoice_items (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id TEXT, description TEXT, quantity INTEGER, unit_price_cents INTEGER, total_cents INTEGER)`);

const TAX_RATE = 0.08;

let invoiceCounter = 1000;
function nextInvoiceNumber() {
  return `INV-${++invoiceCounter}`;
}

app.post('/invoices', (req, res) => {
  const { customer_id, items, due_days } = req.body;
  if (!customer_id || !Array.isArray(items) || !items.length) return res.status(422).json({ error: 'customer_id and items required' });

  // Calculate totals
  let subtotal = 0;
  for (const item of items) {
    if (!item.description || item.quantity <= 0 || item.unit_price_cents < 0) {
      return res.status(422).json({ error: 'invalid item' });
    }
    subtotal += item.quantity * item.unit_price_cents;
  }
  const tax = Math.round(subtotal * TAX_RATE);
  const total = subtotal + tax;
  const id = 'inv_' + crypto.randomBytes(4).toString('hex');
  const number = nextInvoiceNumber();
  const due = due_days ? new Date(Date.now() + due_days * 86400000).toISOString() : null;

  db.prepare("INSERT INTO invoices VALUES (?, ?, ?, 'draft', ?, ?, ?, ?, ?)").run(id, customer_id, number, subtotal, tax, total, due, new Date().toISOString());
  for (const item of items) {
    db.prepare('INSERT INTO invoice_items (invoice_id, description, quantity, unit_price_cents, total_cents) VALUES (?, ?, ?, ?, ?)').run(id, item.description, item.quantity, item.unit_price_cents, item.quantity * item.unit_price_cents);
  }
  res.status(201).json({ id, number, status: 'draft', subtotal_cents: subtotal, tax_cents: tax, total_cents: total });
});

app.get('/invoices/:id', (req, res) => {
  const inv = db.prepare('SELECT * FROM invoices WHERE id = ?').get(req.params.id);
  if (!inv) return res.status(404).json({ error: 'not found' });
  inv.items = db.prepare('SELECT * FROM invoice_items WHERE invoice_id = ?').all(req.params.id);
  res.json(inv);
});

// Mark as paid
app.post('/invoices/:id/pay', (req, res) => {
  const r = db.prepare("UPDATE invoices SET status = 'paid' WHERE id = ?").run(req.params.id);
  r.changes ? res.json({ paid: true }) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('04-invoices on :3000 (8% tax)'));
