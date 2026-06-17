// 08-todo-versioning: Optimistic locking. Client sends the version they last saw. Server rejects if it's stale.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0, version INTEGER DEFAULT 1, updated_at TEXT DEFAULT (datetime('now')))`);

app.post('/todos', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const r = db.prepare('INSERT INTO todos (title) VALUES (?)').run(req.body.title);
  res.status(201).json(db.prepare('SELECT * FROM todos WHERE id = ?').get(r.lastInsertRowid));
});

app.get('/todos/:id', (req, res) => {
  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(parseInt(req.params.id));
  todo ? res.json(todo) : res.status(404).json({ error: 'not found' });
});

// Update with optimistic locking
app.patch('/todos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const { version, ...changes } = req.body;

  if (version === undefined) return res.status(428).json({ error: 'version required for update' });

  const todo = db.prepare('SELECT * FROM todos WHERE id = ?').get(id);
  if (!todo) return res.status(404).json({ error: 'not found' });

  if (todo.version !== version) {
    return res.status(409).json({
      error: 'version conflict',
      yourVersion: version,
      currentVersion: todo.version,
      current: todo,
    });
  }

  const updates = [];
  const params = [];
  if (changes.title !== undefined) { updates.push('title = ?'); params.push(changes.title); }
  if (changes.done !== undefined) { updates.push('done = ?'); params.push(changes.done ? 1 : 0); }
  if (!updates.length) return res.status(422).json({ error: 'no updates' });

  updates.push('version = version + 1');
  updates.push("updated_at = datetime('now')");
  params.push(id);
  db.prepare(`UPDATE todos SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  res.json(db.prepare('SELECT * FROM todos WHERE id = ?').get(id));
});

app.listen(3000, () => console.log('08-todo-versioning on :3000'));
