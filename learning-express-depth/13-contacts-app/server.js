// 13 — Contacts App
// Same CRUD. Contacts have name, email, phone.
// NEW: lookup by email (GET /contacts/by-email/:email).
const express = require('express');
const app = express();
app.use(express.json());

const contacts = [];

app.get('/contacts', (req, res) => {
  res.json({ count: contacts.length, contacts });
});

app.post('/contacts', (req, res) => {
  const { name, email, phone } = req.body;
  if (contacts.some(c => c.email === email)) {
    return res.status(409).json({ error: 'Contact with this email already exists' });
  }
  const contact = { id: contacts.length + 1, name, email, phone: phone || '' };
  contacts.push(contact);
  res.status(201).json(contact);
});

app.get('/contacts/by-email/:email', (req, res) => {
  const contact = contacts.find(c => c.email === req.params.email);
  if (!contact) return res.status(404).json({ error: 'Contact not found' });
  res.json(contact);
});

app.delete('/contacts/:id', (req, res) => {
  const index = contacts.findIndex(c => c.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Contact not found' });
  contacts.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Contacts server on http://localhost:3000'));
