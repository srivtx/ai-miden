// 07_file_upload.js — Single + multiple file upload with multer. Learn: storage, validation, limits.

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const app = express();

// ---- Storage configuration ----
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const dir = './uploads';
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    cb(null, dir);
  },
  filename: (req, file, cb) => {
    const unique = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, unique + path.extname(file.originalname)); // e.g., 1712345678-abc123.jpg
  }
});

// ---- File filter: only images ----
const imageFilter = (req, file, cb) => {
  const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  if (allowed.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error('Only JPEG, PNG, GIF, and WebP allowed'), false);
  }
};

// ---- Upload middlewares ----
const uploadSingle = multer({ storage, fileFilter: imageFilter, limits: { fileSize: 5 * 1024 * 1024 } }).single('avatar');
const uploadMulti = multer({ storage, fileFilter: imageFilter, limits: { fileSize: 10 * 1024 * 1024 } }).array('photos', 5);

// ---- HTML form for testing ----
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'upload.html'));
});

// ---- Single file upload ----
app.post('/upload/avatar', (req, res, next) => {
  uploadSingle(req, res, (err) => {
    if (err) {
      if (err.code === 'LIMIT_FILE_SIZE') return res.status(400).json({ error: 'File too large (max 5MB)' });
      return res.status(400).json({ error: err.message });
    }
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    res.json({
      message: 'Avatar uploaded',
      file: { filename: req.file.filename, original: req.file.originalname, size: req.file.size, path: req.file.path }
    });
  });
});

// ---- Multiple file upload ----
app.post('/upload/photos', (req, res, next) => {
  uploadMulti(req, res, (err) => {
    if (err) return res.status(400).json({ error: err.message });
    if (!req.files || req.files.length === 0) return res.status(400).json({ error: 'No files uploaded' });

    res.json({
      message: `${req.files.length} photos uploaded`,
      files: req.files.map(f => ({ filename: f.filename, original: f.originalname, size: f.size }))
    });
  });
});

app.listen(3000, () => console.log('Upload server on http://localhost:3000'));
/*
  curl -F "avatar=@/path/to/photo.jpg" localhost:3000/upload/avatar
  curl -F "photos=@a.jpg" -F "photos=@b.jpg" localhost:3000/upload/photos
*/
