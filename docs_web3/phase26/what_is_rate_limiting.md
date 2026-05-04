# What is Rate Limiting?

## Why It Exists

Blockchain RPC endpoints are expensive and have finite capacity.
Without protection, a single misbehaving script, a popular NFT drop, or an enthusiastic power user can exhaust your quota.
This crashes your service and racks up massive provider bills that appear without warning.
Rate limiting ensures fair resource distribution and prevents abuse from overwhelming your infrastructure.
It is the difference between a sustainable service and one that collapses under unexpected load.
Every production API should implement rate limiting from day one.

## Definition

Rate limiting is a mechanism that controls how many requests a client can make to an API within a specific time window.
It rejects or delays excess requests to protect backend resources from overload.
The goal is to ensure every user gets fair access while preventing any single client from monopolizing resources.
It is a fundamental component of any production API.
Implementing rate limiting early prevents costly incidents as your user base grows.
Think of it as a traffic light for your data highway.

## Real-Life Analogy

Think of a popular nightclub with a single entrance.
If everyone rushes the door at once, nobody gets in and someone gets hurt.
The bouncer enforces a rule: ten people per minute.
Once the limit is reached, newcomers wait in line.
Regulars with VIP passes get a higher limit.
The club operates smoothly, every guest gets attention, and the building does not collapse.

Rate limiting is that bouncer, keeping traffic orderly and the venue sustainable.
Without the bouncer, one rowdy group ruins the night for everyone else.
The bouncer also checks IDs, ensuring only authorized guests enter.
A good bouncer knows the regulars and the troublemakers.
The bouncer might offer a fast lane for VIP members while limiting general admission.

## Tiny Numeric Example

Your RPC provider charges $0.01 per 1,000 requests and allows 100 requests per second.

| Scenario | Requests/Sec | Daily Cost | Outcome |
|---|---|---|---|
| Normal usage | 50 | $0.43 | Healthy |
| Bug in polling loop | 10,000 | $86.00 | Throttled or massive bill |
| DDoS attack | 100,000 | $860.00 | Service down |
| With rate limit (100/min) | Max 100/min | $1.44 | Protected |

A misconfigured client polling every 1ms instead of every 1s generates 1,000x more requests.
Rate limiting catches this before it reaches the provider, saving the developer from a surprise $2,500 monthly bill.
The 429 status code tells the client exactly when to retry.
Proper limits protect both the service and the developer's wallet.
Monitoring rate limit hits also helps identify bugs in client applications.
Unexpected spikes often reveal misconfigured polling loops or runaway scripts.

## Common Confusion

- **"Doesn't rate limiting hurt legitimate users?"** Properly tuned limits protect everyone. The limit should exceed normal usage but catch abnormal spikes.
- **"Is this the same as DDoS protection?"** DDoS protection blocks malicious traffic floods. Rate limiting manages expected API usage from authenticated or known clients.
- **"Why 429 status code?"** HTTP 429 means "Too Many Requests." It tells clients to slow down and often includes a retry-after header.
- **"Can't I just use my provider's rate limits?"** Provider limits are the last line of defense. Your own limits catch abuse earlier and give better error messages.
- **"Do I rate limit by IP or by API key?"** IP limiting is simple but shared IPs get unfairly blocked. API key limiting is fairer for authenticated users.
- **"What if a user genuinely needs more requests?"** Tiered rate limits solve this. Free users get 100/min, paid users get 10,000/min.
- **"Does rate limiting slow down my API?"** The check itself takes microseconds. The bottleneck is usually the blockchain RPC call, not the limit check.
- **"What about burst traffic?"** Token bucket algorithms allow short bursts while maintaining long-term averages.
- **"Can attackers bypass rate limits with proxies?"** Sophisticated attackers can, which is why rate limiting complements other security layers.

## Key Properties

- **Fairness:** Ensures all users get equitable access to shared resources regardless of their technical sophistication.
- **Cost Control:** Prevents runaway clients from generating unexpected bills and exhausting provider quotas.
- **Stability:** Maintains service availability during traffic spikes, attacks, or misconfigured client loops.
- **Transparency:** Communicates limits clearly through HTTP headers so clients can adapt their behavior.
- **Graduation:** Supports tiered access levels so premium users receive higher limits than free users.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase26/rpc_service.ts` implements per-IP rate limiting middleware allowing 100 requests per minute with automatic window reset and 429 responses.
The middleware tracks request counts in memory and resets them on a rolling time window, ensuring that a single misbehaving client cannot degrade service for others.
