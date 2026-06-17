// 07 — Blog App
// A blog post is like a note, but with an author.
// Same CRUD pattern. New field: author.
const express = require('express');
const app = express();
app.use(express.json());

const posts = [];

app.get('/posts', (req, res) => {
  res.json({ count: posts.length, posts });
});

app.post('/posts', (req, res) => {
  const { title, body, author } = req.body;
  const post = {
    id: posts.length + 1,
    title,
    body: body || '',
    author: author || 'Anonymous',
    createdAt: new Date().toISOString(),
  };
  posts.push(post);
  res.status(201).json(post);
});

app.get('/posts/:id', (req, res) => {
  const post = posts.find(p => p.id === parseInt(req.params.id));
  if (!post) return res.status(404).json({ error: 'Post not found' });
  res.json(post);
});

app.delete('/posts/:id', (req, res) => {
  const index = posts.findIndex(p => p.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Post not found' });
  posts.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Blog server on http://localhost:3000'));
