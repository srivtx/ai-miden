## Why it exists (THE PROBLEM)

One user sends 10,000 requests in 5 seconds. Your server handles them all. The database is overloaded, queries queue up, latency goes from 50ms to 30 seconds. Other users wait. Your costs spike. A bad actor with a simple script can DoS your entire service.

**Rate limiting** says: each user gets N requests per time window. After that, return 429 Too Many Requests. Protect your server from abuse, control costs, and ensure fair access.

This is the second most common pattern in production backends (after auth). Every public API has rate limits. GitHub: 5000/hr authenticated, 60/hr unauthenticated. Twitter: 300/15min for users, 50/15min for apps.

## Definition (very simple)

**Rate limit** = cap on requests per identity per time. Identity can be: IP address, API key, user ID, session token. The cap is a number and a window. Example: 100 requests per minute per IP.

When a request arrives:
1. Identify the caller (IP, token, userId)
2. Look up their request count in the current window
3. If count >= limit, return 429
4. Else, increment count, process request

## Real-life analogy

**Without rate limit = a restaurant with unlimited seating.** 200 people arrive at once. 20 tables. Wait time: 3 hours. Everyone leaves angry.

**With rate limit = a restaurant that takes reservations.** 20 tables, 6 time slots. 120 people per evening. Wait time: 0. The 121st person gets told "we're fully booked tonight, try tomorrow."

## Tiny numeric example

A /search endpoint, limit = 10/min per IP:

```javascript
// Sliding window log
const windows = new Map(); // IP -> [timestamps in last 60s]

function rateLimit(req, res, next) {
  const ip = req.ip;
  const now = Date.now();
  const log = (windows.get(ip) || []).filter(t => t > now - 60000); // remove old
  if (log.length >= 10) {
    const retryAfter = Math.ceil((log[0] + 60000 - now) / 1000);
    res.set('Retry-After', retryAfter);
    return res.status(429).json({ error: 'Too many requests', retryAfter });
  }
  log.push(now);
  windows.set(ip, log);
  next();
}
```

## The 3 main algorithms

### 1. Fixed window
```
Window 1 (00:00-00:59): user makes 100 requests
Window 2 (01:00-01:59): counter resets, user makes 100 more
```
Simple but allows 2× burst at window boundary. If user makes 100 at 00:59 and 100 at 01:00, they get 200 in 2 seconds.

### 2. Sliding window log
```
Keep a list of timestamps for the last 60s
Reject if list length >= limit
```
Most accurate, but memory grows (one entry per request).

### 3. Token bucket
```
Bucket holds N tokens. Refills at R per second.
Each request consumes 1 token. Reject if 0.
```
Allows bursts (if bucket full, all tokens can be used at once), smooths to rate. Most flexible.

### 4. Leaky bucket
```
Queue of N slots. Process at fixed rate R.
Reject if queue is full.
```
Smoother than token bucket. Used when you need steady output rate.

## Common confusion (5+ bullet points)

1. **"Limit per IP — done."** IP can be spoofed. Use API key or user ID as the identity, not just IP. Or both: per IP AND per user. The lowest limit applies.

2. **"Fixed window is fine, simpler."** It has the boundary problem: 200 requests in 1 second at 00:59:30 / 01:00:30. Use sliding window for accuracy. Or token bucket for flexibility.

3. **"Rate limiting makes my server slower."** The check is 1 Map lookup and increment. 0.01ms. The protection it provides (against a 10K request attack) saves you from 10K × actual_cost.

4. **"Return 429 with a Retry-After header."** Standard practice. The header tells the client when to retry. Without it, clients retry immediately, making the problem worse.

5. **"Per-endpoint or global?"** Global: 1000 req/min across all endpoints. Per-endpoint: 60 req/min on /search, 600 req/min on /health. Per-endpoint is more user-friendly. Use both: a global cap protects the server, per-endpoint caps protect specific features.

6. **"Stored where?"** In-memory Map for single server. Redis for multi-server (otherwise each server has its own counter, user gets 3× the limit by hitting different servers).

## Key properties

| Property | Without rate limit | With rate limit |
|---|---|---|
| DDoS protection | None | Yes |
| Server stability | First attacker crashes it | Caps load at design limit |
| Cost | Unbounded (attack pays your bill) | Bounded |
| User experience | Slow under attack | Predictable |
| Implementation cost | $0 | ~10 lines |

## Connection to our projects

Add rate limiting to every API in the 73 backend projects. The pattern is identical: a middleware that runs BEFORE the route handler. 10 lines. Set the limit per use case:
- 100/min for general API endpoints
- 10/min for expensive endpoints (search, generation)
- 1000/min for cheap endpoints (health check)
- 5/min for auth (prevents password brute force)
