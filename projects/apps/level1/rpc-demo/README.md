# RPC Demo — gRPC-style service definitions over HTTP

Service-oriented architecture: define services and methods, then call them via a uniform RPC protocol. This is the same pattern as gRPC, but over HTTP/JSON for simplicity.

## Endpoints
```
POST /rpc/:service/:method     # call a method
GET  /rpc                       # list all services
GET  /rpc/:service              # describe a service
GET  /rpc/:service/health       # health check
```

## Services defined
- **UserService**: `GetUser`, `CreateUser`, `DeleteUser`
- **OrderService**: `CreateOrder`, `GetOrder`, `ListOrders`

## Try
```bash
# Create a user
curl -X POST http://localhost:3000/rpc/UserService/CreateUser \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
# { ok: true, result: { id: 1, name: "Alice", email: "..." }, durationMs: 1 }

# Get a user
curl -X POST http://localhost:3000/rpc/UserService/GetUser \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'

# List services
curl http://localhost:3000/rpc
# { services: { UserService: {...}, OrderService: {...} } }
```

## What this teaches
1. **Service definition**: name + methods with input/output types
2. **Uniform interface**: same URL pattern for all methods
3. **Duration tracking**: how long each RPC takes
4. **Error handling**: ok/!ok, error message, status code
5. **vs REST**: RPC is action-oriented (verb), REST is resource-oriented (noun)
6. **gRPC** uses HTTP/2 + protobuf, this is the same pattern over HTTP/1.1 + JSON
