# OpenAPI Demo — Spec-first API design with auto-generated docs

Define your API in a spec, generate docs, and clients can use the spec to generate SDKs.

## Endpoints
```
GET  /openapi.json        # the OpenAPI 3.0 spec
GET  /docs                # interactive API documentation

GET    /tasks             # list
POST   /tasks             # create
GET    /tasks/:id         # read
PATCH  /tasks/:id         # update
DELETE /tasks/:id         # delete
```

## Try
```bash
# View the spec
curl http://localhost:3000/openapi.json | jq

# View the docs in a browser
open http://localhost:3000/docs
```

## What this teaches
1. **Spec-first**: define the contract before the code
2. **OpenAPI 3.0**: the standard format for API specs
3. **Components/schemas**: reusable type definitions
4. **Auto-generated docs**: clients can read the spec to know what's available
5. **Client SDK generation**: tools like `openapi-generator` create SDKs from the spec
6. **Validation**: tools can validate requests/responses against the spec
