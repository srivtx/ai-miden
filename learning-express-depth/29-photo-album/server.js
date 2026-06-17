// 29 — Photo Album
// Albums have photos. Same nested pattern as playlists.
const express = require('express');
const app = express();
app.use(express.json());

const albums = [];

app.post('/albums', (req, res) => {
  const { title } = req.body;
  const album = { id: albums.length + 1, title, photos: [], createdAt: new Date().toISOString() };
  albums.push(album);
  res.status(201).json(album);
});

app.get('/albums', (req, res) => {
  res.json({ count: albums.length, albums });
});

app.get('/albums/:id', (req, res) => {
  const album = albums.find(a => a.id === parseInt(req.params.id));
  if (!album) return res.status(404).json({ error: 'Album not found' });
  res.json(album);
});

app.post('/albums/:id/photos', (req, res) => {
  const album = albums.find(a => a.id === parseInt(req.params.id));
  if (!album) return res.status(404).json({ error: 'Album not found' });
  const { url, caption } = req.body;
  const photo = { id: album.photos.length + 1, url, caption: caption || '' };
  album.photos.push(photo);
  res.status(201).json(album);
});

app.delete('/albums/:id/photos/:photoId', (req, res) => {
  const album = albums.find(a => a.id === parseInt(req.params.id));
  if (!album) return res.status(404).json({ error: 'Album not found' });
  const index = album.photos.findIndex(p => p.id === parseInt(req.params.photoId));
  if (index === -1) return res.status(404).json({ error: 'Photo not found' });
  album.photos.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Photo album on http://localhost:3000'));
