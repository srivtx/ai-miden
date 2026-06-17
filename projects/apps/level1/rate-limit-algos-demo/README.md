# Rate Limit Algorithms Demo — Fixed window, sliding window, token bucket

Three algorithms for rate limiting, compared side-by-side. All start with limit=10, window=60s.

## Endpoints
```
GET /test/fixed         # fixed window
GET /test/sliding        # sliding window (timestamp-based)
GET /test/token          # token bucket
GET /burst               # hit all 3 with 15 requests, see which pass
GET /admin/limits        # inspect state
```

## Try
```bash
# Hit the fixed window 12 times rapidly
for i in {1..12}; do curl -i http://localhost:3000/test/fixed; echo; done
# First 10: 200
# Last 2: 429 with Retry-After

# Compare all three at once
curl http://localhost:3000/burst
# {
#   "fixed": [allowed, allowed, ... (10 allowed, 5 blocked)],
#   "sliding": [allowed, allowed, ... (10 allowed, 5 blocked)],
#   "token": [allowed, allowed, ... (10 allowed, 5 blocked, but refills)]
# }
```

## What this teaches
1. **Fixed window**: simple but allows bursts at window boundaries (2x limit possible)
2. **Sliding window**: smoother, no boundary bursts, but stores timestamps
3. **Token bucket**: smooth rate, allows bursts up to capacity, refills continuously
4. **Algorithm choice**: trade-off between simplicity and smoothness
5. **Retry-After header**: tells the client when to retry
6. **X-RateLimit headers**: Limit, Remaining — industry standard
