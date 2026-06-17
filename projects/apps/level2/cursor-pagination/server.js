// Cursor-Based Pagination — Modern alternative to offset pagination.
// Offset: slow on large datasets (DB scans and skips rows). Wrong with new items.
// Cursor: stable, fast, works for infinite scroll. Used by Twitter, Instagram, GitHub.
const express = require('express');
const app = express();
app.use(express.json());

const items = Array.from({ length: 1000 }, (_, i) => ({ id: i + 1, name: `Item ${i + 1}`, createdAt: new Date(Date.now() - i * 1000).toISOString() }));

// === OFFSET pagination (simple but slow at scale) ===
app.get('/offset', (req, res) => {
  const limit = Math.min(50, parseInt(req.query.limit) || 20);
  const offset = Math.max(0, parseInt(req.query.offset) || 0);
  const page = items.slice(offset, offset + limit);
  res.json({ data: page, total: items.length, hasMore: offset + limit < items.length });
});

// === CURSOR pagination (fast, stable, infinite scroll friendly) ===
app.get('/cursor', (req, res) => {
  const limit = Math.min(50, parseInt(req.query.limit) || 20);
  const cursor = req.query.cursor ? parseInt(req.query.cursor) : null; // id of the last item from previous page

  let startIdx = 0;
  if (cursor) {
    const idx = items.findIndex(i => i.id === cursor);
    if (idx >= 0) startIdx = idx + 1; // start AFTER the cursor
  }

  const page = items.slice(startIdx, startIdx + limit);
  const nextCursor = page.length === limit ? page[page.length - 1].id : null;

  res.json({
    data: page,
    nextCursor, // pass back as ?cursor= for next page
    hasMore: nextCursor !== null,
  });
});

// === Reverse cursor (older items) ===
app.get('/cursor/older', (req, res) => {
  const limit = Math.min(50, parseInt(req.query.limit) || 20);
  const cursor = req.query.cursor ? parseInt(req.query.cursor) : null;

  let endIdx = items.length;
  if (cursor) {
    const idx = items.findIndex(i => i.id === cursor);
    if (idx >= 0) endIdx = idx; // end BEFORE the cursor
  }

  const startIdx = Math.max(0, endIdx - limit);
  const page = items.slice(startIdx, endIdx);
  const nextCursor = startIdx > 0 ? page[0].id : null;

  res.json({ data: page, nextCursor, hasMore: nextCursor !== null });
});

app.listen(3000, () => console.log('Pagination :3000'));
module.exports = app;
