// 06 — Notes App
// Goal: same structure as the todo app, but for notes.
// A note has: id, title, body, createdAt
// Endpoints: GET /notes, POST /notes, DELETE /notes/:id
const express = require('express');
const app = express();
app.use(express.json());

const notes = []; // Our notes in memory. Resets on restart.

app.get('/notes', (req, res) => {
  res.json({ count: notes.length, notes });
});

app.post('/notes', (req, res) => {
  const { title, body } = req.body;
  const note = {
    id: notes.length + 1,
    title,
    body: body || '', // body is optional
    createdAt: new Date().toISOString(),
  };
  notes.push(note);
  res.status(201).json(note);
});

app.get('/notes/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const note = notes.find(n => n.id === id);
  if (!note) return res.status(404).json({ error: 'Note not found' });
  res.json(note);
});

app.delete('/notes/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const index = notes.findIndex(n => n.id === id);
  if (index === -1) return res.status(404).json({ error: 'Note not found' });
  notes.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Notes server on http://localhost:3000'));
