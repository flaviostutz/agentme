---
name: agentme-edr-011-service-health-check-endpoint
description: Defines the required health endpoint contract for service availability and dependency readiness checks. Use when implementing or reviewing service health endpoints.
---

# agentme-edr-011: Service health check endpoint

## Context and Problem Statement

Services in distributed environments need standardized health endpoints so load balancers, orchestrators, and monitoring systems can determine availability and readiness. Without consistent health checks, infrastructure cannot make informed routing decisions and operational teams lack visibility into dependency status.

How should services expose their health status and validate operational readiness?

## Decision Outcome

**Standardized `/health` endpoint with dependency validation**

All services must expose a `GET /health` endpoint that validates external dependencies using read-only operations and returns structured status with appropriate HTTP codes.

### Implementation Details

**Endpoint contract:**

| Aspect | Requirement |
|--------|-------------|
| Path | `/health` |
| Method | `GET` |
| Authentication | None (publicly accessible) |
| Timeout | 30 seconds maximum |

**HTTP status codes:**

| Code | State | Infrastructure action |
|------|-------|-----------------------|
| `200` | `OK` | Route traffic normally |
| `210` | `WARNING` | Route normally, trigger alerts |
| `503` | `ERROR` | Remove from load balancer rotation |

**Response body:**
```json
{ "health": "OK|WARNING|ERROR", "latencyMs": 156, "message": "All dependencies operational" }
```

- `health` (required): overall state — `OK`, `WARNING`, or `ERROR`
- `latencyMs` (required): total milliseconds to run all checks
- `message` (required): human-readable summary; must never expose credentials, internal IPs, or stack traces

**Dependency validation rules:**

- Check all external dependencies (databases, downstream APIs, queues, caches) using read-only operations (e.g., `SELECT 1`, lightweight GET, connection ping)
- Never execute write operations or create side effects
- `OK`: all dependencies healthy within expected thresholds
- `WARNING`: non-critical dependency degraded, or elevated but acceptable response times
- `ERROR`: critical dependency unavailable or service unable to process requests

**Implementation guidelines:**

- Run dependency checks in parallel to minimize latency
- Cache check results for 5–10 seconds to avoid overwhelming dependencies
- Apply per-dependency timeouts (5–10 seconds each)
- Use circuit breaker patterns to fail fast on known-bad dependencies
- Log failures for debugging; avoid excessive logging on every successful check

**Integration points:**

- Load balancers: 30 s interval, 2 consecutive failures to mark unhealthy, 2 successes to restore
- Container orchestrators (ECS, Kubernetes): use `/health` for liveness and readiness probes
- Monitoring: periodic polling with alerts on `210` and `503` responses
- CI/CD: poll `/health` to confirm deployment success

## Considered Options

* (REJECTED) **No health checks** — detect failures through request errors
  * Reason: Reactive; customer-visible failures occur before detection; no degraded-state visibility
* (REJECTED) **Simple ping returning 200** — no dependency validation
  * Reason: A service can appear healthy while critical dependencies are down
* (CHOSEN) **Standardized `/health` with dependency validation** — single aggregated endpoint
  * Reason: Actionable health info without exposing internals; enables infrastructure automation; balances operational visibility with security

## References

- [Health Check Response Format for HTTP APIs (IETF draft)](https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check)
- [AWS ALB Health Checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
