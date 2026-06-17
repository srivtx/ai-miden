// 01_hello_express.js — First server. GET/POST/PUT/DELETE. Params, query, JSON, 404.

const express = require('express');
const app = express();
app.use(express.json());

let items = [{ id: 1, text: 'hello' }];

app.get('/items', (req, res) => res.json(items));

app.get('/items/:id', (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id));
  item ? res.json(item) : res.status(404).json({ error: 'Not found' });
});

app.post('/items', (req, res) => {
  const item = { id: items.length + 1, text: req.body.text, created: new Date() };
  items.push(item);
  res.status(201).json(item);
});

app.put('/items/:id', (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id));
  if (!item) return res.status(404).json({ error: 'Not found' });
  item.text = req.body.text ?? item.text;
  res.json(item);
});

app.delete('/items/:id', (req, res) => {
  const idx = items.findIndex(i => i.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  items.splice(idx, 1);
  res.status(204).send();
});

app.listen(3000, () => console.log('http://localhost:3000'));
