// 21 — Emoji App
// A list of emojis with their names. Search by name.
const express = require('express');
const app = express();

// Hardcoded data — no POST needed for this one
const emojis = [
  { char: '😀', name: 'grinning' },
  { char: '😂', name: 'laughing' },
  { char: '😍', name: 'heart eyes' },
  { char: '🤔', name: 'thinking' },
  { char: '😎', name: 'cool' },
  { char: '🥳', name: 'party' },
  { char: '😴', name: 'sleeping' },
  { char: '🤯', name: 'mind blown' },
  { char: '❤️', name: 'heart' },
  { char: '🔥', name: 'fire' },
  { char: '⭐', name: 'star' },
  { char: '🎉', name: 'celebration' },
];

// Search by name
app.get('/emojis', (req, res) => {
  const { q } = req.query;
  let result = emojis;
  if (q) {
    result = result.filter(e => e.name.toLowerCase().includes(q.toLowerCase()));
  }
  res.json({ count: result.length, emojis: result });
});

// Random emoji
app.get('/emojis/random', (req, res) => {
  const emoji = emojis[Math.floor(Math.random() * emojis.length)];
  res.json(emoji);
});

app.listen(3000, () => console.log('Emoji server on http://localhost:3000'));
