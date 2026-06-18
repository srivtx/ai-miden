# The Connect

> *"The server is tested. Now we need Docker, CI/CD, observability, and microservices."*

This project added automated tests. The pain of "I have to click around to verify it works" is solved. We have unit tests and integration tests. Every change runs through the test suite. We catch bugs before they reach production.

The next 4 projects complete Phase 6 (Production):

| # | Project | Pain Answered |
|---|---------|---------------|
| 37 | Container | "I want to deploy reproducibly with Docker." |
| 38 | Pipeline | "I want CI/CD." |
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

After these, the server is a production-ready, real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact.

## What Works

- Vitest test runner
- supertest for HTTP tests
- `:memory:` SQLite for test DB
- Reset between tests
- Auth, post, and rate limit tests

## What Doesn't Work

### 1. No Docker

We can't deploy reproducibly. Different machines have different Node versions, different OS, etc.

**The pain**: Container. Project 37.

### 2. No CI/CD

We can't run tests automatically on every commit. We can't deploy automatically on merge to main.

**The pain**: Pipeline. Project 38.

### 3. No observability

We can't see metrics (request rate, error rate, latency, etc.).

**The pain**: Observability. Project 39.

### 4. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

### 5. No end-to-end tests

We don't test the full user flow in a browser.

**The pain**: E2E tests. Out of scope.

### 6. No load tests

We don't test performance under load.

**The pain**: Load tests. Out of scope.

### 7. No mutation tests

We don't verify that our tests actually catch bugs.

**The pain**: Mutation tests. Out of scope.

### 8. No visual regression

We don't test the UI.

**The pain**: Visual regression. Out of scope.

### 9. No security tests

We don't test for vulnerabilities.

**The pain**: Security tests. Out of scope.

### 10. No coverage requirement

We don't enforce a minimum coverage.

**The pain**: Coverage requirement. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Be tested automatically with Vitest
- Run HTTP tests with supertest
- Reset the database between tests
- Verify handlers, validation, and error handling

It cannot:

- Be deployed reproducibly
- Run tests in CI automatically
- Show metrics
- Be split into microservices
- Test the full user flow in a browser
- Test performance under load
- Verify test quality
- Test the UI
- Test for vulnerabilities
- Enforce coverage

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 37 | Container | "I want to deploy reproducibly with Docker." |
| 38 | Pipeline | "I want CI/CD." |
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

Project 37 is the natural next step. We have tests. Now we need reproducible deployments.

---

## What You Should Do Now

1. **Read the code.** Notice the test setup, the integration tests, the reset between tests. The HTTP handlers are unchanged.
2. **Run the tests** with `npm test`. See the output.
3. **Add more tests.** Cover the post flow, the rate limit, the webhook.
4. **Run with coverage** (`npx vitest --coverage`). See what's covered.
5. **When you are ready**, move to [Project 37: Container](../37-container/).
6. **If anything is unclear**, do not proceed. Tests are the foundation of correctness. They must be solid.

---

## A Note on the Bigger Picture

You now have a tested server. Every change runs through the test suite. We catch bugs before they reach production. We can refactor with confidence.

From here, the path diverges into the final 4 projects of Phase 6 (Production):

- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server is tested. The path continues.
