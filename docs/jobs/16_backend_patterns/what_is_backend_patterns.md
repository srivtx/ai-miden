## Why it exists (THE PROBLEM)

Every production API needs: authentication (who are you?), rate limiting (how much can you call?), caching (same question = same answer), retry logic (transient failures happen), and correlation IDs (trace a request through microservices). Without these, your API is a prototype. With them, it's production.

These patterns aren't ML-specific. They're backend fundamentals. But every ML engineer deploys models, so every ML engineer needs them. The gap: ML curricula teach you to train models. Nobody teaches you to serve them safely.

## Pattern 1: API Key Authentication

**The problem:** Anyone with your URL can call your model. You pay per token. An attacker finds your endpoint and runs 10,000 prompts. Your bill: $500. You have no way to identify them or stop them.

**The solution:** Require an API key. FastAPI dependency injection makes this clean:

```python
from fastapi import Header, HTTPException, Depends

VALID_KEYS = {"sk-prod-123": "premium", "sk-test-456": "free"}

async def auth(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")
    token = authorization.split(" ")[1]
    if token not in VALID_KEYS:
        raise HTTPException(403, "Invalid key")
    return token

@app.post("/complete")
async def complete(key: str = Depends(auth)):
    # key is validated, user is authenticated
    ...
```

**Key decisions:**
- Bearer token vs API key header? Bearer (standard, works with proxies)
- Revocation? Check against a DB on every request (expensive) or use JWT with short expiry
- Rate limiting per key? Yes — track usage per key

## Pattern 2: Token Bucket Rate Limiter

**The problem:** One user sends 1000 requests/second. Others wait. GPU maxes out. Costs spike. You need to limit each user to N requests per time window.

**Token bucket (better than fixed window):** Each user has a bucket of tokens. Bucket refills at `rate` tokens/second, capped at `max_tokens`. Each request consumes 1 token. If bucket is empty → 429. 

**Why token bucket > fixed window:**
- Fixed window: 60 requests/minute. All 60 at second 1, then 59 seconds of denial. Bursty but unfair.
- Token bucket with refill rate=1/s, max=60: 60 at once (use all tokens), then 1/second after. Allows bursts but smooths to a steady rate.

```python
class TokenBucket:
    def __init__(self, rate, max_tokens):
        self.rate = rate  # tokens per second
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_refill = time.monotonic()

    def consume(self, n=1):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.rate)
        self.last_refill = now
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False
```

## Pattern 3: Caching (Exact + Semantic)

**The problem:** Two users ask the same question. You call the LLM twice. Pay twice. Wait twice. Same cost, same latency, same result. Waste.

**Exact cache:** Hash the (prompt, max_tokens, temperature, model) → store result. Next time same hash appears → return cached result. TTL: 1 hour. LRU eviction when full.

**Semantic cache (for LLMs):** Two prompts are semantically equivalent but textually different:
- "What is the capital of France?"
- "France's capital city is?"
Same answer. Exact cache misses. Semantic cache: embed both prompts, compute cosine similarity. If similarity > 0.95, return cached result without calling the model. Cost: one embedding per cache query (cheap — 0.1ms). Benefit: avoids one LLM inference (expensive — 500ms).

**When to use each:**
- Exact: cheap (SHA256 hash), misses on rephrasing
- Semantic: more expensive (embedding), catches rephrasing
- Both: exact first (free), semantic second (cheap), LLM last (expensive)

## Pattern 4: Retry with Exponential Backoff

**The problem:** You call an external API. It times out. You retry immediately. It times out again because you're hammering it. You retry again. Now you've sent 3 requests and all failed.

**The fix:** Wait before retrying. And wait LONGER each time. Exponential backoff: wait 0.5s, then 1s, then 2s, then 4s. Gives the downstream service time to recover. Also: don't retry on permanent errors (4xx = your request is wrong, retrying won't help). Only retry on transient errors (5xx, timeout, connection reset).

```python
async def retry_with_backoff(func, max_retries=3, base=0.5):
    for attempt in range(max_retries):
        try:
            return await func()
        except TransientError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(base * (2 ** attempt))
```

## Pattern 5: Correlation IDs

**The problem:** A user reports "my request at 2:37 PM failed." You grep logs for "2:37 PM" and find 43 requests across 3 services. Which one is theirs? You can't tell.

**The fix:** Generate a unique ID at the API edge. Attach it to every log line, every downstream call, every database query. Pass it in headers (`X-Correlation-ID`). Now grep for that ID and you get the ENTIRE trace: request came in at 2:37:01 → cache miss → model inference started at 2:37:02 → GPU OOM at 2:37:03 → error returned. One grep, full story.

```python
# Edge: generate or extract
@app.middleware("http")
async def add_correlation_id(request, call_next):
    cid = request.headers.get("X-Correlation-ID", str(uuid4())[:8])
    correlation_id_var.set(cid)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = cid
    return response

# Everywhere: log with the ID
log_event("INFO", "cache_miss", correlation_id=correlation_id_var.get())
```

## Putting them together

The `projects/llm_gateway/main.py` implements all 5 patterns in a single FastAPI app. 250 lines. Run it. Test it. Then apply the same patterns to cortexcode or logogen.
