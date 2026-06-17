// 58 — Helmet
// NEW CONCEPT: security headers in one line.
// Helmet sets a bunch of HTTP headers that protect against common attacks.
const express = require('express');
const helmet = require('helmet');
const app = express();

// One line: many security headers
app.use(helmet());

app.get('/', (req, res) => res.json({ message: 'Hello with security headers' }));

app.listen(3000, () => console.log('Helmet on http://localhost:3000'));
