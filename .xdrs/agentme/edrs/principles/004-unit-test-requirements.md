---
name: agentme-edr-004-unit-test-requirements
description: Defines unit test requirements for assertions, offline execution, coverage, shared setup, and real-code preference. Use when writing or reviewing tests.
---

# agentme-edr-004: Unit test requirements

## Context and Problem Statement

Without clear unit testing standards, test suites become inconsistent — tests lack assertions, coverage is spotty, setup code is duplicated, and mocks bypass real logic.

What unit testing practices should be followed to ensure tests are meaningful, reliable, and maintainable?

## Decision Outcome

**Every test must assert behavior, run offline without external dependencies, enforce 80% coverage, centralize shared setup, and prefer real code over mocks.**

### Implementation Details

#### 01-must-have-at-least-one-assertion-per-test

```typescript
// bad — no assertion; passes even when code is broken
it("processes the order", () => { processOrder(mockOrder); });

// good
it("processes the order and returns a confirmation id", () => {
  const result = processOrder(mockOrder);
  expect(result.confirmationId).toBeDefined();
});
```

---

#### 02-must-run-offline

Unit tests must not depend on any external resources: no network calls, no running databases, no external APIs, no file system paths outside the repo. Tests must pass with only static code available.

```typescript
// bad — hits a real HTTP endpoint
it("fetches user", async () => {
  const user = await fetch("https://api.example.com/users/1").then(r => r.json());
  expect(user.id).toBe(1);
});

// good — uses a fake/in-memory implementation
it("fetches user", async () => {
  const client = new UserClient({ transport: new InMemoryTransport(fixtures.users) });
  const user = await client.getUser(1);
  expect(user.id).toBe(1);
});
```

---

#### 03-must-maintain-80-percent-coverage

```typescript
// vitest.config.ts
export default defineConfig({
  test: { coverage: { provider: "v8", thresholds: { lines: 80, branches: 80 } } },
});
```

Builds that miss the threshold must not be merged.

---

#### 04-should-extract-shared-setup

When setup logic is repeated across two or more test files, centralize it (`src/test-utils/`, `internal/testutil/`, `tests/conftest.py`).

```typescript
// src/test-utils/order-factory.ts
export function makeOrder(overrides: Partial<Order> = {}): Order {
  return { id: "ord-1", items: [{ sku: "A", qty: 1, price: 10 }], status: "pending", ...overrides };
}
```

---

#### 05-should-avoid-mocks

Use the lowest-cost alternative that exercises real behavior:

1. **Real implementation** — always prefer this
2. **In-memory / lightweight fake** — e.g. in-memory DB, stub HTTP server
3. **Recorded fixture** — replay captured real responses
4. **Mock / stub** — only for external APIs, irreversible operations, or hardware I/O

```typescript
// bad — mocks internal logic; passes even when pricing is broken
jest.mock("../pricing", () => ({ calculateTotal: () => 99 }));

// good — exercises the real pricing module
it("charges the correct amount", () => {
  const order = makeOrder({ items: [{ sku: "A", qty: 1, price: 99 }] });
  expect(checkout(order)).toBe(99);
});
```

When a mock is unavoidable, keep it narrow (one boundary point) and add a comment explaining why.
