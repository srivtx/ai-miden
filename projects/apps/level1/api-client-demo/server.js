// API Client Demo — Calls other APIs with retries, timeouts, circuit breaker.
const express = require('express');
const http = require('http');
const https = require('https');
const { URL } = require('url');
const app = express();
app.use(express.json());

// === Simple HTTP client with timeout ===
function fetchUrl(rawUrl, { method = 'GET', headers = {}, body = null, timeoutMs = 5000 } = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(rawUrl);
    const lib = url.protocol === 'https:' ? https : http;
    const req = lib.request({
      method, hostname: url.hostname, port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname + url.search, headers: { 'User-Agent': 'api-client-demo/1.0', ...headers },
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: data }));
    });
    req.on('error', reject);
    req.setTimeout(timeoutMs, () => req.destroy(new Error('Timeout after ' + timeoutMs + 'ms')));
    if (body) req.write(body);
    req.end();
  });
}

// === Retry with exponential backoff ===
async function fetchWithRetry(url, options = {}, { maxAttempts = 3, baseDelayMs = 100 } = {}) {
  let lastErr;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const result = await fetchUrl(url, options);
      // Don't retry 4xx (client error), only 5xx and network errors
      if (result.status < 500) return { ...result, attempts: attempt };
      lastErr = new Error(`HTTP ${result.status}`);
    } catch (e) {
      lastErr = e;
    }
    if (attempt < maxAttempts) {
      const delay = baseDelayMs * Math.pow(2, attempt - 1) + Math.random() * 50;
      await new Promise(r => setTimeout(r, delay));
    }
  }
  throw new Error(`Failed after ${maxAttempts} attempts: ${lastErr.message}`);
}

// === Circuit breaker ===
class CircuitBreaker {
  constructor({ failureThreshold = 3, resetTimeoutMs = 10000 }) {
    this.failureThreshold = failureThreshold;
    this.resetTimeoutMs = resetTimeoutMs;
    this.failures = 0;
    this.state = 'closed';
    this.openedAt = 0;
  }
  async exec(fn) {
    if (this.state === 'open') {
      if (Date.now() - this.openedAt < this.resetTimeoutMs) throw new Error('Circuit open: not calling');
      this.state = 'half-open';
    }
    try {
      const result = await fn();
      this.failures = 0;
      this.state = 'closed';
      return result;
    } catch (e) {
      this.failures++;
      if (this.failures >= this.failureThreshold) {
        this.state = 'open';
        this.openedAt = Date.now();
      }
      throw e;
    }
  }
  get status() { return { state: this.state, failures: this.failures }; }
}

const externalBreaker = new CircuitBreaker({ failureThreshold: 3, resetTimeoutMs: 5000 });

// === Mock external service for demo ===
app.get('/mock-external', (req, res) => {
  const failRate = parseFloat(req.query.fail) || 0;
  const delay = parseInt(req.query.delay) || 0;
  setTimeout(() => {
    if (Math.random() < failRate) return res.status(500).json({ error: 'simulated failure' });
    res.json({ data: 'external response', ts: Date.now() });
  }, delay);
});

// === Endpoints ===
app.get('/proxy/retry', async (req, res) => {
  try {
    const result = await fetchWithRetry('http://localhost:3000/mock-external?fail=0.5', {}, { maxAttempts: 3 });
    res.json({ success: true, attempts: result.attempts, body: JSON.parse(result.body) });
  } catch (e) { res.status(502).json({ error: e.message }); }
});

app.get('/proxy/breaker', async (req, res) => {
  try {
    const result = await externalBreaker.exec(() => fetchWithRetry('http://localhost:3000/mock-external?fail=0.7', {}, { maxAttempts: 1 }));
    res.json({ success: true, body: JSON.parse(result.body), breaker: externalBreaker.status });
  } catch (e) { res.status(502).json({ error: e.message, breaker: externalBreaker.status }); }
});

app.get('/proxy/timeout', async (req, res) => {
  try {
    const result = await fetchUrl('http://localhost:3000/mock-external?delay=10000', { timeoutMs: 500 });
    res.json(result);
  } catch (e) { res.status(504).json({ error: e.message, code: 'timeout' }); }
});

app.get('/breaker/status', (req, res) => res.json(externalBreaker.status));

app.listen(3000, () => console.log('API client demo :3000 — GET /proxy/retry, /proxy/breaker, /proxy/timeout'));
module.exports = app;
