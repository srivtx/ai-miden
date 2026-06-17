// 55 — Encryption
// NEW CONCEPT: encrypt data at rest.
// Hashing is one-way (we did this in project 14).
// Encryption is two-way: encrypt to hide, decrypt to read.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// Encryption key (in production, store in env var or secret manager)
const KEY = Buffer.from('12345678901234567890123456789012');  // 32 bytes for AES-256

// Encrypt
function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', KEY, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

// Decrypt
function decrypt(encrypted) {
  const [ivHex, encryptedHex] = encrypted.split(':');
  const iv = Buffer.from(ivHex, 'hex');
  const decipher = crypto.createDecipheriv('aes-256-cbc', KEY, iv);
  let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

// Store notes (encrypted at rest)
const notes = [];

app.post('/notes', (req, res) => {
  const { text } = req.body;
  if (!text) return res.status(422).json({ error: 'text required' });
  // Encrypt before storing
  const encrypted = encrypt(text);
  const note = { id: notes.length + 1, encrypted, createdAt: new Date().toISOString() };
  notes.push(note);
  // Return id only, NOT the encrypted text
  res.status(201).json({ id: note.id });
});

// Get a note (decrypt before returning)
app.get('/notes/:id', (req, res) => {
  const note = notes.find(n => n.id === parseInt(req.params.id));
  if (!note) return res.status(404).json({ error: 'Not found' });
  // Decrypt
  const text = decrypt(note.encrypted);
  res.json({ id: note.id, text, createdAt: note.createdAt });
});

// Admin: see the raw encrypted form (for debugging)
app.get('/admin/notes', (req, res) => {
  res.json({ notes: notes.map(n => ({ id: n.id, encrypted: n.encrypted })) });
});

app.listen(3000, () => console.log('Encryption on http://localhost:3000'));
