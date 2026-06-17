// 10 — Bookmarks App
// Same CRUD. Bookmarks have url, title, description.
// NEW: we reject duplicate URLs.
const express = require('express');
const app = express();
app.use(express.json());

const bookmarks = [];

app.get('/bookmarks', (req, res) => {
  res.json({ count: bookmarks.length, bookmarks });
});

app.post('/bookmarks', (req, res) => {
  const { url, title, description } = req.body;
  // Reject duplicate URLs
  if (bookmarks.some(b => b.url === url)) {
    return res.status(409).json({ error: 'Bookmark with this URL already exists' });
  }
  const bookmark = { id: bookmarks.length + 1, url, title, description: description || '', createdAt: new Date().toISOString() };
  bookmarks.push(bookmark);
  res.status(201).json(bookmark);
});

app.get('/bookmarks/:id', (req, res) => {
  const bookmark = bookmarks.find(b => b.id === parseInt(req.params.id));
  if (!bookmark) return res.status(404).json({ error: 'Bookmark not found' });
  res.json(bookmark);
});

app.delete('/bookmarks/:id', (req, res) => {
  const index = bookmarks.findIndex(b => b.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Bookmark not found' });
  bookmarks.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Bookmarks server on http://localhost:3000'));
