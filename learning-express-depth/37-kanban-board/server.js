// 37 — Kanban Board
// Cards have a column (todo / in_progress / done). Move them between columns.
const express = require('express');
const app = express();
app.use(express.json());

const cards = [];

app.get('/cards', (req, res) => {
  // Group by column
  const board = { todo: [], in_progress: [], done: [] };
  for (const c of cards) board[c.column].push(c);
  res.json(board);
});

app.post('/cards', (req, res) => {
  const { title, description } = req.body;
  const card = { id: cards.length + 1, title, description: description || '', column: 'todo' };
  cards.push(card);
  res.status(201).json(card);
});

// Move a card to a different column
app.patch('/cards/:id/move', (req, res) => {
  const card = cards.find(c => c.id === parseInt(req.params.id));
  if (!card) return res.status(404).json({ error: 'Card not found' });
  const { column } = req.body;
  if (!['todo', 'in_progress', 'done'].includes(column)) {
    return res.status(422).json({ error: 'column must be todo, in_progress, or done' });
  }
  card.column = column;
  res.json(card);
});

app.listen(3000, () => console.log('Kanban on http://localhost:3000'));
