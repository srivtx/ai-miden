## Missing skills — the final gap analysis

We have 80% of job skills. These are the 20% still missing:

### Backend Engineering for AI (most critical gap)

| Pattern | Why jobs require it | In our curriculum? |
|---|---|---|
| Authentication (JWT, API keys) | Every production API needs auth | ❌ |
| Rate limiting | Prevent abuse, manage cost | ❌ |
| Caching (semantic + exact) | Reduce latency, cut API costs | ❌ |
| Message queues (async processing) | Long inference shouldn't block users | ❌ |
| Idempotency | Duplicate POST requests = disaster | ❌ |
| Webhooks / event-driven | Notify users when model finishes | ❌ |
| Background workers | Process retraining, evaluation offline | ❌ |
| File upload (S3 presigned URLs) | Upload codebase/logos for training | ❌ |

### API Design Patterns

| Pattern | Why | Status |
|---|---|---|
| Rate limiter (token bucket, sliding window) | Every public API | ❌ |
| Circuit breaker | Don't call a dead downstream service | ❌ |
| Retry with exponential backoff | Transient failures happen | ❌ |
| Correlation IDs | Trace a request across services | ❌ |
| Structured logging (JSON) | Searchable, machine-readable logs | ❌ |
| OpenAPI auto-generation | Document your API automatically | ❌ |
| Health check levels (liveness vs readiness) | Kubernetes needs this | ❌ |
| API versioning | Don't break existing clients | ❌ |

### LLM Orchestration

| Pattern | Why | Status |
|---|---|---|
| Multi-model routing | Route to cheapest model that can handle the task | ❌ |
| Semantic caching | Same prompt → same result, don't call LLM | ❌ |
| Cost tracking per request | Know your API spend | ❌ |
| Token counting + truncation | Don't exceed context limits | ❌ |
| Fallback chain | Model A unavailable → try Model B | ❌ |
| Prompt compression | Reduce tokens sent to LLM | ❌ |
| Structured output parsing | LLM returns JSON, parse and validate | ❌ |

### Software Testing for ML

| Pattern | Why | Status |
|---|---|---|
| Unit tests for data pipelines | Did tokenizer change unexpectedly? | ❌ |
| Snapshot testing for model outputs | Did new version produce different outputs? | ❌ |
| Contract tests for API | Did response schema change? | ❌ |
| Chaos testing for ML infra | What if GPU dies mid-inference? | ❌ |
| Load testing (locust, k6) | How many concurrent users can we handle? | ❌ |
