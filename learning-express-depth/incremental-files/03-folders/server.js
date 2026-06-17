// 03-folders: Hierarchical folders. Folders can contain files and other folders.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE folders (id TEXT PRIMARY KEY, name TEXT NOT NULL, parent_id TEXT, user_id TEXT, created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE files (id TEXT PRIMARY KEY, folder_id TEXT, name TEXT, size_bytes INTEGER, mime_type TEXT, created_at TEXT DEFAULT (datetime('now')));
`);

function getFolderPath(id) {
  const path = [];
  let current = id;
  while (current) {
    const folder = db.prepare('SELECT * FROM folders WHERE id = ?').get(current);
    if (!folder) break;
    path.unshift(folder.name);
    current = folder.parent_id;
  }
  return '/' + path.join('/');
}

// Create a folder
app.post('/folders', (req, res) => {
  const { name, parent_id, user_id } = req.body;
  if (!name) return res.status(422).json({ error: 'name required' });
  if (parent_id && !db.prepare('SELECT id FROM folders WHERE id = ?').get(parent_id)) {
    return res.status(422).json({ error: 'parent not found' });
  }
  const id = 'd_' + Math.random().toString(36).slice(2, 10);
  try {
    db.prepare('INSERT INTO folders VALUES (?, ?, ?, ?, ?)').run(id, name, parent_id || null, user_id, new Date().toISOString());
    res.status(201).json({ id, name, parent_id, path: getFolderPath(id) });
  } catch (e) { res.status(409).json({ error: 'folder exists' }); }
});

// List folder contents
app.get('/folders/:id', (req, res) => {
  const folder = req.params.id === 'root' ? null : db.prepare('SELECT * FROM folders WHERE id = ?').get(req.params.id);
  if (req.params.id !== 'root' && !folder) return res.status(404).json({ error: 'not found' });
  const parentId = folder ? folder.id : null;
  const subfolders = db.prepare('SELECT * FROM folders WHERE parent_id IS ? ORDER BY name').all(parentId);
  const files = db.prepare('SELECT * FROM files WHERE folder_id IS ? ORDER BY name').all(parentId);
  res.json({
    folder: folder || { id: 'root', name: 'root', path: '/' },
    subfolders,
    files,
  });
});

// Move folder
app.patch('/folders/:id/move', (req, res) => {
  const folder = db.prepare('SELECT * FROM folders WHERE id = ?').get(req.params.id);
  if (!folder) return res.status(404).json({ error: 'not found' });
  const { new_parent_id } = req.body;
  if (new_parent_id === folder.id) return res.status(422).json({ error: 'cannot move into self' });
  db.prepare('UPDATE folders SET parent_id = ? WHERE id = ?').run(new_parent_id || null, folder.id);
  res.json({ id: folder.id, new_parent_id });
});

app.listen(3000, () => console.log('03-folders on :3000'));
