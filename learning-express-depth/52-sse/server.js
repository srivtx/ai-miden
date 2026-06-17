// 52 — Server-Sent Events (SSE)
// NEW CONCEPT: one-way streaming from server to client.
// WebSocket is bidirectional. SSE is server-to-client only. Simpler.
const express = require('express');
const app = express();

// SSE endpoint: streams events
app.get('/events', (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  });
  res.flushHeaders();

  // Send a tick every second
  let n = 0;
  const interval = setInterval(() => {
    n++;
    res.write(`event: tick\ndata: {"n":${n},"ts":${Date.now()}}\n\n`);
    if (n >= 10) {
      clearInterval(interval);
      res.end();
    }
  }, 1000);

  // Clean up if the client disconnects
  req.on('close', () => clearInterval(interval));
});

// A "stock price" stream
const prices = { AAPL: 150, GOOG: 100, MSFT: 300 };
app.get('/stocks', (req, res) => {
  res.set({ 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' });
  res.flushHeaders();
  setInterval(() => {
    for (const [symbol, price] of Object.entries(prices)) {
      // Simulate price change
      prices[symbol] = price + (Math.random() - 0.5) * 2;
      res.write(`event: price\ndata: ${JSON.stringify({ symbol, price: prices[symbol].toFixed(2) })}\n\n`);
    }
  }, 1000);
});

app.listen(3000, () => console.log('SSE on http://localhost:3000'));
