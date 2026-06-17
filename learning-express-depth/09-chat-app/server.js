// 09 — Chat App
// A chat is different from a todo: there are messages from many users.
// We add: rooms (like channels), and a from field on each message.
const express = require('express');
const app = express();
app.use(express.json());

// messages is an array, but each message belongs to a room.
const messages = [];

// Get all messages in a room
app.get('/rooms/:room/messages', (req, res) => {
  const room = req.params.room;
  const roomMessages = messages.filter(m => m.room === room);
  res.json({ room, count: roomMessages.length, messages: roomMessages });
});

// Post a message to a room
app.post('/rooms/:room/messages', (req, res) => {
  const room = req.params.room;
  const { from, text } = req.body;
  const message = {
    id: messages.length + 1,
    room,
    from,
    text,
    sentAt: new Date().toISOString(),
  };
  messages.push(message);
  res.status(201).json(message);
});

app.listen(3000, () => console.log('Chat server on http://localhost:3000'));
