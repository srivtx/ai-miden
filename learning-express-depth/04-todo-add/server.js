// 04 — Todo Add
// Goal: let the client add new todos by sending POST /todos
// The request body has { "title": "Buy milk" } and we add it to the list.
const express = require('express');
const app = express();

// This line is new: it tells Express to read JSON bodies.
// Without it, req.body is undefined.
app.use(express.json());

const todos = []; // Our list. In memory. Resets on restart.

// GET /todos — return the list
app.get('/todos', (req, res) => {
  res.json({ count: todos.length, todos });
});

// POST /todos — add a new todo
app.post('/todos', (req, res) => {
  // req.body is whatever JSON the client sent
  const { title } = req.body;

  // Make a todo object with an id
  const todo = { id: todos.length + 1, title, done: false };

  // Add it to the list
  todos.push(todo);

  // Send back the new todo with status 201 (Created)
  res.status(201).json(todo);
});

app.listen(3000, () => console.log('Server on http://localhost:3000'));
