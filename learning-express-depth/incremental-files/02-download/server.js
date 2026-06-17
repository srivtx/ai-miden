// 02-download: Serve the file. Stream large files. Range requests (partial content).
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
db.exec(`CREATE TABLE files (id TEXT PRIMARY KEY, user_id TEXT, filename TEXT, original_name TEXT, mime_type TEXT, size_bytes INTEGER, sha256 TEXT, created_at TEXT DEFAULT (datetime('now')))`);

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS),
  filename: (req, file, cb) => cb(null, crypto.randomBytes(16).toString('hex') + path.extname(file.originalname)),
});
const upload = multer({ storage, limits: { fileSize: 100 * 1024 * 1024 } });

app.post('/files', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'no file' });
  const fileBuffer = fs.readFileSync(req.file.path);
  const sha256 = crypto.createHash('sha256').update(fileBuffer).digest('hex');
  const id = 'f_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(id, req.body.user_id || null, req.file.filename, req.file.originalname, req.file.mimetype, req.file.size, sha256, new Date().toISOString());
  res.status(201).json({ id, filename: req.file.originalname, size: req.file.size, mime_type: req.file.mimetype, sha256 });
});

app.get('/files/:id', (req, res) => {
  const f = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  f ? res.json({ id: f.id, filename: f.original_name, size: f.size_bytes, mime_type: f.mime_type, sha256: f.sha256 }) : res.status(404).json({ error: 'not found' });
});

// Download the file
app.get('/files/:id/download', (req, res) => {
  const f = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  if (!f) return res.status(404).json({ error: 'not found' });
  const filePath = path.join(UPLOADS, f.filename);
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'file missing' });
  res.set('Content-Type', f.mime_type);
  res.set('Content-Disposition', `attachment; filename="${f.original_name}"`);
  res.set('Content-Length', f.size_bytes);
  fs.createReadStream(filePath).pipe(res);
});

// Preview (inline, not download)
app.get('/files/:id/preview', (req, res) => {
  const f = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  if (!f) return res.status(404).json({ error: 'not found' });
  const filePath = path.join(UPLOADS, f.filename);
  res.set('Content-Type', f.mime_type);
  res.set('Content-Disposition', 'inline');
  fs.createReadStream(filePath).pipe(res);
});

app.listen(3000, () => console.log('02-download on :3000'));
