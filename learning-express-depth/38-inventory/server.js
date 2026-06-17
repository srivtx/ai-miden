// 38 — Inventory Tracker
// Items have a quantity. Add or remove stock.
const express = require('express');
const app = express();
app.use(express.json());

const items = [];

app.get('/items', (req, res) => {
  res.json({ count: items.length, items });
});

app.post('/items', (req, res) => {
  const { name, sku, quantity } = req.body;
  if (items.some(i => i.sku === sku)) return res.status(409).json({ error: 'SKU already exists' });
  const item = { id: items.length + 1, name, sku, quantity: quantity || 0 };
  items.push(item);
  res.status(201).json(item);
});

// Add stock: positive number
// Remove stock: negative number
app.patch('/items/:id/adjust', (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id));
  if (!item) return res.status(404).json({ error: 'Item not found' });
  const delta = req.body.delta;
  if (typeof delta !== 'number') return res.status(422).json({ error: 'delta must be a number' });
  item.quantity += delta;
  if (item.quantity < 0) item.quantity = 0; // Never negative
  res.json(item);
});

// Low stock alert
app.get('/low-stock', (req, res) => {
  const threshold = parseInt(req.query.threshold) || 10;
  const low = items.filter(i => i.quantity < threshold);
  res.json({ threshold, count: low.length, items: low });
});

app.listen(3000, () => console.log('Inventory on http://localhost:3000'));
