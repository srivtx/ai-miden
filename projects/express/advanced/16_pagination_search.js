// 16_pagination_search.js — Full query API: search, filter, sort, paginate, select fields.
const express = require('express');
const app = express();

// Mock data
const products = Array.from({ length: 100 }, (_, i) => ({
  id: i + 1, name: `Product ${i + 1}`,
  category: ['electronics', 'clothing', 'books', 'food'][i % 4],
  price: Math.round((Math.random() * 500 + 10) * 100) / 100,
  inStock: i % 3 !== 0,
  tags: ['new', 'sale', 'popular', 'eco'].slice(0, (i % 4) + 1),
  rating: Math.round((Math.random() * 5) * 10) / 10,
  created: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
}));

function queryAPI(data) {
  return (req, res) => {
    let result = [...data];

    // Search (text match across multiple fields)
    if (req.query.q) {
      const q = req.query.q.toLowerCase();
      result = result.filter(p => p.name.toLowerCase().includes(q) || p.category.includes(q) || p.tags.some(t => t.includes(q)));
    }

    // Filter by exact fields
    if (req.query.category) result = result.filter(p => p.category === req.query.category);
    if (req.query.inStock !== undefined) result = result.filter(p => p.inStock === (req.query.inStock === 'true'));
    if (req.query.minPrice) result = result.filter(p => p.price >= parseFloat(req.query.minPrice));
    if (req.query.maxPrice) result = result.filter(p => p.price <= parseFloat(req.query.maxPrice));

    // Filter by tag (array contains)
    if (req.query.tag) result = result.filter(p => p.tags.includes(req.query.tag));

    // Sort
    const sortField = req.query.sort || 'id';
    const order = req.query.order === 'desc' ? -1 : 1;
    result.sort((a, b) => (a[sortField] > b[sortField] ? 1 : -1) * order);

    // Pagination
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(100, Math.max(1, parseInt(req.query.limit) || 20));
    const total = result.length;
    const pages = Math.ceil(total / limit);
    result = result.slice((page - 1) * limit, page * limit);

    // Select specific fields
    if (req.query.fields) {
      const fields = req.query.fields.split(',');
      result = result.map(p => {
        const obj = {};
        fields.forEach(f => { if (p[f] !== undefined) obj[f] = p[f]; });
        return obj;
      });
    }

    res.json({
      total, page, pages, limit,
      filters: { q: req.query.q, category: req.query.category, minPrice: req.query.minPrice, maxPrice: req.query.maxPrice },
      data: result,
    });
  };
}

app.get('/products', queryAPI(products));

app.listen(3000, () => console.log('Search API :3000'));
/*
Test:
  curl "localhost:3000/products?q=book&sort=price&order=asc&page=1&limit=5&fields=name,price"
  curl "localhost:3000/products?category=electronics&inStock=true&minPrice=100&maxPrice=500"
  curl "localhost:3000/products?tag=sale&sort=rating&order=desc"
*/
