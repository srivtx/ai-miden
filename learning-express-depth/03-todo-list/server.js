// 03 — Todo List (empty)
// Goal: an endpoint that returns the list of todos.
// Right now the list is empty. We just send back an empty array.
const express = require('express');
const app = express();

const todos = []; // An array in memory. Will hold our todos.

app.get('/todos', (req, res) => {
  res.json({ count: todos.length, todos });
});

app.listen(3000, () => console.log('Server on http://localhost:3000'));
