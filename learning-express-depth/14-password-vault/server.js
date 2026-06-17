// 14 — Password Vault
// Same CRUD. Each item has a name (e.g. "Gmail") and a password.
// We never store the password in plain text. We hash it.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const vault = [];

// Simple hash. In a real app, use bcrypt.
function hash(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}

app.get('/vault', (req, res) => {
  // Never return the hash. Just say which entries exist.
  res.json({ count: vault.length, items: vault.map(v => ({ id: v.id, name: v.name })) });
});

app.post('/vault', (req, res) => {
  const { name, password } = req.body;
  const item = { id: vault.length + 1, name, passwordHash: hash(password), createdAt: new Date().toISOString() };
  vault.push(item);
  // Don't return the hash either — only the id and name
  res.status(201).json({ id: item.id, name: item.name });
});

app.listen(3000, () => console.log('Vault server on http://localhost:3000'));
