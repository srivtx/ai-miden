// gRPC-style Demo — Service definition, request handlers, simple RPC protocol over HTTP/2-like framing.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// === Service registry (proto-style definitions) ===
const services = {
  UserService: {
    GetUser: { input: '{id: number}', output: '{id, name, email}' },
    CreateUser: { input: '{name, email}', output: '{id, name, email}' },
    DeleteUser: { input: '{id}', output: '{success}' },
  },
  OrderService: {
    CreateOrder: { input: '{userId, items: [{productId, quantity}]}', output: '{id, total, status}' },
    GetOrder: { input: '{id}', output: '{id, userId, items, total, status}' },
    ListOrders: { input: '{userId, limit?}', output: '{orders: [...]}' },
  },
};

// === In-memory data ===
const users = new Map();
const orders = new Map();
let nextUserId = 1, nextOrderId = 1;

// === Service implementations ===
const implementations = {
  UserService: {
    GetUser: ({ id }) => users.get(id) || null,
    CreateUser: ({ name, email }) => {
      const u = { id: nextUserId++, name, email };
      users.set(u.id, u);
      return u;
    },
    DeleteUser: ({ id }) => {
      const ok = users.delete(id);
      return { success: ok };
    },
  },
  OrderService: {
    CreateOrder: ({ userId, items }) => {
      const order = { id: nextOrderId++, userId, items, total: items.reduce((s, i) => s + (i.price || 10) * i.quantity, 0), status: 'pending' };
      orders.set(order.id, order);
      return order;
    },
    GetOrder: ({ id }) => orders.get(id) || null,
    ListOrders: ({ userId, limit = 10 }) => {
      const list = Array.from(orders.values()).filter(o => o.userId === userId);
      return { orders: list.slice(0, limit) };
    },
  },
};

// === RPC endpoint (POST /rpc/:service/:method) ===
app.post('/rpc/:service/:method', (req, res) => {
  const { service, method } = req.params;
  const start = Date.now();
  if (!services[service]) return res.status(404).json({ error: 'service_not_found', service });
  if (!services[service][method]) return res.status(404).json({ error: 'method_not_found', method });
  const impl = implementations[service]?.[method];
  if (!impl) return res.status(501).json({ error: 'method_not_implemented' });
  try {
    const result = impl(req.body || {});
    res.json({ ok: true, result, durationMs: Date.now() - start });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message, durationMs: Date.now() - start });
  }
});

// === Service discovery ===
app.get('/rpc', (req, res) => res.json({ services }));
app.get('/rpc/:service', (req, res) => {
  const s = services[req.params.service];
  s ? res.json(s) : res.status(404).json({ error: 'service_not_found' });
});

// === Health check per service ===
app.get('/rpc/:service/health', (req, res) => {
  const exists = !!services[req.params.service];
  res.json({ service: req.params.service, healthy: exists, ts: Date.now() });
});

app.listen(3000, () => console.log('RPC demo :3000 — POST /rpc/:service/:method, GET /rpc for service list'));
module.exports = app;
