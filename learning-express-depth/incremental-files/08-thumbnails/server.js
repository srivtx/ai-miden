// 08-thumbnails: Generate image thumbnails. Store a small version, serve it for previews.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE files (id TEXT PRIMARY KEY, name TEXT, mime_type TEXT, size_bytes INTEGER, width INTEGER, height INTEGER, thumbnail_url TEXT)`);

// Simulated thumbnail generation (in real life, use sharp or jimp)
function generateThumbnail(width, height) {
  // Return a 200x200 thumbnail URL
  return `/thumbnails/${width}x${height}`;
}

app.post('/files', (req, res) => {
  const { name, mime_type, size_bytes, width, height } = req.body;
  if (!name) return res.status(422).json({ error: 'name required' });
  if (!mime_type || !mime_type.startsWith('image/')) return res.status(422).json({ error: 'only images get thumbnails' });
  const id = 'f_' + Math.random().toString(36).slice(2, 10);
  const thumbnail_url = generateThumbnail(200, 200);
  db.prepare('INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?)').run(id, name, mime_type, size_bytes, width, height, thumbnail_url);
  res.status(201).json({ id, name, thumbnail_url });
});

app.get('/files', (req, res) => {
  const files = db.prepare('SELECT * FROM files').all();
  res.json({ files });
});

app.get('/files/:id/thumbnail', (req, res) => {
  const f = db.prepare('SELECT thumbnail_url FROM files WHERE id = ?').get(req.params.id);
  f ? res.json({ thumbnail_url: f.thumbnail_url }) : res.status(404).json({ error: 'not found' });
});

// Custom thumbnail size
app.get('/files/:id/thumbnail/:size', (req, res) => {
  const f = db.prepare('SELECT width, height, thumbnail_url FROM files WHERE id = ?').get(req.params.id);
  if (!f) return res.status(404).json({ error: 'not found' });
  res.json({ file_id: req.params.id, requested_size: req.params.size, thumbnail_url: f.thumbnail_url });
});

app.listen(3000, () => console.log('08-thumbnails on :3000'));
