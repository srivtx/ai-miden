// 20_sse_stream.js — Server-Sent Events: real-time push without WebSocket complexity.
const express = require('express');
const app = express();

// HTML page that connects to SSE
app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html>
<html><body><h2>SSE Demo</h2><div id="log"></div>
<script>
const evt = new EventSource('/events');
evt.onmessage = (e) => document.getElementById('log').innerHTML += '<p>' + e.data + '</p>';
evt.addEventListener('notification', (e) => document.getElementById('log').innerHTML += '<p style=color:red>NOTIFICATION: ' + e.data + '</p>');
evt.addEventListener('heartbeat', (e) => console.log('heartbeat:', e.data));
</script></body></html>`);
});

// SSE endpoint
app.get('/events', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });

  const clientId = Date.now();
  res.write(`data: Connected as ${clientId}\n\n`);

  // Send heartbeat every 15s (keep connection alive through proxies)
  const heartbeat = setInterval(() => res.write(`event: heartbeat\ndata: ${Date.now()}\n\n`), 15000);

  // Send occasional messages
  let count = 0;
  const timer = setInterval(() => {
    count++;
    res.write(`data: Message ${count} at ${new Date().toISOString()}\n\n`);
    if (count % 5 === 0) res.write(`event: notification\ndata: Milestone: ${count} messages sent!\n\n`);
    if (count >= 20) {
      res.write(`data: Stream closed after ${count} messages\n\n`);
      res.end();
      clearInterval(timer);
      clearInterval(heartbeat);
    }
  }, 2000);

  req.on('close', () => { clearInterval(timer); clearInterval(heartbeat); });
});

app.listen(3000, () => console.log('SSE :3000'));
