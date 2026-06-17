# Pub/Sub Demo — Event bus with topics, subscribers, retry, DLQ

Publish events to topics. Subscribers receive them. Failures retry, then go to a dead-letter queue. Wildcard subscriptions let one handler match many topics.

## Endpoints
```
POST /subscribe/:topic    { failRate? }   -> { subscriptionId }
POST /publish/:topic      { ...data }     -> { eventId, delivered, failed }
GET  /events?topic=...                    -> recent events
GET  /dlq                                  -> failed deliveries
GET  /admin/subscribers                    -> count by topic
```

## Built-in subscribers
- `user.created` → sends welcome email + records analytics
- `order.created` → reserves inventory
- `user.*` → audit log (wildcard)

## Try
```bash
# Publish
curl -X POST http://localhost:3000/publish/user.created \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "userId": 1}'
# 202 { eventId: "evt_...", delivered: 3, failed: 0 }
# (3 = 2 user.created subscribers + 1 wildcard user.*)

# Check event log
curl http://localhost:3000/events?topic=user.created

# Subscribe with 100% failure
curl -X POST http://localhost:3000/subscribe/flaky-topic \
  -H "Content-Type: application/json" \
  -d '{"failRate": 1.0}'
# Now publish to /publish/flaky-topic and check /dlq
```

## What this teaches
1. **Topics**: named channels for events
2. **Multiple subscribers**: same event delivered to N handlers
3. **Wildcard patterns**: `user.*` matches `user.created`, `user.updated`
4. **Retry**: failed deliveries retry up to 3 times
5. **Dead-letter queue**: events that can't be delivered go here
6. **At-least-once**: a subscriber may receive the same event more than once (handlers must be idempotent)
7. **Real systems**: Kafka, RabbitMQ, Redis Pub/Sub, Google Pub/Sub
