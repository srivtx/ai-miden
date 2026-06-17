## Why it exists (THE PROBLEM)

A user uploads a 50MB video. You need to transcode it (convert formats, create thumbnails). Transcoding takes 30 seconds. If you do it inside the request handler, the user waits 30 seconds. The server is blocked. If 5 users upload simultaneously, the server runs out of memory (5 × 50MB in RAM).

**Message queues** decouple the request from the work. The request handler posts a message: `{ type: 'transcode', videoId: 42 }`. A worker picks it up minutes later, transcodes, updates the DB. The user sees "Processing... check back in 2 minutes." Zero server blocking. Zero concurrent memory overhead.

## Definition

**Message Queue** = a buffer between producers and consumers. Producers PUSH messages. Consumers PULL and process them. The queue guarantees: at-least-once delivery, order within a partition, persistence (messages survive server restart).

**Key patterns:**
| Pattern | What it does | When |
|---|---|---|
| **Work Queue** | N workers compete for messages. Each message processed once. | Transcoding, email, image resize |
| **Pub/Sub** | One message → all subscribers. Each gets a copy. | Notifications, cache invalidation |
| **Routing** | Messages routed by key. `order.created` → order service. `user.signup` → email + analytics. | Event-driven architecture |
| **RPC** | Request-reply. Send msg → wait for response. | Service-to-service calls |
| **Delayed Queue** | Message processed after N seconds. | Reminders, retry with delay |

## RabbitMQ vs Kafka vs Redis

| | RabbitMQ | Kafka | Redis Pub/Sub |
|---|---|---|---|
| **Best for** | Task queues, RPC | Event streaming, logs | Simple pub/sub |
| **Delivery** | Push (to consumer) | Pull (consumer polls) | Push |
| **Persistence** | Yes (disk) | Yes (disk, designed for it) | No (in-memory, lost on restart) |
| **Replay** | No | Yes (retain for N days) | No |
| **Throughput** | ~20K msg/s | ~1M msg/s | ~100K msg/s |
| **Complexity** | Medium | High | Low |

**Rule of thumb:** Redis for prototyping. RabbitMQ for task processing. Kafka for event streaming at scale.
