## Why it exists (THE PROBLEM)

You built an API. It handles 10 requests/second on your laptop. You deploy. 1000 users hit it at once. It crashes. You don't know where the bottleneck is — is it the database? The auth middleware? Memory? You can't fix what you can't measure.

**Load testing** simulates real traffic BEFORE users arrive. You run 100 virtual users for 5 minutes. You see: the `/search` endpoint gets slow at 50 concurrent users. The database connection pool maxes out at 20 connections. Memory leaks 2MB per 1000 requests. You fix the bottlenecks BEFORE users hit them.

## Key metrics from a load test

| Metric | What it tells you |
|---|---|
| **Requests/sec** | Can your server handle expected traffic? |
| **p50/p95/p99 latency** | How long do most/mostly/all users wait? |
| **Error rate** | How many requests fail under load? |
| **Concurrent users** | How many simultaneous connections? |
| **Throughput** | Total data transferred |

## Tools (k6 — the standard)

```javascript
// load-test.js — run: k6 run load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // ramp up to 20 users
    { duration: '1m', target: 50 },   // ramp to 50
    { duration: '30s', target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must be <500ms
    http_req_failed: ['rate<0.01'],   // error rate <1%
  },
};

const BASE_URL = 'http://localhost:3000';

export default function () {
  // Test health
  let res = http.get(`${BASE_URL}/health`);
  check(res, { 'status 200': (r) => r.status === 200 });

  // Test auth
  res = http.post(`${BASE_URL}/auth/login`, JSON.stringify({ email: 'test@test.com', password: 'pass' }), { headers: { 'Content-Type': 'application/json' } });
  check(res, { 'auth ok': (r) => r.status === 200 || r.status === 401 });

  // Test search (heavier endpoint)
  res = http.get(`${BASE_URL}/tasks?search=test&page=1&limit=20`);
  check(res, { 'search ok': (r) => r.status === 200 });

  sleep(1);
}
```

## What to do with load test results

1. **High p99 latency at 50 users:** Find the bottleneck (profiler). Usually: database query without index, synchronous file I/O, or GC pause.
2. **Error rate spikes at 100 users:** Connection pool exhausted. Increase `max_connections` or add connection pooling.
3. **Memory grows linearly:** Memory leak. Check that you're not storing request data in global variables.
4. **Throughput plateaus:** CPU-bound. Check for sync operations, add clustering (PM2), or cache heavy endpoints.

## Common confusion

1. **"I'll test in production with real users."** The worst place to discover your server crashes at 100 concurrent users is when 1000 users arrive. Load test BEFORE launch. It's free (k6 is open-source, runs on your laptop).

2. **"One user = one request/second."** Real users interact: click, wait, scroll, click again. The `sleep(1)` in k6 simulates think time. Without it, you're testing a bot attack, not real usage.

3. **"The load test tool must run on a powerful machine."** k6 runs 1000 virtual users on a MacBook. If the tool is the bottleneck (not your server), run k6 in distributed mode or use cloud load testing (k6 Cloud, Artillery Pro).
