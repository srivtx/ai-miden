// 08_rate_limit.js — Three rate limiter patterns: fixed window, sliding window, token bucket.
const express = require('express');
const app = express();

// ---- 1. Fixed window (simplest) ----
const fixedWindow = new Map(); // ip -> { count, resetTime }
function fixedWindowLimiter(windowMs = 60000, max = 20) {
  return (req, res, next) => {
    const ip = req.ip;
    const now = Date.now();
    const entry = fixedWindow.get(ip);
    if (!entry || now > entry.resetTime) { fixedWindow.set(ip, { count: 1, resetTime: now + windowMs }); return next(); }
    entry.count++;
    if (entry.count > max) return res.status(429).json({ error: 'Too many requests', retryAfter: Math.ceil((entry.resetTime - now) / 1000) });
    next();
  };
}

// ---- 2. Token bucket (allows bursts, smooths to rate) ----
const buckets = new Map();
function tokenBucketLimiter(rate = 1, maxTokens = 30) {
  return (req, res, next) => {
    const ip = req.ip;
    const now = Date.now();
    if (!buckets.has(ip)) buckets.set(ip, { tokens: maxTokens, last: now });
    const b = buckets.get(ip);
    b.tokens = Math.min(maxTokens, b.tokens + (now - b.last) * (rate / 1000));
    b.last = now;
    if (b.tokens < 1) return res.status(429).json({ error: 'Rate limited' });
    b.tokens--;
    next();
  };
}

// ---- 3. Sliding window log (most precise, most memory) ----
const slidingLog = new Map(); // ip -> [timestamps]
function slidingWindowLimiter(windowMs = 60000, max = 20) {
  return (req, res, next) => {
    const ip = req.ip;
    const now = Date.now();
    const log = slidingLog.get(ip) || [];
    while (log.length && log[0] < now - windowMs) log.shift();
    if (log.length >= max) return res.status(429).json({ error: 'Rate limited' });
    log.push(now);
    slidingLog.set(ip, log);
    next();
  };
}

app.get('/fixed', fixedWindowLimiter(), (req, res) => res.json({ msg: 'Fixed window' }));
app.get('/token-bucket', tokenBucketLimiter(2, 60), (req, res) => res.json({ msg: 'Token bucket' }));
app.get('/sliding', slidingWindowLimiter(), (req, res) => res.json({ msg: 'Sliding window' }));

app.listen(3000, () => console.log('Rate limit :3000'));
