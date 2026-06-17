# Testing Demo — Testable Express endpoints + a mini test runner

Same endpoints as a real app, but with a built-in test runner. Run with `node server.js test` to see 5 tests pass.

## Endpoints
```
POST   /todos            { title, user_id }     # create
GET    /todos/:id                              # read
GET    /users/:userId/todos                    # list
PATCH  /todos/:id        { done }               # update
DELETE /todos/:id                               # delete
```

## Run tests
```
node server.js test
```

Output:
```
Running tests:
  PASS  POST /todos creates a todo
  PASS  POST /todos rejects empty title
  PASS  GET /todos/:id returns the todo
  PASS  PATCH /todos/:id marks done
  PASS  DELETE /todos/:id removes

All tests passed
```

## What this teaches
1. **Testable design**: routes as a function `routes(db)` that takes a DB and returns a router
2. **Test isolation**: each test creates its own in-memory DB
3. **Mini test runner**: no jest/mocha, just `assertEqual` and `assertStatus`
4. **HTTP testing**: spawn the app on a random port, make real HTTP requests
5. **CRUD test coverage**: create, read, update, delete, error cases
