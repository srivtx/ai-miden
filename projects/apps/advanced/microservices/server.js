// Microservices Demo — Two services (users + orders) with an API Gateway.
// Run each in a separate terminal:
//   node server.js users
//   node server.js orders
//   node server.js gateway

const express = require('express');
const app = express();
app.use(express.json());

const SERVICE = process.argv[2]; // 'users', 'orders', or 'gateway'
const PORTS = { users: 3001, orders: 3002, gateway: 3000 };

// ---- Data stores (each service has its OWN data) ----
const userStore = [{ id: 1, name: 'Zen', email: 'zen@test.com' }];
const orderStore = [];

// ---- USERS SERVICE ----
if (SERVICE === 'users') {
  app.get('/users', (req, res) => res.json(userStore));
  app.get('/users/:id', (req, res) => {
    const user = userStore.find(u => u.id === parseInt(req.params.id));
    user ? res.json(user) : res.status(404).json({ error: 'Not found' });
  });
  app.get('/health', (req, res) => res.json({ service: 'users', status: 'ok' }));
  app.listen(PORTS.users, () => console.log(`Users service :${PORTS.users}`));
}

// ---- ORDERS SERVICE ----
if (SERVICE === 'orders') {
  app.post('/orders', (req, res) => {
    const order = { id: orderStore.length + 1, userId: req.body.userId, product: req.body.product, status: 'created' };
    orderStore.push(order);
    res.status(201).json(order);
  });
  app.get('/orders', (req, res) => res.json(orderStore));
  app.get('/orders/:id', (req, res) => {
    const order = orderStore.find(o => o.id === parseInt(req.params.id));
    order ? res.json(order) : res.status(404).json({ error: 'Not found' });
  });
  app.get('/health', (req, res) => res.json({ service: 'orders', status: 'ok' }));
  app.listen(PORTS.orders, () => console.log(`Orders service :${PORTS.orders}`));
}

// ---- API GATEWAY (routes to services) ----
if (SERVICE === 'gateway') {
  const http = require('http');

  function proxy(servicePort) {
    return (req, res) => {
      const opts = {
        hostname: 'localhost', port: servicePort, path: req.url,
        method: req.method, headers: { ...req.headers, 'content-type': 'application/json' },
      };

      const proxyReq = http.request(opts, (proxyRes) => {
        let data = '';
        proxyRes.on('data', c => data += c);
        proxyRes.on('end', () => {
          res.status(proxyRes.statusCode);
          try { res.json(JSON.parse(data)); } catch { res.send(data); }
        });
      });
      proxyReq.on('error', () => res.status(502).json({ error: 'Service unavailable' }));
      if (req.body && Object.keys(req.body).length) proxyReq.write(JSON.stringify(req.body));
      proxyReq.end();
    };
  }

  app.use('/api/users', proxy(PORTS.users));
  app.use('/api/orders', proxy(PORTS.orders));

  // Service health dashboard
  async function checkHealth(port) {
    try {
      return await new Promise((resolve) => {
        http.get(`http://localhost:${port}/health`, (res) => {
          let data = ''; res.on('data', c => data += c);
          res.on('end', () => resolve(JSON.parse(data)));
        }).on('error', () => resolve({ status: 'down' }));
      });
    } catch { return { status: 'down' }; }
  }

  app.get('/health', async (req, res) => {
    const [users, orders] = await Promise.all([checkHealth(PORTS.users), checkHealth(PORTS.orders)]);
    res.json({ gateway: 'ok', services: { users, orders } });
  });

  app.listen(PORTS.gateway, () => console.log(`Gateway :${PORTS.gateway}`));
}
