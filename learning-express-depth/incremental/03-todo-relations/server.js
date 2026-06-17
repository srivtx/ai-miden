// 03-todo-relations: Add tags (many-to-many) and categories (one-to-many).
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL);
  CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER DEFAULT 0, category_id INTEGER REFERENCES categories(id), created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
  CREATE TABLE todo_tags (todo_id INTEGER, tag_id INTEGER, PRIMARY KEY (todo_id, tag_id));
`);

const insertCategory = db.prepare('INSERT INTO categories (name) VALUES (?)');
const insertTodo = db.prepare('INSERT INTO todos (title, category_id) VALUES (?, ?)');
const insertTag = db.prepare('INSERT INTO tags (name) VALUES (?)');
const linkTag = db.prepare('INSERT OR IGNORE INTO todo_tags (todo_id, tag_id) VALUES (?, ?)');
const findTag = db.prepare('SELECT id FROM tags WHERE name = ?');

const getTodoWithTags = (id) => {
  const todo = db.prepare('SELECT t.*, c.name as category FROM todos t LEFT JOIN categories c ON c.id = t.category_id WHERE t.id = ?').get(id);
  if (!todo) return null;
  todo.tags = db.prepare('SELECT tag.name FROM tags tag JOIN todo_tags tt ON tt.tag_id = tag.id WHERE tt.todo_id = ?').all(id).map(t => t.name);
  return todo;
};

// Categories
app.post('/categories', (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'name required' });
  try {
    const result = insertCategory.run(req.body.name);
    res.status(201).json({ id: result.lastInsertRowid, name: req.body.name });
  } catch (e) { res.status(409).json({ error: 'category exists' }); }
});

app.get('/categories', (req, res) => res.json({ categories: db.prepare('SELECT * FROM categories').all() }));

// Todos
app.get('/todos', (req, res) => {
  const { category, tag, q } = req.query;
  let query = 'SELECT DISTINCT t.* FROM todos t';
  const params = [];
  if (tag) {
    query += ' JOIN todo_tags tt ON tt.todo_id = t.id JOIN tags tag ON tag.id = tt.tag_id';
  }
  query += ' WHERE 1=1';
  if (category) { query += ' AND t.category_id = (SELECT id FROM categories WHERE name = ?)'; params.push(category); }
  if (tag) { query += ' AND tag.name = ?'; params.push(tag); }
  if (q) { query += ' AND t.title LIKE ?'; params.push('%' + q + '%'); }
  query += ' ORDER BY t.id DESC';
  const todos = db.prepare(query).all(...params).map(t => getTodoWithTags(t.id));
  res.json({ count: todos.length, todos });
});

app.post('/todos', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  let categoryId = null;
  if (req.body.category) {
    const cat = db.prepare('SELECT id FROM categories WHERE name = ?').get(req.body.category);
    if (cat) categoryId = cat.id;
    else {
      const r = insertCategory.run(req.body.category);
      categoryId = r.lastInsertRowid;
    }
  }
  const result = insertTodo.run(req.body.title, categoryId);
  const todoId = result.lastInsertRowid;
  if (Array.isArray(req.body.tags)) {
    for (const name of req.body.tags) {
      let tag = findTag.get(name);
      if (!tag) tag = insertTag.run(name);
      linkTag.run(todoId, tag.lastInsertRowid || tag.id);
    }
  }
  res.status(201).json(getTodoWithTags(todoId));
});

app.delete('/todos/:id', (req, res) => {
  db.prepare('DELETE FROM todo_tags WHERE todo_id = ?').run(parseInt(req.params.id));
  const r = db.prepare('DELETE FROM todos WHERE id = ?').run(parseInt(req.params.id));
  r.changes ? res.status(204).end() : res.status(404).json({ error: 'Not found' });
});

app.listen(3000, () => console.log('03-todo-relations on :3000'));
