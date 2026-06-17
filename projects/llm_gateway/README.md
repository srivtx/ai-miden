# LLM Gateway — Practice Project

A production-ready API gateway for serving language models.

## What you learn

| Pattern | Implementation | File location |
|---|---|---|
| **API Key Auth** | Bearer token, tiered access | `main.py:113-125` |
| **Token Bucket** | Rate limiter per key | `main.py:135-160` |
| **Exact Match Cache** | TTL + LRU OrderedDict | `main.py:168-195` |
| **Structured Logging** | JSON logs with correlation IDs | `main.py:98-108` |
| **Retry + Backoff** | Exponential, permanent vs transient | `main.py:202-218` |
| **Health Probes** | Liveness, readiness endpoints | `main.py:234-244` |
| **Correlation IDs** | Request tracing across services | `main.py:220-230` |
| **Env-based Config** | 12-factor app style | `main.py:86-93` |
| **OpenAPI Docs** | Auto-generated at `/docs` | Built-in (FastAPI) |
| **Graceful Shutdown** | Signal handler, drain requests | Built-in (uvicorn) |

## Run

```bash
pip install fastapi uvicorn
python main.py
# Open http://localhost:8000/docs
```

## Test the patterns

```bash
# 1. Auth: valid key
curl -H "Authorization: Bearer sk-test-key-123" \
     -X POST http://localhost:8000/v1/complete \
     -H "Content-Type: application/json" \
     -d '{"prompt": "def add(a, b):", "max_tokens": 50}'

# 2. Auth: invalid key → 403
curl -H "Authorization: Bearer wrong-key" \
     http://localhost:8000/v1/complete

# 3. Auth: missing key → 401
curl http://localhost:8000/v1/complete

# 4. Cache: repeat request → cached=true, 1ms response
curl -H "Authorization: Bearer sk-test-key-123" \
     -X POST http://localhost:8000/v1/complete \
     -H "Content-Type: application/json" \
     -d '{"prompt": "def add(a, b):", "max_tokens": 50}'

# 5. Rate limit: send 61 requests → 429
for i in {1..65}; do
  curl -s -H "Authorization: Bearer sk-test-key-123" \
       http://localhost:8000/health | grep status
done

# 6. Correlation ID: every response has X-Correlation-ID
curl -i -H "Authorization: Bearer sk-test-key-123" \
     http://localhost:8000/health

# 7. Health probes
curl http://localhost:8000/health   # liveness
curl http://localhost:8000/ready    # readiness
```

## Production checklist (for when you deploy)

- [ ] Replace hardcoded `VALID_KEYS` with a database (or env var `API_KEYS=key:tier,...`)
- [ ] Replace in-memory `ExactCache` with Redis
- [ ] Add real `prometheus_client` metrics
- [ ] Add HTTPS (nginx + Let's Encrypt or Cloudflare tunnel)
- [ ] Add request body size limits (prevents OOM)
- [ ] Add IP-based rate limiting (in addition to key-based)
- [ ] Log to a file or ELK instead of stdout
- [ ] Add anomaly detection on request patterns
