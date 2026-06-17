// 08 — Products App
// Same CRUD pattern, but products have a price (number) and a category (string).
// We also add filtering: GET /products?category=electronics
const express = require('express');
const app = express();
app.use(express.json());

const products = [];

app.get('/products', (req, res) => {
  // req.query is an object of all ?key=value pairs in the URL
  const { category } = req.query;
  let result = products;
  if (category) {
    result = result.filter(p => p.category === category);
  }
  res.json({ count: result.length, products: result });
});

app.post('/products', (req, res) => {
  const { name, price, category } = req.body;
  const product = {
    id: products.length + 1,
    name,
    price,
    category: category || 'general',
  };
  products.push(product);
  res.status(201).json(product);
});

app.get('/products/:id', (req, res) => {
  const product = products.find(p => p.id === parseInt(req.params.id));
  if (!product) return res.status(404).json({ error: 'Product not found' });
  res.json(product);
});

app.delete('/products/:id', (req, res) => {
  const index = products.findIndex(p => p.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Product not found' });
  products.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Products server on http://localhost:3000'));
