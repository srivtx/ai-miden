# API Client Demo — Retry, timeout, circuit breaker

Patterns for calling other services reliably. Three classic resilience patterns.

## Endpoints (mock external service)
```
GET  /mock-external?fail=0.5&delay=0   # simulate a flaky upstream
GET  /proxy/retry                      # retry with exponential backoff
GET  /proxy/breaker                    # call through a circuit breaker
GET  /proxy/timeout                    # 5s timeout on a 10s request
GET  /breaker/status                   # current circuit state
```

## Try
```bash
# Retry (succeeds after some failures)
curl http://localhost:3000/proxy/retry
# { success: true, attempts: 2, body: {...} }

# Circuit breaker (after 3 failures, opens and refuses to call)
for i in {1..5}; do curl http://localhost:3000/proxy/breaker; echo; done
# First few: 502 with breaker.status.state going to "open"
# Last few: 502 with error: "Circuit open: not calling"

# Timeout
curl http://localhost:3000/proxy/timeout
# 504 { error: "Timeout after 500ms" }
```

## What this teaches
1. **Retry with exponential backoff**: don't hammer a failing service
2. **Don't retry 4xx**: client errors won't fix themselves; only retry 5xx and network errors
3. **Circuit breaker**: stop calling a failing service to give it time to recover
4. **Half-open state**: after a timeout, try one request to see if the service is back
5. **Timeout per request**: never wait forever
6. **3 states**: closed (normal) → open (refusing) → half-open (testing)
