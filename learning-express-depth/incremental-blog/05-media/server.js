// 05-media: Upload images and other media. Posts can have featured images.
const express = require('express');
const Database = require('better-sqlite3');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const UPLOADS = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOADS)) fs.mkdirSync(UPLOADS);

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE media (id TEXT PRIMARY KEY, filename TEXT, original_name TEXT, mime_type TEXT, size_bytes INTEGER, width INTEGER, height INTEGER, alt_text TEXT, uploaded_by TEXT, created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT, body TEXT, featured_media_id TEXT, status TEXT DEFAULT 'draft', author_id TEXT);
`);

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS),
  filename: (req, file, cb) => cb(null, crypto.randomBytes(8).toString('hex') + path.extname(file.originalname)),
});
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },  // 10MB
  fileFilter: (req, file, cb) => {
    if (/^image\//.test(file.mimetype)) cb(null, true);
    else cb(new Error('only images allowed'));
  },
});

// Upload an image
app.post('/media', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'no file' });
  const id = 'm_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO media (id, filename, original_name, mime_type, size_bytes, uploaded_by) VALUES (?, ?, ?, ?, ?, ?)').run(id, req.file.filename, req.file.originalname, req.file.mimetype, req.file.size, req.headers['x-user-id'] || null);
  res.status(201).json({ id, url: `/media/${req.file.filename}`, original_name: req.file.originalname, size: req.file.size, type: req.file.mimetype });
});

// Get media info
app.get('/media/:id', (req, res) => {
  const m = db.prepare('SELECT * FROM media WHERE id = ?').get(req.params.id);
  if (!m) return res.status(404).json({ error: 'not found' });
  res.json(m);
});

// Serve the file
app.get('/media-file/:filename', (req, res) => {
  const safe = path.basename(req.params.filename);
  const fp = path.join(UPLOADS, safe);
  if (!fs.existsSync(fp)) return res.status(404).json({ error: 'not found' });
  res.sendFile(fp);
});

// Set alt text
app.patch('/media/:id', (req, res) => {
  if (!req.body.alt_text) return res.status(422).json({ error: 'alt_text required' });
  const r = db.prepare('UPDATE media SET alt_text = ? WHERE id = ?').run(req.body.alt_text, req.params.id);
  r.changes ? res.json({ id: req.params.id, alt_text: req.body.alt_text }) : res.status(404).json({ error: 'not found' });
});

// Create a post with a featured image
app.post('/posts', (req, res) => {
  const { title, body, featured_media_id, author_id } = req.body;
  if (!title) return res.status(422).json({ error: 'title required' });
  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const r = db.prepare('INSERT INTO posts (title, body, featured_media_id, author_id, slug) VALUES (?, ?, ?, ?, ?)').run(title, body || '', featured_media_id, author_id, slug);
  res.status(201).json({ id: r.lastInsertRowid, slug, featured_media_id });
});

app.listen(3000, () => console.log('05-media on :3000'));
