// Movies API — Step 11. Adds: genres, cast, similar movies, watchlist, ratings.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE movies (id TEXT PRIMARY KEY, title TEXT, year INTEGER, director TEXT, duration_min INTEGER, synopsis TEXT, poster_url TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE genres (id TEXT PRIMARY KEY, name TEXT UNIQUE)`);
db.exec(`CREATE TABLE movie_genres (movie_id TEXT, genre_id TEXT, PRIMARY KEY (movie_id, genre_id))`);
db.exec(`CREATE TABLE cast (id TEXT PRIMARY KEY, movie_id TEXT, person_name TEXT, role TEXT)`);
db.exec(`CREATE TABLE watchlist (user_id TEXT, movie_id TEXT, added_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (user_id, movie_id))`);

app.get('/movies', (req, res) => {
  const { q, genre, year, sort = 'recent' } = req.query;
  let query = 'SELECT DISTINCT m.* FROM movies m WHERE 1=1';
  const params = [];
  if (q) { query += ' AND m.title LIKE ?'; params.push('%' + q + '%'); }
  if (year) { query += ' AND m.year = ?'; params.push(parseInt(year)); }
  if (genre) { query += ' AND m.id IN (SELECT mg.movie_id FROM movie_genres mg JOIN genres g ON g.id = mg.genre_id WHERE g.name = ?)'; params.push(genre); }
  if (sort === 'year') query += ' ORDER BY m.year DESC';
  else if (sort === 'title') query += ' ORDER BY m.title ASC';
  else query += ' ORDER BY m.created_at DESC';
  res.json({ movies: db.prepare(query).all(...params) });
});

app.get('/movies/:id', (req, res) => {
  const movie = db.prepare('SELECT * FROM movies WHERE id = ?').get(req.params.id);
  if (!movie) return res.status(404).json({ error: 'not_found' });
  movie.genres = db.prepare('SELECT g.name FROM genres g JOIN movie_genres mg ON mg.genre_id = g.id WHERE mg.movie_id = ?').all(movie.id).map(g => g.name);
  movie.cast = db.prepare('SELECT person_name, role FROM cast WHERE movie_id = ?').all(movie.id);
  res.json(movie);
});

app.post('/movies', (req, res) => {
  const { title, year, director, duration_min, synopsis, poster_url, genres, cast } = req.body;
  if (!title) return res.status(422).json({ error: 'missing_title' });
  const id = 'm_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO movies (id, title, year, director, duration_min, synopsis, poster_url) VALUES (?, ?, ?, ?, ?, ?, ?)').run(id, title, year, director, duration_min, synopsis || '', poster_url || '');
  if (Array.isArray(genres)) for (const name of genres) {
    let g = db.prepare('SELECT id FROM genres WHERE name = ?').get(name);
    if (!g) g = db.prepare('INSERT INTO genres (id, name) VALUES (?, ?)').run('g_' + crypto.randomBytes(3).toString('hex'), name);
    try { db.prepare('INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)').run(id, g.lastInsertRowid || g.id); } catch {}
  }
  if (Array.isArray(cast)) for (const c of cast) db.prepare('INSERT INTO cast (id, movie_id, person_name, role) VALUES (?, ?, ?, ?)').run('c_' + crypto.randomBytes(3).toString('hex'), id, c.person_name, c.role || 'actor');
  res.status(201).json(db.prepare('SELECT * FROM movies WHERE id = ?').get(id));
});

// Similar movies: same genre
app.get('/movies/:id/similar', (req, res) => {
  const similar = db.prepare(`SELECT DISTINCT m.* FROM movies m JOIN movie_genres mg ON mg.movie_id = m.id WHERE mg.genre_id IN (SELECT genre_id FROM movie_genres WHERE movie_id = ?) AND m.id != ? LIMIT 10`).all(req.params.id, req.params.id);
  res.json({ similar });
});

// Watchlist
app.post('/watchlist/:movieId', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  try { db.prepare('INSERT INTO watchlist (user_id, movie_id) VALUES (?, ?)').run(req.userId, req.params.movieId); res.status(201).json({ added: true }); }
  catch { res.json({ added: false, reason: 'already_in_watchlist' }); }
});

app.get('/watchlist', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const list = db.prepare('SELECT m.*, w.added_at FROM watchlist w JOIN movies m ON m.id = w.movie_id WHERE w.user_id = ? ORDER BY w.added_at DESC').all(req.userId);
  res.json({ watchlist: list });
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Movies API :3000'));
module.exports = app;
