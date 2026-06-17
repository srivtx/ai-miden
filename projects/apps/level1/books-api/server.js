// Books API — Step 10. Adds: ISBN lookup, authors (many-to-many), ratings, reviews.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE authors (id TEXT PRIMARY KEY, name TEXT UNIQUE, bio TEXT)`);
db.exec(`CREATE TABLE books (id TEXT PRIMARY KEY, isbn TEXT UNIQUE, title TEXT, description TEXT, published_year INTEGER, page_count INTEGER, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE book_authors (book_id TEXT, author_id TEXT, PRIMARY KEY (book_id, author_id))`);
db.exec(`CREATE TABLE reviews (id TEXT PRIMARY KEY, book_id TEXT, user_id TEXT, rating INTEGER CHECK (rating BETWEEN 1 AND 5), body TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE INDEX idx_reviews_book ON reviews(book_id)`);

app.get('/books', (req, res) => {
  const { q, author, year, sort = 'recent', limit = 20 } = req.query;
  let query = 'SELECT b.*, AVG(r.rating) as avg_rating, COUNT(r.id) as review_count FROM books b LEFT JOIN reviews r ON r.book_id = b.id WHERE 1=1';
  const params = [];
  if (q) { query += ' AND (b.title LIKE ? OR b.description LIKE ?)'; params.push('%' + q + '%', '%' + q + '%'); }
  if (year) { query += ' AND b.published_year = ?'; params.push(parseInt(year)); }
  if (author) { query += ' AND b.id IN (SELECT ba.book_id FROM book_authors ba JOIN authors a ON a.id = ba.author_id WHERE a.name LIKE ?)'; params.push('%' + author + '%'); }
  query += ' GROUP BY b.id';
  if (sort === 'rating') query += ' ORDER BY avg_rating DESC, b.created_at DESC';
  else if (sort === 'title') query += ' ORDER BY b.title ASC';
  else query += ' ORDER BY b.created_at DESC';
  query += ' LIMIT ?'; params.push(parseInt(limit));
  res.json({ books: db.prepare(query).all(...params).map(b => ({ ...b, avg_rating: b.avg_rating ? Math.round(b.avg_rating * 10) / 10 : null })) });
});

app.get('/books/:id', (req, res) => {
  const book = db.prepare('SELECT * FROM books WHERE id = ? OR isbn = ?').get(req.params.id, req.params.id);
  if (!book) return res.status(404).json({ error: 'not_found' });
  book.authors = db.prepare('SELECT a.* FROM authors a JOIN book_authors ba ON ba.author_id = a.id WHERE ba.book_id = ?').all(book.id);
  book.reviews = db.prepare('SELECT id, user_id, rating, body, created_at FROM reviews WHERE book_id = ? ORDER BY created_at DESC').all(book.id);
  book.avg_rating = book.reviews.length ? book.reviews.reduce((s, r) => s + r.rating, 0) / book.reviews.length : null;
  res.json(book);
});

app.post('/books', (req, res) => {
  const { isbn, title, description, published_year, page_count, authors } = req.body;
  if (!isbn || !title) return res.status(422).json({ error: 'missing_fields' });
  const id = 'b_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO books (id, isbn, title, description, published_year, page_count) VALUES (?, ?, ?, ?, ?, ?)').run(id, isbn, title, description || '', published_year, page_count);
  if (Array.isArray(authors)) for (const name of authors) {
    let author = db.prepare('SELECT id FROM authors WHERE name = ?').get(name);
    if (!author) author = db.prepare('INSERT INTO authors (id, name) VALUES (?, ?)').run('a_' + crypto.randomBytes(3).toString('hex'), name);
    try { db.prepare('INSERT INTO book_authors (book_id, author_id) VALUES (?, ?)').run(id, author.lastInsertRowid || author.id); } catch {}
  }
  res.status(201).json(db.prepare('SELECT * FROM books WHERE id = ?').get(id));
});

app.post('/books/:id/reviews', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { rating, body } = req.body;
  if (!rating || rating < 1 || rating > 5) return res.status(422).json({ error: 'invalid_rating' });
  const id = 'rv_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO reviews (id, book_id, user_id, rating, body) VALUES (?, ?, ?, ?, ?)').run(id, req.params.id, req.userId, rating, body || '');
  res.status(201).json(db.prepare('SELECT * FROM reviews WHERE id = ?').get(id));
});

app.get('/authors', (req, res) => res.json({ authors: db.prepare('SELECT a.*, COUNT(ba.book_id) as book_count FROM authors a LEFT JOIN book_authors ba ON ba.author_id = a.id GROUP BY a.id ORDER BY book_count DESC').all() }));

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Books API :3000'));
module.exports = app;
