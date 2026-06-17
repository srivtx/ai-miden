// 09-tax: Tax calculation per region. Sales tax, VAT, GST.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE tax_rates (country TEXT, region TEXT, rate REAL, type TEXT, PRIMARY KEY (country, region))`);

// Seed: US states, EU countries, etc.
const rates = [
  ['US', 'CA', 0.0725, 'sales_tax'], ['US', 'NY', 0.04, 'sales_tax'], ['US', 'TX', 0.0625, 'sales_tax'],
  ['US', 'DE', 0, 'sales_tax'], ['GB', '', 0.20, 'vat'], ['DE', '', 0.19, 'vat'],
  ['FR', '', 0.20, 'vat'], ['JP', '', 0.10, 'consumption'], ['AU', '', 0.10, 'gst'],
  ['IN', '', 0.18, 'gst'], ['CA', 'ON', 0.13, 'hst'],
];
for (const r of rates) db.prepare('INSERT INTO tax_rates VALUES (?, ?, ?, ?)').run(...r);

// Calculate tax
app.post('/tax/calculate', (req, res) => {
  const { country, region, amount_cents } = req.body;
  if (!country || !amount_cents) return res.status(422).json({ error: 'country and amount_cents required' });
  const rate = db.prepare('SELECT * FROM tax_rates WHERE country = ? AND (region = ? OR region = "")').get(country, region || '');
  if (!rate) return res.json({ country, region, rate: 0, tax_cents: 0, total_cents: amount_cents, note: 'no tax rate for region' });
  const tax_cents = Math.round(amount_cents * rate.rate);
  res.json({
    country,
    region: rate.region || '(country)',
    type: rate.type,
    rate: rate.rate,
    tax_cents,
    total_cents: amount_cents + tax_cents,
  });
});

app.get('/tax/rates', (req, res) => {
  res.json({ rates: db.prepare('SELECT * FROM tax_rates ORDER BY country, region').all() });
});

app.listen(3000, () => console.log('09-tax on :3000'));
