// 09-shipping: Shipping methods, rates by zone, tracking integration.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE shipping_zones (id INTEGER PRIMARY KEY, name TEXT, countries TEXT);
  CREATE TABLE shipping_methods (id INTEGER PRIMARY KEY, name TEXT, zone_id INTEGER, base_cents INTEGER, per_kg_cents INTEGER DEFAULT 0, estimated_days INTEGER);
  CREATE TABLE shipments (id TEXT PRIMARY KEY, order_id TEXT, method_id INTEGER, tracking TEXT, status TEXT DEFAULT 'pending', cost_cents INTEGER, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')));
`);

// Seed
db.prepare('INSERT INTO shipping_zones VALUES (1, ?, ?)').run('US Domestic', 'US');
db.prepare('INSERT INTO shipping_zones VALUES (2, ?, ?)').run('International', 'XX');
db.prepare('INSERT INTO shipping_methods VALUES (1, ?, 1, 599, 100, 3)').run('Standard');
db.prepare('INSERT INTO shipping_methods VALUES (2, ?, 1, 1499, 200, 1)').run('Express');
db.prepare('INSERT INTO shipping_methods VALUES (3, ?, 2, 2499, 500, 7)').run('International Standard');

// Get available methods
app.get('/shipping/methods', (req, res) => {
  const methods = db.prepare(`
    SELECT m.*, z.name as zone, z.countries
    FROM shipping_methods m JOIN shipping_zones z ON z.id = m.zone_id
  `).all();
  res.json({ methods });
});

// Calculate shipping cost
app.post('/shipping/calculate', (req, res) => {
  const { method_id, weight_kg = 1, country = 'US' } = req.body;
  if (!method_id) return res.status(422).json({ error: 'method_id required' });
  const method = db.prepare(`
    SELECT m.*, z.countries FROM shipping_methods m JOIN shipping_zones z ON z.id = m.zone_id
    WHERE m.id = ?
  `).get(method_id);
  if (!method) return res.status(404).json({ error: 'method not found' });
  if (!method.countries.split(',').includes(country) && !method.countries.split(',').includes('XX')) {
    return res.status(422).json({ error: 'method not available in your country' });
  }
  const cost = method.base_cents + method.per_kg_cents * weight_kg;
  res.json({
    method: method.name,
    zone: method.name,
    cost_cents: cost,
    cost: (cost / 100).toFixed(2),
    estimated_days: method.estimated_days,
  });
});

// Create a shipment for an order
app.post('/shipments', (req, res) => {
  const { order_id, method_id, weight_kg = 1 } = req.body;
  if (!order_id || !method_id) return res.status(422).json({ error: 'order_id and method_id required' });
  const method = db.prepare('SELECT * FROM shipping_methods WHERE id = ?').get(method_id);
  if (!method) return res.status(404).json({ error: 'method not found' });
  const cost = method.base_cents + method.per_kg_cents * weight_kg;
  const tracking = 'TRK' + Date.now() + Math.random().toString(36).slice(2, 8).toUpperCase();
  const id = 'shp_' + Date.now();
  db.prepare('INSERT INTO shipments VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(id, order_id, method_id, tracking, 'pending', cost, new Date().toISOString(), new Date().toISOString());
  res.status(201).json({ id, tracking, cost_cents: cost, estimated_days: method.estimated_days });
});

// Track a shipment (simulated)
app.get('/shipments/:tracking', (req, res) => {
  const shipment = db.prepare('SELECT * FROM shipments WHERE tracking = ?').get(req.params.tracking);
  if (!shipment) return res.status(404).json({ error: 'not found' });
  res.json({
    tracking: shipment.tracking,
    status: shipment.status,
    created_at: shipment.created_at,
    events: [
      { ts: shipment.created_at, status: 'pending', location: 'Origin warehouse' },
    ],
  });
});

app.listen(3000, () => console.log('09-shipping on :3000'));
