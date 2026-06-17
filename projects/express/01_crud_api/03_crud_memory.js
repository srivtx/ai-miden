// 03_crud_memory.js — Full CRUD with in-memory storage. Learn: data modeling, state management.

const express = require('express');
const app = express();
app.use(express.json());

// ---- The "database" — a plain array ----
let users = [];
let nextId = 1;

// ---- Helper: find user by id ----
function findUser(id) {
  return users.find(u => u.id === parseInt(id));
}

// CREATE
app.post('/users', (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) return res.status(400).json({ error: 'name and email required' });
  const user = { id: nextId++, name, email, createdAt: new Date().toISOString() };
  users.push(user);
  res.status(201).json(user);
});

// READ all
app.get('/users', (req, res) => {
  const { sort } = req.query;
  let result = [...users];
  if (sort === 'name') result.sort((a, b) => a.name.localeCompare(b.name));
  res.json({ count: result.length, users: result });
});

// READ one
app.get('/users/:id', (req, res) => {
  const user = findUser(req.params.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json(user);
});

// UPDATE
app.put('/users/:id', (req, res) => {
  const user = findUser(req.params.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  const { name, email } = req.body;
  if (name) user.name = name;
  if (email) user.email = email;
  res.json(user);
});

// PATCH (partial update — safer than PUT for some use cases)
app.patch('/users/:id', (req, res) => {
  const user = findUser(req.params.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  Object.assign(user, req.body); // merge all fields
  res.json(user);
});

// DELETE
app.delete('/users/:id', (req, res) => {
  const idx = users.findIndex(u => u.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'User not found' });
  users.splice(idx, 1);
  res.status(204).send(); // 204 = success, no body
});

app.listen(3000, () => console.log('CRUD API on :3000'));
/*
Test:
  curl -X POST localhost:3000/users -H "Content-Type: application/json" -d '{"name":"Zen","email":"z@t.com"}'
  curl -X POST localhost:3000/users -H "Content-Type: application/json" -d '{"name":"Ava","email":"a@t.com"}'
  curl localhost:3000/users
  curl localhost:3000/users?sort=name
  curl localhost:3000/users/1
  curl -X PUT localhost:3000/users/1 -H "Content-Type: application/json" -d '{"name":"ZenX"}'
  curl -X PATCH localhost:3000/users/1 -H "Content-Type: application/json" -d '{"email":"new@t.com"}'
  curl -X DELETE localhost:3000/users/2
*/
