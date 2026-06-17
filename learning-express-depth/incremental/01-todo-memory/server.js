// 01-todo-memory: The starting point. In-memory CRUD. No database, no auth.
// This is the simplest possible todo API. Every later stage adds one thing on top of this.
const express = require('express');
const app = express();
app.use(express.json());

let todos = [];
let nextId = 1;

app.get('/todos', (req, res) => {
  res.json({ count: todos.length, todos });
});

app.post('/todos', (req, res) => {
  const { title } = req.body;
  if (!title) return res.status(422).json({ error: 'title is required' });
  const todo = { id: nextId++, title, done: false, createdAt: new Date().toISOString() };
  todos.push(todo);
  res.status(201).json(todo);
});

app.patch('/todos/:id', (req, res) => {
  const todo = todos.find(t => t.id === parseInt(req.params.id));
  if (!todo) return res.status(404).json({ error: 'Not found' });
  if (req.body.title !== undefined) todo.title = req.body.title;
  if (req.body.done !== undefined) todo.done = req.body.done;
  res.json(todo);
});

app.delete('/todos/:id', (req, res) => {
  const index = todos.findIndex(t => t.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Not found' });
  todos.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('01-todo-memory on :3000'));
