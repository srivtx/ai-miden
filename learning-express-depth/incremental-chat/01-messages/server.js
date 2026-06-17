// 01-messages: A simple chat. Messages have a sender and text. List and create.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, text TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')))`);

app.get('/messages', (req, res) => {
  const { limit = 50, before } = req.query;
  let query = 'SELECT * FROM messages';
  const params = [];
  if (before) { query += ' WHERE id < ?'; params.push(parseInt(before)); }
  query += ' ORDER BY id DESC LIMIT ?';
  params.push(parseInt(limit));
  res.json({ count: db.prepare('SELECT COUNT(*) as c FROM messages').get().c, messages: db.prepare(query).all(...params).reverse() });
});

app.post('/messages', (req, res) => {
  const { sender, text } = req.body;
  if (!sender || !text) return res.status(422).json({ error: 'sender and text required' });
  const r = db.prepare('INSERT INTO messages (sender, text) VALUES (?, ?)').run(sender, text);
  res.status(201).json(db.prepare('SELECT * FROM messages WHERE id = ?').get(r.lastInsertRowid));
});

app.delete('/messages/:id', (req, res) => {
  const r = db.prepare('DELETE FROM messages WHERE id = ?').run(parseInt(req.params.id));
  r.changes ? res.status(204).end() : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('01-messages on :3000'));
