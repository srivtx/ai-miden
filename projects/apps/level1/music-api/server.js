// Music API — Step 12. Adds: artists, albums, tracks, playlists, play counts, top charts.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE artists (id TEXT PRIMARY KEY, name TEXT UNIQUE, bio TEXT)`);
db.exec(`CREATE TABLE albums (id TEXT PRIMARY KEY, artist_id TEXT, title TEXT, release_year INTEGER, cover_url TEXT)`);
db.exec(`CREATE TABLE tracks (id TEXT PRIMARY KEY, album_id TEXT, title TEXT, duration_sec INTEGER, track_number INTEGER)`);
db.exec(`CREATE TABLE playlists (id TEXT PRIMARY KEY, user_id TEXT, name TEXT, description TEXT, is_public INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE playlist_tracks (playlist_id TEXT, track_id TEXT, position INTEGER, PRIMARY KEY (playlist_id, track_id))`);
db.exec(`CREATE TABLE plays (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, track_id TEXT, played_at TEXT DEFAULT (datetime('now')))`);

app.get('/artists', (req, res) => res.json({ artists: db.prepare('SELECT * FROM artists').all() }));
app.get('/artists/:id', (req, res) => {
  const artist = db.prepare('SELECT * FROM artists WHERE id = ?').get(req.params.id);
  if (!artist) return res.status(404).json({ error: 'not_found' });
  artist.albums = db.prepare('SELECT * FROM albums WHERE artist_id = ? ORDER BY release_year DESC').all(artist.id);
  res.json(artist);
});

app.post('/artists', (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'ar_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO artists (id, name, bio) VALUES (?, ?, ?)').run(id, req.body.name, req.body.bio || '');
  res.status(201).json({ id, name: req.body.name });
});

app.get('/albums', (req, res) => {
  const albums = db.prepare('SELECT a.*, ar.name as artist_name, COUNT(t.id) as track_count FROM albums a JOIN artists ar ON ar.id = a.artist_id LEFT JOIN tracks t ON t.album_id = a.id GROUP BY a.id').all();
  res.json({ albums });
});

app.get('/albums/:id', (req, res) => {
  const album = db.prepare('SELECT a.*, ar.name as artist_name FROM albums a JOIN artists ar ON ar.id = a.artist_id WHERE a.id = ?').get(req.params.id);
  if (!album) return res.status(404).json({ error: 'not_found' });
  album.tracks = db.prepare('SELECT * FROM tracks WHERE album_id = ? ORDER BY track_number').all(album.id);
  res.json(album);
});

app.post('/albums', (req, res) => {
  const { artist_id, title, release_year, cover_url } = req.body;
  if (!artist_id || !title) return res.status(422).json({ error: 'missing_fields' });
  const id = 'al_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO albums (id, artist_id, title, release_year, cover_url) VALUES (?, ?, ?, ?, ?)').run(id, artist_id, title, release_year, cover_url);
  res.status(201).json({ id });
});

app.post('/tracks', (req, res) => {
  const { album_id, title, duration_sec, track_number } = req.body;
  if (!album_id || !title) return res.status(422).json({ error: 'missing_fields' });
  const id = 'tr_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO tracks (id, album_id, title, duration_sec, track_number) VALUES (?, ?, ?, ?, ?)').run(id, album_id, title, duration_sec, track_number);
  res.status(201).json({ id });
});

app.post('/play/:trackId', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  db.prepare('INSERT INTO plays (user_id, track_id) VALUES (?, ?)').run(req.userId, req.params.trackId);
  res.json({ played: true });
});

app.get('/charts/top', (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  const top = db.prepare('SELECT t.id, t.title, ar.name as artist, a.title as album, COUNT(p.id) as play_count FROM tracks t JOIN plays p ON p.track_id = t.id JOIN albums a ON a.id = t.album_id JOIN artists ar ON ar.id = a.artist_id GROUP BY t.id ORDER BY play_count DESC LIMIT ?').all(limit);
  res.json({ top });
});

app.post('/playlists', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'pl_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO playlists (id, user_id, name, description, is_public) VALUES (?, ?, ?, ?, ?)').run(id, req.userId, req.body.name, req.body.description || '', req.body.is_public ? 1 : 0);
  res.status(201).json({ id });
});

app.post('/playlists/:id/tracks', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const playlist = db.prepare('SELECT * FROM playlists WHERE id = ?').get(req.params.id);
  if (!playlist || playlist.user_id !== req.userId) return res.status(404).json({ error: 'not_found' });
  const pos = db.prepare('SELECT COALESCE(MAX(position), 0) + 1 as p FROM playlist_tracks WHERE playlist_id = ?').get(req.params.id).p;
  try { db.prepare('INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES (?, ?, ?)').run(req.params.id, req.body.track_id, pos); res.status(201).json({ added: true, position: pos }); }
  catch { res.status(409).json({ error: 'already_in_playlist' }); }
});

app.get('/playlists/:id', (req, res) => {
  const playlist = db.prepare('SELECT * FROM playlists WHERE id = ?').get(req.params.id);
  if (!playlist) return res.status(404).json({ error: 'not_found' });
  playlist.tracks = db.prepare('SELECT t.*, pt.position FROM playlist_tracks pt JOIN tracks t ON t.id = pt.track_id WHERE pt.playlist_id = ? ORDER BY pt.position').all(playlist.id);
  res.json(playlist);
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Music API :3000'));
module.exports = app;
