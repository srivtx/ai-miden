// 02-todo-sqlite: Same as 01, but data lives in SQLite. Survives restarts.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database('todos.db');
db.exec(`CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);

const insert = db.prepare('INSERT INTO todos (title) VALUES (?)');
const selectAll = db.prepare('SELECT * FROM todos ORDER BY id DESC');
const selectOne = db.prepare('SELECT * FROM todos WHERE id = ?');
const update = db.prepare('UPDATE todos SET title = ?, done = ? WHERE id = ?');
const del = db.prepare('DELETE FROM todos WHERE id = ?');

app.get('/todos', (req, res) => res.json({ count: db.prepare('SELECT COUNT(*) as c FROM todos').get().c, todos: selectAll.all() }));

app.post('/todos', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title is required' });
  const result = insert.run(req.body.title);
  res.status(201).json(selectOne.get(result.lastInsertRowid));
});

app.patch('/todos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const todo = selectOne.get(id);
  if (!todo) return res.status(404).json({ error: 'Not found' });
  update.run(
    req.body.title !== undefined ? req.body.title : todo.title,
    req.body.done !== undefined ? (req.body.done ? 1 : 0) : todo.done,
    id
  );
  res.json(selectOne.get(id));
});

app.delete('/todos/:id', (req, res) => {
  const result = del.run(parseInt(req.params.id));
  result.changes ? res.status(204).end() : res.status(404).json({ error: 'Not found' });
});

app.listen(3000, () => console.log('02-todo-sqlite on :3000'));
