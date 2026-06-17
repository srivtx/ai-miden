// 15 — Expense Tracker
// Same CRUD. Each expense has an amount (number) and a category.
// NEW: a /summary endpoint that adds up the totals.
const express = require('express');
const app = express();
app.use(express.json());

const expenses = [];

app.get('/expenses', (req, res) => {
  res.json({ count: expenses.length, expenses });
});

app.post('/expenses', (req, res) => {
  const { amount, category, description } = req.body;
  const expense = { id: expenses.length + 1, amount, category, description: description || '', date: new Date().toISOString() };
  expenses.push(expense);
  res.status(201).json(expense);
});

app.delete('/expenses/:id', (req, res) => {
  const index = expenses.findIndex(e => e.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Expense not found' });
  expenses.splice(index, 1);
  res.status(204).end();
});

// NEW: summary endpoint. Adds up the totals.
app.get('/summary', (req, res) => {
  const total = expenses.reduce((sum, e) => sum + e.amount, 0);
  const byCategory = {};
  for (const e of expenses) {
    byCategory[e.category] = (byCategory[e.category] || 0) + e.amount;
  }
  res.json({ total, count: expenses.length, byCategory });
});

app.listen(3000, () => console.log('Expense server on http://localhost:3000'));
