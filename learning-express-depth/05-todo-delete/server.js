// 05 — Todo Delete
// Goal: let the client remove a todo by its id.
// Client sends DELETE /todos/1 and we remove the one with id 1.
const express = require('express');
const app = express();
app.use(express.json());

const todos = [
  { id: 1, title: 'Buy milk', done: false },
  { id: 2, title: 'Walk dog', done: false },
];

// GET /todos — return the list
app.get('/todos', (req, res) => {
  res.json({ count: todos.length, todos });
});

// POST /todos — add a new todo
app.post('/todos', (req, res) => {
  const { title } = req.body;
  const todo = { id: todos.length + 1, title, done: false };
  todos.push(todo);
  res.status(201).json(todo);
});

// DELETE /todos/:id — remove a todo by id
// The :id part is a "URL parameter" — it captures whatever the client puts there.
app.delete('/todos/:id', (req, res) => {
  // req.params.id is the string from the URL
  const id = parseInt(req.params.id);

  // Find the index of the todo with that id
  const index = todos.findIndex(t => t.id === id);

  // If not found, return 404
  if (index === -1) {
    return res.status(404).json({ error: 'Todo not found' });
  }

  // Remove from the array
  todos.splice(index, 1);

  // 204 means "success, no body to return"
  res.status(204).end();
});

app.listen(3000, () => console.log('Server on http://localhost:3000'));
