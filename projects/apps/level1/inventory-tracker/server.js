// Inventory Tracker — Products, stock, low-stock alerts, categories, transactions.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const items = []; const transactions = []; let itemId = 1, txId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// ITEMS
app.post('/items', auth, (req, res) => {
  const { name, sku, category, quantity, unit, lowStockThreshold, price } = req.body;
  if (!name) return res.status(400).json({ error: 'Name required' });
  if (items.find(i => i.sku === sku)) return res.status(409).json({ error: 'SKU already exists' });
  const item = { id: itemId++, name, sku: sku || `SKU-${itemId}`, category: category || 'General', quantity: quantity || 0, unit: unit || 'pcs', lowStockThreshold: lowStockThreshold || 10, price: price || 0, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  items.push(item);
  res.status(201).json(item);
});

app.get('/items', auth, (req, res) => {
  let result = [...items];
  if (req.query.category) result = result.filter(i => i.category === req.query.category);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(i => i.name.toLowerCase().includes(q) || i.sku.toLowerCase().includes(q)); }
  if (req.query.lowStock === 'true') result = result.filter(i => i.quantity <= i.lowStockThreshold);
  if (req.query.outOfStock === 'true') result = result.filter(i => i.quantity <= 0);
  const sortField = ['name', 'quantity', 'category', 'createdAt'].includes(req.query.sort) ? req.query.sort : 'name';
  result.sort((a, b) => (a[sortField] > b[sortField] ? 1 : -1) * (req.query.order === 'desc' ? -1 : 1));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 50;
  const total = result.length;
  res.json({ total, page, pages: Math.ceil(total / limit), lowStockCount: items.filter(i => i.quantity <= i.lowStockThreshold).length, outOfStockCount: items.filter(i => i.quantity <= 0).length, data: result.slice((page - 1) * limit, page * limit) });
});

// TRANSACTIONS (stock in/out)
app.post('/items/:id/transactions', auth, (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id));
  if (!item) return res.status(404).json({ error: 'Not found' });
  const { type, quantity, note } = req.body;
  if (!type || !['in', 'out'].includes(type)) return res.status(400).json({ error: 'Type must be "in" or "out"' });
  if (!quantity || quantity <= 0) return res.status(400).json({ error: 'Positive quantity required' });
  if (type === 'out' && item.quantity < quantity) return res.status(400).json({ error: `Insufficient stock. Available: ${item.quantity}` });
  item.quantity += type === 'in' ? quantity : -quantity;
  item.updatedAt = new Date().toISOString();
  const tx = { id: txId++, itemId: item.id, type, quantity, note: note || '', previousQuantity: type === 'in' ? item.quantity - quantity : item.quantity + quantity, newQuantity: item.quantity, userId: req.user.id, createdAt: new Date().toISOString() };
  transactions.push(tx);
  res.status(201).json({ transaction: tx, item });
});

app.get('/items/:id/transactions', auth, (req, res) => {
  const txs = transactions.filter(t => t.itemId === parseInt(req.params.id)).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 20;
  res.json({ total: txs.length, page, data: txs.slice((page - 1) * limit, page * limit) });
});

// SUMMARY
app.get('/summary', auth, (req, res) => {
  const totalItems = items.length;
  const totalValue = items.reduce((s, i) => s + i.quantity * i.price, 0);
  const lowStock = items.filter(i => i.quantity <= i.lowStockThreshold && i.quantity > 0).length;
  const outOfStock = items.filter(i => i.quantity <= 0).length;
  const byCategory = {}; items.forEach(i => { if (!byCategory[i.category]) byCategory[i.category] = { count: 0, value: 0 }; byCategory[i.category].count++; byCategory[i.category].value += i.quantity * i.price; });
  const recentTx = transactions.slice(-10).reverse();
  res.json({ totalItems, totalValue, lowStock, outOfStock, byCategory, recentTransactions: recentTx.map(t => ({ ...t, itemName: items.find(i => i.id === t.itemId)?.name })) });
});

app.listen(3000, () => console.log('Inventory :3000'));
module.exports = app;
