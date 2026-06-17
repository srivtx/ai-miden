# 44 — Rate Limiter

**New concept:** rate limiting. Each client can only make so many requests per second.

If you let any client make unlimited requests, they can overwhelm your server. Rate limiting caps the rate at something sensible (e.g., 10 requests per second per IP).

## Run it

```bash
npm install
node server.js
```

```bash
# Hit the API 15 times rapidly. The first 10 succeed, the rest get 429.
for i in {1..15}; do
  curl -s -o /dev/null -w "Request $i: %{http_code}\n" http://localhost:3000/api/data
done
# Request 1-10: 200
# Request 11-15: 429

# Wait a second, then try again — bucket has refilled
sleep 1
curl -i http://localhost:3000/api/data
# 200, X-RateLimit-Remaining: 0
```

## How to think about it

Think of it like a bouncer at a club. The club has a capacity. Each person who comes in takes a spot. When the club is full, new people are turned away. After some people leave, new people can come in.

The "club" is your server. The "people" are requests. The "capacity" is the bucket size.

## How to build it (line by line)

```js
const CAPACITY = 10;       // max tokens
const REFILL_RATE = 1;     // tokens per second
```

**Lines 11-12.** The bucket can hold 10 tokens. It refills at 1 per second. So if you use 10 in a burst, you wait 10 seconds for the next.

```js
function refill(bucket) {
  const elapsed = (now - bucket.lastRefill) / 1000;
  bucket.tokens = Math.min(CAPACITY, bucket.tokens + elapsed * REFILL_RATE);
  bucket.lastRefill = now;
}
```

**Lines 22-26.** Add tokens based on time passed.

**`Math.min(CAPACITY, ...)`** — never go above the capacity. Even if 100 seconds passed, you only get 10 tokens.

```js
if (bucket.tokens < 1) {
  return res.status(429).json({ error: 'Too many requests' });
}
bucket.tokens -= 1;
```

**Lines 32-37.** If no tokens, reject with 429. Otherwise, take one.

## What we learned

1. Rate limiting protects your server
2. Token bucket is the most common algorithm
3. Status 429 means "too many requests"
4. The `Retry-After` header tells the client when to try again
5. `X-RateLimit-*` headers are standard

## What's next

In **45-cron-scheduler** we run tasks on a schedule.
