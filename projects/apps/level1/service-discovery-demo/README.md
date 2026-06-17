# Service Discovery Demo — Registry, heartbeats, TTL, health states

In a microservices world, services come and go. The registry knows who's alive and routes traffic only to healthy instances.

## Endpoints
```
POST   /registry/services                    # register
POST   /registry/services/:id/heartbeat      # keep alive
DELETE /registry/services/:id                # deregister
GET    /registry/services?health=healthy     # list (filter by health)
GET    /registry/discover/:name              # find healthy instances of a service
GET    /registry/services-by-name            # count by service name
```

## Health states
- **healthy**: heartbeat within TTL/2
- **degraded**: heartbeat between TTL/2 and TTL
- **unhealthy**: no heartbeat for more than TTL

## Try
```bash
# Register a new instance
curl -X POST http://localhost:3000/registry/services \
  -H "Content-Type: application/json" \
  -d '{"name": "payment-service", "host": "10.0.0.5", "port": 3003}'
# 201 { id: "payment-service-...", ... }

# Find healthy instances
curl http://localhost:3000/registry/discover/user-service
# { service: "user-service", instances: [...], count: 2 }
```

## What this teaches
1. **Service registry**: central place to find service instances
2. **Heartbeat**: clients tell the registry "I'm still alive"
3. **TTL**: if no heartbeat, the service is considered down
4. **Health states**: healthy, degraded, unhealthy (3 levels)
5. **Discovery**: clients query "give me a healthy payment-service"
6. **Real systems**: Consul, Eureka, etcd, Kubernetes DNS
