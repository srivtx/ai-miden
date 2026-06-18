# The Connect

> *"The app is observable. Now we need to split into microservices."*

This project added observability. The pain of "is the app working?" is solved. Prometheus scrapes metrics. Grafana visualizes them. We can see request rate, error rate, latency, and Node.js process metrics.

The next (and last) project is **40: Microservices**. We split the monolith into independent services (auth, posts, presence, etc.) that communicate via HTTP and a message broker.

After project 40, the path is **complete**: 40 projects, 6 phases, a complete zero-to-hero backend curriculum.

## What Works

- prom-client exposes metrics
- `/metrics` endpoint
- Prometheus scrapes every 15 seconds
- Grafana visualizes
- Starter dashboard
- Default Node.js metrics

## What Doesn't Work

### 1. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

### 2. No distributed tracing

We can't trace a request across services.

**The pain**: Tracing. Out of scope.

### 3. No log aggregation

We have structured logs but no aggregation.

**The pain**: Log aggregation. Out of scope.

### 4. No APM

No application performance monitoring.

**The pain**: APM. Out of scope.

### 5. No RUM

No real user monitoring (browser-side metrics).

**The pain**: RUM. Out of scope.

### 6. No synthetic monitoring

We don't simulate user actions to check uptime.

**The pain**: Synthetic monitoring. Out of scope.

### 7. No status page

We don't have a public status page.

**The pain**: Status page. Out of scope.

### 8. No SLO / SLI

We don't track service-level objectives.

**The pain**: SLO. Out of scope.

### 9. No alerting (yet)

We have example alerts but no automated alerting.

**The pain**: Alerting. Out of scope.

### 10. No long-term storage

Prometheus is short-term (15 days default). For long-term, use Thanos or Cortex.

**The pain**: Long-term storage. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Expose metrics to Prometheus
- Visualize metrics in Grafana
- Track RED metrics (Rate, Errors, Duration)
- Track Node.js process metrics

It cannot:

- Be split into microservices
- Trace requests across services
- Aggregate logs
- Have APM
- Have RUM
- Have synthetic monitoring
- Have a status page
- Track SLOs
- Alert automatically
- Store metrics long-term

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 40 | Microservice | "I want to split into services." |

Project 40 is the last. After that, the path is **complete**.

---

## What You Should Do Now

1. **Read the code.** Notice the metrics setup, the middleware, the `/metrics` endpoint. The HTTP handlers are extended.
2. **Run the app** with Prometheus and Grafana.
3. **View the metrics** in Grafana.
4. **Set up an alert** (e.g., high error rate).
5. **When you are ready**, move to [Project 40: Microservice](../40-microservice/). This is the **last** project in the path.
6. **If anything is unclear**, do not proceed. Observability is the foundation of production. It must be solid.

---

## A Note on the Bigger Picture

You now have an observable app. You can see what's happening in production. You can spot problems before users do. You can make data-driven decisions.

From here, the path diverges to the final project:

- **Microservice** (project 40): split into services

The app is observable. The path continues — to its end.
