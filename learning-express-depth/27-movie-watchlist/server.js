// 27 — Movie Watchlist
// Same CRUD + a "watched" boolean and a rating.
const express = require('express');
const app = express();
app.use(express.json());

const movies = [];

app.get('/movies', (req, res) => {
  res.json({ count: movies.length, movies });
});

app.post('/movies', (req, res) => {
  const { title, year } = req.body;
  const movie = { id: movies.length + 1, title, year, watched: false, rating: 0 };
  movies.push(movie);
  res.status(201).json(movie);
});

app.patch('/movies/:id', (req, res) => {
  const movie = movies.find(m => m.id === parseInt(req.params.id));
  if (!movie) return res.status(404).json({ error: 'Movie not found' });
  if (req.body.watched !== undefined) movie.watched = req.body.watched;
  if (req.body.rating !== undefined) movie.rating = req.body.rating;
  res.json(movie);
});

app.delete('/movies/:id', (req, res) => {
  const index = movies.findIndex(m => m.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Movie not found' });
  movies.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Movie watchlist on http://localhost:3000'));
