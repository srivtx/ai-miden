// E-Commerce — Products, cart, orders, inventory, multi-tenant (simplified).
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const products = []; const carts = new Map(); const orders = []; let orderId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

// AUTH
app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) return res.status(400).json({ error: 'name, email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) };
  users.push(user); carts.set(user.id, []);
  res.status(201).json({ user: { id: user.id, name, email }, token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '1h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '1h' }) });
});

// PRODUCTS (anyone can view)
app.get('/products', (req, res) => {
  let result = [...products].filter(p => p.stock > 0);
  if (req.query.category) result = result.filter(p => p.category === req.query.category);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(p => p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q)); }
  if (req.query.sort === 'price') result.sort((a, b) => a.price - b.price);
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = Math.min(50, parseInt(req.query.limit) || 20);
  const total = result.length; result = result.slice((page - 1) * limit, page * limit);
  res.json({ total, page, data: result });
});
app.get('/products/:id', (req, res) => {
  const p = products.find(pr => pr.id === parseInt(req.params.id));
  p ? res.json(p) : res.status(404).json({ error: 'Not found' });
});

// SEED products (admin setup)
app.post('/admin/products', (req, res) => {
  const { name, description, price, category, stock } = req.body;
  const p = { id: products.length + 1, name, description: description || '', price, category: category || 'general', stock: stock || 0 };
  products.push(p);
  res.status(201).json(p);
});

// CART
app.get('/cart', auth, (req, res) => {
  const cart = carts.get(req.user.id) || [];
  const items = cart.map(ci => { const p = products.find(pr => pr.id === ci.productId); return p ? { ...ci, name: p.name, price: p.price, subtotal: p.price * ci.quantity } : ci; });
  const total = items.reduce((sum, i) => sum + (i.subtotal || 0), 0);
  res.json({ items, total, count: items.length });
});

app.post('/cart', auth, (req, res) => {
  const { productId, quantity = 1 } = req.body;
  const product = products.find(p => p.id === parseInt(productId));
  if (!product) return res.status(404).json({ error: 'Product not found' });
  if (product.stock < quantity) return res.status(400).json({ error: 'Insufficient stock' });
  const cart = carts.get(req.user.id) || [];
  const existing = cart.find(i => i.productId === parseInt(productId));
  if (existing) existing.quantity += quantity;
  else cart.push({ productId: parseInt(productId), quantity });
  carts.set(req.user.id, cart);
  res.json({ added: product.name, quantity });
});

app.delete('/cart/:productId', auth, (req, res) => {
  const cart = carts.get(req.user.id) || [];
  const idx = cart.findIndex(i => i.productId === parseInt(req.params.productId));
  if (idx === -1) return res.status(404).json({ error: 'Not in cart' });
  cart.splice(idx, 1);
  res.json({ removed: true });
});

// CHECKOUT (place order)
app.post('/orders', auth, (req, res) => {
  const cart = carts.get(req.user.id) || [];
  if (!cart.length) return res.status(400).json({ error: 'Cart is empty' });
  // Verify stock and deduct
  for (const ci of cart) {
    const p = products.find(pr => pr.id === ci.productId);
    if (!p || p.stock < ci.quantity) return res.status(400).json({ error: `Insufficient stock for ${p?.name || ci.productId}` });
  }
  cart.forEach(ci => { const p = products.find(pr => pr.id === ci.productId); p.stock -= ci.quantity; });
  const orderItems = cart.map(ci => { const p = products.find(pr => pr.id === ci.productId); return { productId: p.id, name: p.name, price: p.price, quantity: ci.quantity, subtotal: p.price * ci.quantity }; });
  const total = orderItems.reduce((s, i) => s + i.subtotal, 0);
  const order = { id: orderId++, userId: req.user.id, items: orderItems, total, status: 'confirmed', createdAt: new Date().toISOString() };
  orders.push(order);
  carts.set(req.user.id, []);
  res.status(201).json(order);
});

// ORDER HISTORY
app.get('/orders', auth, (req, res) => {
  res.json(orders.filter(o => o.userId === req.user.id));
});

app.listen(3000, () => console.log('E-Commerce :3000'));
module.exports = app;
