// 05-versions: Every upload creates a version. Restore old versions, see history.
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
db.exec(`CREATE TABLE files (id TEXT PRIMARY KEY, user_id TEXT, current_version INTEGER DEFAULT 0)`);
db.exec(`CREATE TABLE versions (id INTEGER PRIMARY KEY AUTOINCREMENT, file_id TEXT, version_number INTEGER, filename TEXT, size_bytes INTEGER, uploaded_by TEXT, message TEXT, created_at TEXT DEFAULT (datetime('now')))`);

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS),
  filename: (req, file, cb) => cb(null, crypto.randomBytes(8).toString('hex') + path.extname(file.originalname)),
});
const upload = multer({ storage, limits: { fileSize: 100 * 1024 * 1024 } });

// Create a file (with first version)
app.post('/files', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'no file' });
  const id = 'f_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO files (id, user_id, current_version) VALUES (?, ?, 1)').run(id, req.body.user_id);
  db.prepare('INSERT INTO versions (file_id, version_number, filename, size_bytes, uploaded_by, message) VALUES (?, 1, ?, ?, ?, ?)').run(id, req.file.filename, req.file.size, req.body.user_id, req.body.message || 'initial');
  res.status(201).json({ id, version: 1 });
});

// New version
app.post('/files/:id/versions', upload.single('file'), (req, res) => {
  const file = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  if (!file) return res.status(404).json({ error: 'not found' });
  if (!req.file) return res.status(400).json({ error: 'no file' });
  const newVersion = file.current_version + 1;
  db.prepare('UPDATE files SET current_version = ? WHERE id = ?').run(newVersion, file.id);
  db.prepare('INSERT INTO versions (file_id, version_number, filename, size_bytes, uploaded_by, message) VALUES (?, ?, ?, ?, ?, ?)').run(file.id, newVersion, req.file.filename, req.file.size, req.body.user_id, req.body.message);
  res.status(201).json({ id: file.id, version: newVersion });
});

// List versions
app.get('/files/:id/versions', (req, res) => {
  const versions = db.prepare('SELECT id, version_number, size_bytes, uploaded_by, message, created_at FROM versions WHERE file_id = ? ORDER BY version_number DESC').all(req.params.id);
  res.json({ file_id: req.params.id, versions });
});

// Get a specific version
app.get('/files/:id/versions/:v', (req, res) => {
  const v = db.prepare('SELECT * FROM versions WHERE file_id = ? AND version_number = ?').get(req.params.id, parseInt(req.params.v));
  if (!v) return res.status(404).json({ error: 'not found' });
  const fp = path.join(UPLOADS, v.filename);
  if (fs.existsSync(fp)) res.sendFile(fp);
  else res.status(404).json({ error: 'file missing' });
});

// Restore an old version (creates a new version that's a copy)
app.post('/files/:id/restore/:v', (req, res) => {
  const file = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  if (!file) return res.status(404).json({ error: 'not found' });
  const oldV = db.prepare('SELECT * FROM versions WHERE file_id = ? AND version_number = ?').get(file.id, parseInt(req.params.v));
  if (!oldV) return res.status(404).json({ error: 'version not found' });
  const newVersion = file.current_version + 1;
  db.prepare('UPDATE files SET current_version = ? WHERE id = ?').run(newVersion, file.id);
  db.prepare('INSERT INTO versions (file_id, version_number, filename, size_bytes, uploaded_by, message) VALUES (?, ?, ?, ?, ?, ?)').run(file.id, newVersion, oldV.filename, oldV.size_bytes, req.body.user_id, `restored from v${oldV.version_number}`);
  res.json({ id: file.id, new_version: newVersion, restored_from: oldV.version_number });
});

app.listen(3000, () => console.log('05-versions on :3000'));
