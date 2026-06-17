// Notes API — Step 2. Adds: tags, full-text search, categories, archive.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT, category TEXT DEFAULT 'general', archived INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)`);
db.exec(`CREATE TABLE note_tags (note_id INTEGER, tag_id INTEGER, PRIMARY KEY (note_id, tag_id))`);

// === Full-text search via LIKE (no FTS extension needed) ===
app.get('/notes', (req, res) => {
  const { q, category, archived, tag, limit = 50 } = req.query;
  let query = `SELECT DISTINCT n.* FROM notes n ${tag ? 'LEFT JOIN note_tags nt ON nt.note_id = n.id LEFT JOIN tags t ON t.id = nt.tag_id' : ''} WHERE 1=1`;
  const params = [];
  if (q) { query += ' AND (n.title LIKE ? OR n.body LIKE ?)'; params.push('%' + q + '%', '%' + q + '%'); }
  if (category) { query += ' AND n.category = ?'; params.push(category); }
  if (archived !== undefined) { query += ' AND n.archived = ?'; params.push(archived === 'true' ? 1 : 0); }
  if (tag) { query += ' AND t.name = ?'; params.push(tag); }
  query += ' ORDER BY n.updated_at DESC LIMIT ?';
  params.push(parseInt(limit));
  const notes = db.prepare(query).all(...params);
  // Attach tags
  for (const note of notes) note.tags = db.prepare('SELECT t.name FROM tags t JOIN note_tags nt ON nt.tag_id = t.id WHERE nt.note_id = ?').all(note.id).map(t => t.name);
  res.json({ count: notes.length, notes });
});

app.post('/notes', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'missing_title' });
  const result = db.prepare('INSERT INTO notes (title, body, category) VALUES (?, ?, ?)').run(req.body.title, req.body.body || '', req.body.category || 'general');
  const noteId = result.lastInsertRowid;
  if (Array.isArray(req.body.tags)) {
    for (const name of req.body.tags) addTagToNote(noteId, name);
  }
  res.status(201).json(getNote(noteId));
});

app.get('/notes/:id', (req, res) => {
  const note = getNote(parseInt(req.params.id));
  note ? res.json(note) : res.status(404).json({ error: 'not_found' });
});

app.patch('/notes/:id', (req, res) => {
  const note = getNote(parseInt(req.params.id));
  if (!note) return res.status(404).json({ error: 'not_found' });
  const updates = [];
  const params = [];
  for (const field of ['title', 'body', 'category']) {
    if (req.body[field] !== undefined) { updates.push(`${field} = ?`); params.push(req.body[field]); }
  }
  if (req.body.archived !== undefined) { updates.push('archived = ?'); params.push(req.body.archived ? 1 : 0); }
  if (updates.length) {
    updates.push("updated_at = datetime('now')");
    params.push(note.id);
    db.prepare(`UPDATE notes SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  }
  if (Array.isArray(req.body.tags)) {
    db.prepare('DELETE FROM note_tags WHERE note_id = ?').run(note.id);
    for (const name of req.body.tags) addTagToNote(note.id, name);
  }
  res.json(getNote(note.id));
});

app.delete('/notes/:id', (req, res) => {
  db.prepare('DELETE FROM note_tags WHERE note_id = ?').run(parseInt(req.params.id));
  const result = db.prepare('DELETE FROM notes WHERE id = ?').run(parseInt(req.params.id));
  result.changes ? res.status(204).end() : res.status(404).json({ error: 'not_found' });
});

app.get('/tags', (req, res) => {
  const tags = db.prepare('SELECT t.name, COUNT(nt.note_id) as count FROM tags t LEFT JOIN note_tags nt ON nt.tag_id = t.id GROUP BY t.id ORDER BY count DESC').all();
  res.json({ tags });
});

function addTagToNote(noteId, name) {
  let tag = db.prepare('SELECT id FROM tags WHERE name = ?').get(name);
  if (!tag) tag = db.prepare('INSERT INTO tags (name) VALUES (?)').run(name);
  try { db.prepare('INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)').run(noteId, tag.lastInsertRowid || tag.id); } catch {}
}

function getNote(id) {
  const note = db.prepare('SELECT * FROM notes WHERE id = ?').get(id);
  if (!note) return null;
  note.tags = db.prepare('SELECT t.name FROM tags t JOIN note_tags nt ON nt.tag_id = t.id WHERE nt.note_id = ?').all(id).map(t => t.name);
  return note;
}

app.listen(3000, () => console.log('Notes API :3000 — GET/POST/PATCH/DELETE /notes, /tags'));
module.exports = app;
