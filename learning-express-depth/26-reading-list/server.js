// 26 — Reading List
// Each book: title, author, status (to_read/reading/done), rating.
const express = require('express');
const app = express();
app.use(express.json());

const books = [];

app.get('/books', (req, res) => {
  const { status } = req.query;
  let result = books;
  if (status) result = result.filter(b => b.status === status);
  res.json({ count: result.length, books: result });
});

app.post('/books', (req, res) => {
  const { title, author } = req.body;
  const book = { id: books.length + 1, title, author, status: 'to_read', rating: 0, addedAt: new Date().toISOString() };
  books.push(book);
  res.status(201).json(book);
});

// Update status and/or rating
app.patch('/books/:id', (req, res) => {
  const book = books.find(b => b.id === parseInt(req.params.id));
  if (!book) return res.status(404).json({ error: 'Book not found' });
  if (req.body.status) book.status = req.body.status;
  if (req.body.rating) book.rating = req.body.rating;
  res.json(book);
});

app.listen(3000, () => console.log('Reading list on http://localhost:3000'));
