# API Gateway Demo — Single entry point routing to multiple backends

A gateway is the front door of your microservice system. Clients talk to the gateway, the gateway routes to backends. Common gateway features: auth, rate limiting, logging, request transformation.

## Endpoints
```
GET /                     # gateway info
GET /health               # gateway + backend status
GET /api/users/*          # routed to users service (port 3001)
GET /api/orders/*         # routed to orders service (port 3002)
GET /api/products/*       # routed to products service (port 3003)
GET /api/dashboard        # fan out: aggregate from all services
```

## What this teaches
1. **Single entry point**: clients don't need to know about each service
2. **Path-based routing**: `/api/users/*` → users service
3. **X-Forwarded-For header**: pass the original client IP to backends
4. **Aggregation**: one endpoint that calls multiple backends and combines results
5. **vs no gateway**: clients would need to know every service URL
6. **Production gateways**: Kong, AWS API Gateway, nginx, Envoy
