// 42 — File Upload
// NEW CONCEPT: receiving files from clients.
// JSON in the body is one thing. Files are different — they use multipart/form-data.
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const app = express();

// Create an uploads folder
const UPLOADS = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOADS)) fs.mkdirSync(UPLOADS);

// Configure multer (the file upload library)
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS),
  filename: (req, file, cb) => {
    // Generate a random filename so files don't overwrite each other
    const id = crypto.randomBytes(8).toString('hex');
    const ext = path.extname(file.originalname);
    cb(null, id + ext);
  },
});
const upload = multer({ storage, limits: { fileSize: 5 * 1024 * 1024 } });  // 5MB max

// Upload a single file
app.post('/upload', upload.single('file'), (req, res) => {
  res.json({
    id: req.file.filename,
    originalName: req.file.originalname,
    size: req.file.size,
    mimetype: req.file.mimetype,
  });
});

// Upload multiple files
app.post('/upload-many', upload.array('files', 10), (req, res) => {
  res.json({
    count: req.files.length,
    files: req.files.map(f => ({ id: f.filename, name: f.originalname, size: f.size })),
  });
});

// Download a file
app.get('/files/:id', (req, res) => {
  const safe = path.basename(req.params.id);  // Prevent path traversal
  const filePath = path.join(UPLOADS, safe);
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'Not found' });
  res.sendFile(filePath);
});

app.listen(3000, () => console.log('File upload on http://localhost:3000'));
