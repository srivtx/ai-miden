// 08-coupons: Discount codes. Apply at checkout. Track usage.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE coupons (code TEXT PRIMARY KEY, type TEXT CHECK(type IN ('percent', 'fixed')), value INTEGER, min_order_cents INTEGER DEFAULT 0, max_uses INTEGER, used_count INTEGER DEFAULT 0, expires_at TEXT, active INTEGER DEFAULT 1);
  CREATE TABLE coupon_redemptions (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, user_id TEXT, order_id TEXT, redeemed_at TEXT DEFAULT (datetime('now')));
`);

// Create a coupon
app.post('/coupons', (req, res) => {
  const { code, type, value, min_order_cents, max_uses, expires_at } = req.body;
  if (!code || !type || value === undefined) return res.status(422).json({ error: 'missing fields' });
  if (!['percent', 'fixed'].includes(type)) return res.status(422).json({ error: 'type must be percent or fixed' });
  try {
    db.prepare('INSERT INTO coupons VALUES (?, ?, ?, ?, ?, 0, ?, 1)').run(code.toUpperCase(), type, value, min_order_cents || 0, max_uses || null, expires_at || null);
    res.status(201).json({ code: code.toUpperCase(), type, value, min_order_cents: min_order_cents || 0, max_uses, expires_at });
  } catch { res.status(409).json({ error: 'code already exists' }); }
});

app.get('/coupons/:code', (req, res) => {
  const coupon = db.prepare('SELECT * FROM coupons WHERE code = ?').get(req.params.code.toUpperCase());
  if (!coupon) return res.status(404).json({ error: 'not found' });
  res.json(coupon);
});

// Apply coupon to a cart total
app.post('/coupons/apply', (req, res) => {
  const { code, subtotal_cents, user_id, order_id } = req.body;
  if (!code || subtotal_cents === undefined) return res.status(422).json({ error: 'code and subtotal_cents required' });

  const coupon = db.prepare('SELECT * FROM coupons WHERE code = ?').get(code.toUpperCase());
  if (!coupon) return res.status(404).json({ error: 'coupon not found' });
  if (!coupon.active) return res.status(410).json({ error: 'coupon inactive' });
  if (coupon.expires_at && new Date(coupon.expires_at) < new Date()) return res.status(410).json({ error: 'coupon expired' });
  if (coupon.max_uses && coupon.used_count >= coupon.max_uses) return res.status(410).json({ error: 'coupon exhausted' });
  if (coupon.min_order_cents && subtotal_cents < coupon.min_order_cents) {
    return res.status(422).json({ error: 'order below minimum', min: coupon.min_order_cents });
  }

  // Check: this user hasn't used this code before
  if (user_id) {
    const used = db.prepare('SELECT id FROM coupon_redemptions WHERE code = ? AND user_id = ?').get(coupon.code, user_id);
    if (used) return res.status(409).json({ error: 'you already used this coupon' });
  }

  // Calculate discount
  let discount;
  if (coupon.type === 'percent') {
    discount = Math.round(subtotal_cents * coupon.value / 100);
  } else {
    discount = Math.min(coupon.value, subtotal_cents);
  }

  res.json({
    code: coupon.code,
    type: coupon.type,
    discount_cents: discount,
    subtotal_cents,
    total_cents: subtotal_cents - discount,
  });
});

// Confirm redemption (after order is placed)
app.post('/coupons/:code/redeem', (req, res) => {
  const { user_id, order_id } = req.body;
  if (!user_id || !order_id) return res.status(422).json({ error: 'user_id and order_id required' });
  const coupon = db.prepare('SELECT * FROM coupons WHERE code = ?').get(req.params.code.toUpperCase());
  if (!coupon) return res.status(404).json({ error: 'coupon not found' });
  const used = db.prepare('SELECT id FROM coupon_redemptions WHERE code = ? AND user_id = ?').get(coupon.code, user_id);
  if (used) return res.status(409).json({ error: 'already redeemed' });
  db.prepare('INSERT INTO coupon_redemptions (code, user_id, order_id) VALUES (?, ?, ?)').run(coupon.code, user_id, order_id);
  db.prepare('UPDATE coupons SET used_count = used_count + 1 WHERE code = ?').run(coupon.code);
  res.json({ redeemed: true, code: coupon.code });
});

app.listen(3000, () => console.log('08-coupons on :3000'));
