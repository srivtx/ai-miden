// Ticket Booking API — Step 17. Adds: events, venues, seat selection, booking, payment.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE venues (id TEXT PRIMARY KEY, name TEXT, address TEXT, capacity INTEGER)`);
db.exec(`CREATE TABLE events (id TEXT PRIMARY KEY, venue_id TEXT, name TEXT, description TEXT, start_at TEXT, end_at TEXT, base_price_cents INTEGER, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE seats (id TEXT PRIMARY KEY, venue_id TEXT, row TEXT, number INTEGER, section TEXT)`);
db.exec(`CREATE TABLE bookings (id TEXT PRIMARY KEY, event_id TEXT, user_id TEXT, seat_id TEXT, status TEXT DEFAULT 'pending', payment_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE UNIQUE INDEX idx_seat_unique ON seats(venue_id, row, number)`);
db.exec(`CREATE UNIQUE INDEX idx_booking_seat ON bookings(event_id, seat_id)`);

app.post('/venues', (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'v_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO venues (id, name, address, capacity) VALUES (?, ?, ?, ?)').run(id, req.body.name, req.body.address || '', req.body.capacity || 0);
  // Auto-generate seats in a grid
  if (req.body.generate_seats) {
    const { rows = 5, seats_per_row = 10 } = req.body.generate_seats;
    for (let r = 0; r < rows; r++) for (let s = 1; s <= seats_per_row; s++) {
      db.prepare('INSERT INTO seats (id, venue_id, row, number, section) VALUES (?, ?, ?, ?, ?)').run('seat_' + crypto.randomBytes(3).toString('hex'), id, String.fromCharCode(65 + r), s, r < 2 ? 'premium' : 'general');
    }
  }
  res.status(201).json({ id });
});

app.post('/events', (req, res) => {
  const { venue_id, name, description, start_at, end_at, base_price_cents } = req.body;
  if (!venue_id || !name || !start_at) return res.status(422).json({ error: 'missing_fields' });
  const id = 'e_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO events (id, venue_id, name, description, start_at, end_at, base_price_cents) VALUES (?, ?, ?, ?, ?, ?, ?)').run(id, venue_id, name, description || '', start_at, end_at, base_price_cents);
  res.status(201).json({ id });
});

app.get('/events', (req, res) => {
  const events = db.prepare('SELECT e.*, v.name as venue_name FROM events e JOIN venues v ON v.id = e.venue_id ORDER BY e.start_at ASC').all();
  for (const e of events) e.available_seats = db.prepare('SELECT COUNT(*) as c FROM seats s WHERE s.venue_id = e.venue_id AND s.id NOT IN (SELECT seat_id FROM bookings WHERE event_id = e.id AND status != "cancelled")').get(e).c;
  res.json({ events });
});

app.get('/events/:id', (req, res) => {
  const event = db.prepare('SELECT e.*, v.name as venue_name FROM events e JOIN venues v ON v.id = e.venue_id WHERE e.id = ?').get(req.params.id);
  if (!event) return res.status(404).json({ error: 'not_found' });
  // Show all seats with availability
  const seats = db.prepare('SELECT s.id, s.row, s.number, s.section, EXISTS(SELECT 1 FROM bookings b WHERE b.event_id = ? AND b.seat_id = s.id AND b.status != "cancelled") as taken FROM seats s WHERE s.venue_id = ? ORDER BY s.row, s.number').all(event.id, event.venue_id);
  res.json({ event, seats });
});

// === Reserve a seat (with payment simulation) ===
app.post('/events/:id/book', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  if (!req.body.seat_id) return res.status(422).json({ error: 'missing_seat' });
  const event = db.prepare('SELECT * FROM events WHERE id = ?').get(req.params.id);
  if (!event) return res.status(404).json({ error: 'event_not_found' });
  // Check seat not taken
  const taken = db.prepare('SELECT id FROM bookings WHERE event_id = ? AND seat_id = ? AND status != "cancelled"').get(event.id, req.body.seat_id);
  if (taken) return res.status(409).json({ error: 'seat_taken' });
  // Simulate payment
  const paymentId = 'pay_' + crypto.randomBytes(4).toString('hex');
  const id = 'bk_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO bookings (id, event_id, user_id, seat_id, status, payment_id) VALUES (?, ?, ?, ?, ?, ?)').run(id, event.id, req.userId, req.body.seat_id, 'confirmed', paymentId);
  res.status(201).json({ booking_id: id, payment_id: paymentId, event_id: event.id, seat_id: req.body.seat_id, status: 'confirmed', amount_cents: event.base_price_cents });
});

app.post('/bookings/:id/cancel', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const booking = db.prepare('SELECT * FROM bookings WHERE id = ?').get(req.params.id);
  if (!booking) return res.status(404).json({ error: 'not_found' });
  if (booking.user_id !== req.userId) return res.status(403).json({ error: 'forbidden' });
  db.prepare('UPDATE bookings SET status = ? WHERE id = ?').run('cancelled', req.params.id);
  res.json({ cancelled: true });
});

app.get('/my-bookings', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const bookings = db.prepare('SELECT b.*, e.name as event_name, e.start_at, s.row, s.number FROM bookings b JOIN events e ON e.id = b.event_id JOIN seats s ON s.id = b.seat_id WHERE b.user_id = ? ORDER BY b.created_at DESC').all(req.userId);
  res.json({ bookings });
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Ticket booking API :3000 — X-User-Id header'));
module.exports = app;
