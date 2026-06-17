// 36 — Flashcards
// Each card: question, answer, status (new/known/review).
const express = require('express');
const app = express();
app.use(express.json());

const cards = [];

app.get('/cards', (req, res) => {
  const { status } = req.query;
  let result = cards;
  if (status) result = result.filter(c => c.status === status);
  res.json({ count: result.length, cards: result });
});

app.post('/cards', (req, res) => {
  const { question, answer } = req.body;
  const card = { id: cards.length + 1, question, answer, status: 'new' };
  cards.push(card);
  res.status(201).json(card);
});

app.patch('/cards/:id', (req, res) => {
  const card = cards.find(c => c.id === parseInt(req.params.id));
  if (!card) return res.status(404).json({ error: 'Card not found' });
  if (req.body.status) card.status = req.body.status;
  res.json(card);
});

app.listen(3000, () => console.log('Flashcards on http://localhost:3000'));
