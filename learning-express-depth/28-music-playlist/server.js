// 28 — Music Playlist
// A playlist has songs. Songs are inside playlists (nested).
const express = require('express');
const app = express();
app.use(express.json());

const playlists = [];

// Create a playlist
app.post('/playlists', (req, res) => {
  const { name } = req.body;
  const playlist = { id: playlists.length + 1, name, songs: [] };
  playlists.push(playlist);
  res.status(201).json(playlist);
});

app.get('/playlists', (req, res) => {
  res.json({ count: playlists.length, playlists });
});

app.get('/playlists/:id', (req, res) => {
  const playlist = playlists.find(p => p.id === parseInt(req.params.id));
  if (!playlist) return res.status(404).json({ error: 'Playlist not found' });
  res.json(playlist);
});

// Add a song to a playlist
app.post('/playlists/:id/songs', (req, res) => {
  const playlist = playlists.find(p => p.id === parseInt(req.params.id));
  if (!playlist) return res.status(404).json({ error: 'Playlist not found' });
  const { title, artist } = req.body;
  const song = { id: playlist.songs.length + 1, title, artist };
  playlist.songs.push(song);
  res.status(201).json(playlist);
});

// Remove a song
app.delete('/playlists/:id/songs/:songId', (req, res) => {
  const playlist = playlists.find(p => p.id === parseInt(req.params.id));
  if (!playlist) return res.status(404).json({ error: 'Playlist not found' });
  const index = playlist.songs.findIndex(s => s.id === parseInt(req.params.songId));
  if (index === -1) return res.status(404).json({ error: 'Song not found' });
  playlist.songs.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Music playlist on http://localhost:3000'));
