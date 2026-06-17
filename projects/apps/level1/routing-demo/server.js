// Routing Demo — Static, dynamic, regex, nested routers, route parameters.
const express = require('express');
const app = express();
app.use(express.json());

// === Static routes (most specific first) ===
app.get('/', (req, res) => res.json({ message: 'Routing demo' }));
app.get('/about', (req, res) => res.json({ page: 'about' }));

// === Dynamic route parameters ===
app.get('/users/:id', (req, res) => res.json({ user: { id: req.params.id } }));
app.get('/users/:id/posts/:postId', (req, res) => res.json({ user: req.params.id, post: req.params.postId }));

// === Optional parameters ===
app.get('/products/:category/:productId?', (req, res) => res.json({ category: req.params.category, productId: req.params.productId || 'all' }));

// === Regex routes ===
app.get(/.*fly$/, (req, res) => res.json({ match: 'ends with fly', path: req.path }));
app.get(/^\/api\/v(\d+)\/.*/, (req, res) => res.json({ apiVersion: req.params[0] }));

// === Query strings ===
app.get('/search', (req, res) => res.json({ q: req.query.q, page: req.query.page || 1, limit: req.query.limit || 20, filters: req.query.filter ? [].concat(req.query.filter) : [] }));

// === Wildcard (404) ===
app.use((req, res) => res.status(404).json({ error: 'route_not_found', method: req.method, path: req.path }));

// === Nested routers (sub-applications) ===
const adminRouter = express.Router();
adminRouter.use((req, res, next) => { req.isAdmin = true; next(); });
adminRouter.get('/users', (req, res) => res.json({ users: [], isAdmin: req.isAdmin }));
adminRouter.get('/stats', (req, res) => res.json({ stats: { users: 100, posts: 200 } }));
adminRouter.post('/users', (req, res) => res.status(201).json({ id: 'u_' + Math.random().toString(36).slice(2, 8) }));
app.use('/admin', adminRouter);

const apiV1 = express.Router();
apiV1.get('/items', (req, res) => res.json({ items: [], version: 1 }));
app.use('/api/v1', apiV1);

const apiV2 = express.Router();
apiV2.get('/items', (req, res) => res.json({ items: [], data: [], version: 2, note: 'different shape' }));
app.use('/api/v2', apiV2);

app.listen(3000, () => console.log('Routing demo :3000'));
module.exports = app;
