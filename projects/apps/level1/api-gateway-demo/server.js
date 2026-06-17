// API Gateway Demo — Single entry point that routes to multiple backend services.
const express = require('express');
const http = require('http');
const app = express();
app.use(express.json());

// === Backend services (in real life, separate servers) ===
const services = {
  users: { port: 3001, prefix: '/api/users' },
  orders: { port: 3002, prefix: '/api/orders' },
  products: { port: 3003, prefix: '/api/products' },
};

// === Simple proxy function ===
function proxyTo(port, path) {
  return (req, res) => {
    const options = {
      hostname: 'localhost', port, path, method: req.method,
      headers: { ...req.headers, 'X-Forwarded-For': req.ip, 'X-Gateway': 'true' },
    };
    const proxyReq = http.request(options, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });
    proxyReq.on('error', (e) => res.status(502).json({ error: 'upstream_error', upstream: `localhost:${port}`, detail: e.message }));
    req.pipe(proxyReq);
  };
}

// === Gateway-level middleware: auth, rate limit, logging, headers ===
app.use((req, res, next) => {
  res.set('X-Gateway', 'demo');
  res.set('X-Powered-By', 'api-gateway/1.0');
  console.log(`[gateway] ${req.method} ${req.path}`);
  next();
});

// === Routes ===
app.get('/health', (req, res) => res.json({ gateway: 'ok', services: Object.keys(services) }));
app.get('/', (req, res) => res.json({ message: 'API Gateway', services }));

// In a real gateway, you'd proxy to actual backends. For demo, we just rewrite and return placeholder.
app.use('/api/users', (req, res) => res.json({ routed: 'users', upstream: services.users, path: req.path, method: req.method }));
app.use('/api/orders', (req, res) => res.json({ routed: 'orders', upstream: services.orders, path: req.path, method: req.method }));
app.use('/api/products', (req, res) => res.json({ routed: 'products', upstream: services.products, path: req.path, method: req.method }));

// === Aggregate endpoint: fan out to multiple backends, combine results ===
app.get('/api/dashboard', async (req, res) => {
  // Simulate calling multiple backends
  const fetchFake = (name) => Promise.resolve({ service: name, count: Math.floor(Math.random() * 100) });
  const [users, orders, products] = await Promise.all([fetchFake('users'), fetchFake('orders'), fetchFake('products')]);
  res.json({ dashboard: { users, orders, products }, generatedAt: new Date().toISOString() });
});

app.listen(3000, () => console.log('API Gateway demo :3000 — see also projects/llm_gateway for production version'));
module.exports = app;
