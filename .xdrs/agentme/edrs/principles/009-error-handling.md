---
name: agentme-edr-009-error-handling
description: Defines error handling practices for catching, propagating, surfacing, and testing failures consistently across projects. Use when implementing interfaces and failure paths.
---

# agentme-edr-009: Error handling

## Context and Problem Statement

Poor error handling is one of the most common sources of production incidents. Errors that are silently swallowed hide bugs; exceptions leaked through public interfaces force callers to know internal implementation details; scattered `catch` blocks spread fragile logic across the codebase; processes that exit with code `0` despite failure mislead orchestrators; and untested error paths mean breakages are only discovered in production.

What error handling practices should be followed across all languages and projects to produce systems that fail loudly, communicate failure clearly, and remain easy to reason about?

## Decision Outcome

**Follow a set of consistent error handling practices: catch only where you can handle, return errors as values at interfaces, centralize repetitive catch logic, communicate failure clearly at process and service boundaries, and exercise error paths with dedicated tests.**

### Implementation Details

#### 01-catch-only-where-handled

Never catch an exception unless the catching site can genuinely recover from it, translate it into a meaningful domain error, or enrich it with context before re-throwing. Do **not** swallow exceptions silently. When suppressing an exception is intentional, always add a comment explaining exactly why, or log it at an appropriate level.

*Why:* Swallowed exceptions hide bugs and make incidents impossible to diagnose. Every silent `catch` is a future mystery.

**Examples:**

```typescript
// bad — swallowed silently
try {
  await saveOrder(order);
} catch (e) {
  // nothing here
}

// bad — caught but not handled or re-thrown
try {
  await saveOrder(order);
} catch (e) {
  console.log("error"); // no context, no rethrow, no recovery
}

// good — caught, enriched, re-thrown
try {
  await saveOrder(order);
} catch (e) {
  throw new OrderPersistenceError(`Failed to save order ${order.id}`, { cause: e });
}

// good — intentional suppression with explanation
try {
  await evictCache(key);
} catch (e) {
  // Cache eviction is best-effort; a failure here does not affect correctness.
  logger.warn({ err: e, key }, "cache eviction failed, continuing");
}
```

```python
# bad
try:
    save_order(order)
except Exception:
    pass  # no explanation

# good — intentional suppression documented
try:
    evict_cache(key)
except CacheError:
    # Cache eviction is best-effort; failure does not affect correctness.
    logger.warning("cache eviction failed for key=%s", key, exc_info=True)
```

---

#### 02-avoid-exceptions-in-public-interfaces

At module and service boundaries, prefer returning a value that signals success or failure (e.g., a result type, a discriminated union, or a `(value, error)` tuple as in Go) over throwing exceptions. This forces callers to explicitly acknowledge and handle the error case before using the result.

*Why:* Exceptions are invisible in signatures. A caller who doesn't know an exception can be thrown will never write a handler. Explicit error return values make the contract visible and encourage handling at the call site.

**Examples:**

```typescript
// bad — exception leaks from a public function
async function fetchUser(id: string): Promise<User> {
  const row = await db.query("SELECT * FROM users WHERE id = $1", [id]);
  if (!row) throw new Error("user not found"); // caller must know this can throw
  return row;
}

// good — result type makes the error case explicit
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

async function fetchUser(id: string): Promise<Result<User, "not-found" | "db-error">> {
  try {
    const row = await db.query("SELECT * FROM users WHERE id = $1", [id]);
    if (!row) return { ok: false, error: "not-found" };
    return { ok: true, value: row };
  } catch (e) {
    logger.error({ err: e, userId: id }, "db query failed");
    return { ok: false, error: "db-error" };
  }
}

// caller is forced to check
const result = await fetchUser(id);
if (!result.ok) {
  // handle not-found or db-error
  return;
}
use(result.value);
```

```go
// Go — idiomatic error return
func FetchUser(id string) (*User, error) {
    row, err := db.QueryRow("SELECT * FROM users WHERE id = $1", id)
    if err != nil {
        return nil, fmt.Errorf("fetchUser %s: %w", id, err)
    }
    return row, nil
}

// caller must inspect error before using value
user, err := FetchUser(id)
if err != nil {
    return err
}
```

```python
# good — use a result-like pattern or explicit sentinel returns
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err:
    error: str

def fetch_user(user_id: str) -> Ok[User] | Err:
    try:
        row = db.query("SELECT * FROM users WHERE id = %s", (user_id,))
        if row is None:
            return Err("not-found")
        return Ok(row)
    except DBError as e:
        logger.error("db query failed", exc_info=True, extra={"user_id": user_id})
        return Err("db-error")
```

---

#### 03-centralise-repetitive-catch-logic

If the same `try/catch` pattern (e.g., logging, classifying HTTP errors, wrapping exceptions) appears in multiple places, extract it into a shared utility. Do not copy-paste catch blocks across the codebase.

*Why:* Scattered catch blocks drift out of sync — one gets updated, the others don't. A central utility is tested once and applied everywhere consistently.

