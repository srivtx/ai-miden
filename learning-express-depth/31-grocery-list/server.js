// 31 — Grocery List
// Items with a "purchased" flag. Check them off as you shop.
const express = require('express');
const app = express();
app.use(express.json());

const items = [];

app.get('/items', (req, res) => {
  res.json({ count: items.length, items });
});

app.post('/items', (req, res) => {
  const { name, quantity } = req.body;
  const item = { id: items.length + 1, name, quantity: quantity || 1, purchased: false };
  items.push(item);
  res.status(201).json(item);
});

// Check off an item
app.patch('/items/:id', (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id));
  if (!item) return res.status(404).json({ error: 'Item not found' });
  if (req.body.purchased !== undefined) item.purchased = req.body.purchased;
  if (req.body.quantity !== undefined) item.quantity = req.body.quantity;
  res.json(item);
});

app.delete('/items/:id', (req, res) => {
  const index = items.findIndex(i => i.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Item not found' });
  items.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Grocery list on http://localhost:3000'));
