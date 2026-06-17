// 07-files: Upload files and share them in chat. Image previews, file metadata.
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
db.exec(`CREATE TABLE files (id TEXT PRIMARY KEY, filename TEXT, original_name TEXT, mime_type TEXT, size_bytes INTEGER, uploader_id TEXT, room_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, room_id TEXT, user_id TEXT, text TEXT, file_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);

const ALLOWED = /^image\//.test.bind(/^image\//) || ((m) => /^(image|application\/pdf|text)/.test(m));
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS),
  filename: (req, file, cb) => cb(null, crypto.randomBytes(8).toString('hex') + path.extname(file.originalname)),
});
const upload = multer({ storage, limits: { fileSize: 25 * 1024 * 1024 } });

// Upload a file (and post it as a message in a room)
app.post('/rooms/:id/files', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'no file' });
  const { user_id } = req.body;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  const fileId = 'f_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO files (id, filename, original_name, mime_type, size_bytes, uploader_id, room_id) VALUES (?, ?, ?, ?, ?, ?, ?)').run(fileId, req.file.filename, req.file.originalname, req.file.mimetype, req.file.size, user_id, req.params.id);
  // Also create a message for it
  const msgResult = db.prepare('INSERT INTO messages (room_id, user_id, text, file_id) VALUES (?, ?, ?, ?)').run(req.params.id, user_id, `Shared a file: ${req.file.originalname}`, fileId);
  res.status(201).json({ file_id: fileId, message_id: msgResult.lastInsertRowid, url: `/files/${req.file.filename}`, mime_type: req.file.mimetype, size: req.file.size });
});

// Get file info
app.get('/files/:id', (req, res) => {
  const f = db.prepare('SELECT * FROM files WHERE id = ?').get(req.params.id);
  if (!f) return res.status(404).json({ error: 'not found' });
  res.json(f);
});

// Download a file
app.get('/files-download/:filename', (req, res) => {
  const safe = path.basename(req.params.filename);
  const fp = path.join(UPLOADS, safe);
  if (!fs.existsSync(fp)) return res.status(404).json({ error: 'not found' });
  res.sendFile(fp);
});

app.listen(3000, () => console.log('07-files on :3000 (upload with multipart)'));