**Examples:**

```typescript
// bad — copy-pasted http error handling across many call sites
try {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
} catch (e) {
  logger.error({ err: e }, "request failed");
  throw e;
}

// good — one utility used everywhere
async function httpGet<T>(url: string): Promise<Result<T, HttpError>> {
  try {
    const res = await fetch(url);
    if (!res.ok) return { ok: false, error: new HttpError(res.status, url) };
    return { ok: true, value: (await res.json()) as T };
  } catch (e) {
    logger.error({ err: e, url }, "http request failed");
    return { ok: false, error: new HttpError(0, url, e as Error) };
  }
}
```

```python
# good — a decorator that handles and logs DB errors uniformly
def handle_db_errors(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except DBError as e:
            logger.error("db error in %s", fn.__name__, exc_info=True)
            return Err("db-error")
    return wrapper

@handle_db_errors
def fetch_user(user_id: str): ...

@handle_db_errors
def save_order(order: Order): ...
```

---

#### 04-communicate-failure-at-boundaries

Every system boundary must signal failure explicitly:

- **OS processes** must exit with a **non-zero exit code** when something went wrong. Exit code `0` means success.
- **HTTP services** must return a **non-2xx/3xx status code** on error, accompanied by a response body that describes the problem without exposing internal system details (stack traces, SQL queries, internal paths, etc.).
- **All error responses** should be logged to the console/structured logger, especially system-level or unexpected errors. Operational teams must be able to find the cause from logs alone.

*Why:* Orchestrators, CI runners, load balancers, and callers all rely on these signals to detect failures automatically. A process or service that reports success on failure leads to silent data corruption and missed alerts.

**Examples:**

```bash
#!/usr/bin/env bash
set -euo pipefail  # exit immediately on error, unset variable, or pipe failure

run_migration() {
  ./bin/migrate up || { echo "Migration failed" >&2; exit 1; }
}

run_migration
```

```typescript
// HTTP handler — bad: always 200, internals leaked
app.post("/orders", async (req, res) => {
  try {
    const order = await createOrder(req.body);
    res.json(order);
  } catch (e) {
    res.status(200).json({ error: e.stack }); // wrong status, stack leaked
  }
});

// HTTP handler — good: correct status, safe message, logged internally
app.post("/orders", async (req, res) => {
  const result = await createOrder(req.body);
  if (!result.ok) {
    if (result.error === "validation") {
      return res.status(400).json({ error: "Invalid order data" });
    }
    logger.error({ error: result.error }, "unexpected error creating order");
    return res.status(500).json({ error: "Internal server error" });
  }
  res.status(201).json(result.value);
});
```

```python
# FastAPI — good error response
@app.post("/orders", status_code=201)
def create_order_endpoint(payload: OrderRequest):
    result = create_order(payload)
    if isinstance(result, Err):
        if result.error == "validation":
            raise HTTPException(status_code=400, detail="Invalid order data")
        logger.error("unexpected error creating order: %s", result.error)
        raise HTTPException(status_code=500, detail="Internal server error")
    return result.value
```

---

#### 05-write-test-cases-for-error-scenarios

Every module that handles errors must have dedicated test cases that verify the error paths. Do not only test the happy path.

*Why:* Error handling code is the code most likely to be broken and the code least likely to be exercised in manual testing. Without automated tests, regressions in error paths go undetected until production.

Typical error scenarios to cover:

- The dependency (DB, HTTP service, file system) is unavailable or times out.
- The input is invalid, missing, or out of range.
- A partial failure occurs (some items processed, some not).
- The system is in an unexpected state (e.g., record not found, duplicate key).

**Examples:**

```typescript
// good — dedicated tests for error scenarios
describe("fetchUser", () => {
  it("returns ok:true with the user when found", async () => {
    db.query.mockResolvedValue(mockUser);
    const result = await fetchUser("123");
    expect(result).toEqual({ ok: true, value: mockUser });
  });

  it("returns ok:false with 'not-found' when the user does not exist", async () => {
    db.query.mockResolvedValue(null);
    const result = await fetchUser("999");
    expect(result).toEqual({ ok: false, error: "not-found" });
  });

  it("returns ok:false with 'db-error' when the db throws", async () => {
    db.query.mockRejectedValue(new Error("connection refused"));
    const result = await fetchUser("123");
    expect(result).toEqual({ ok: false, error: "db-error" });
  });
});
```

```python
# good
def test_fetch_user_found(mock_db):
    mock_db.query.return_value = sample_user
    result = fetch_user("123")
    assert isinstance(result, Ok)
    assert result.value == sample_user

def test_fetch_user_not_found(mock_db):
    mock_db.query.return_value = None
    result = fetch_user("999")
    assert isinstance(result, Err)
    assert result.error == "not-found"

def test_fetch_user_db_error(mock_db):
    mock_db.query.side_effect = DBError("connection refused")
    result = fetch_user("123")
    assert isinstance(result, Err)
    assert result.error == "db-error"
```
