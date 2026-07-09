---
name: agentme-edr-policy-122-unit-test-requirements
description: Defines unit test requirements for assertions, offline execution, coverage, shared setup, and real-code preference. Use when writing or reviewing tests.
apply-to: All projects with unit tests
valid-from: 2026-05-25
---

# agentme-edr-policy-122: Unit test requirements

## Context and Problem Statement

Without clear unit testing standards, test suites become inconsistent — tests lack assertions, coverage is spotty, setup code is duplicated, and mocks bypass real logic.

What unit testing practices should be followed to ensure tests are meaningful, reliable, and maintainable?

## Decision Outcome

**Every test MUST assert behavior, run offline without external dependencies, enforce 80% coverage, centralize shared setup, and prefer real code over mocks.**

### Details

#### 01-must-have-at-least-one-assertion-per-test

Every test MUST have at least one assertion that validates the expected behavior.

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

Unit tests MUST NOT depend on any external resources: no network calls, no running databases, no external APIs, no file system paths outside the repo. Tests MUST pass with only static code available.

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

Builds that miss the threshold MUST NOT be merged.

---

#### 04-must-place-test-files-alongside-source

Test files MUST live next to the source file they test, in the same directory, following the convention of the language/framework:

| Language | Pattern | Example |
|----------|---------|-------|
| TypeScript/JavaScript | `[name].test.ts` or `[name].spec.js` | `file1.test.ts` |
| Go | `[name]_test.go` | `file1_test.go` |
| Python | `[name]_test.py` | `myfunc_test.py` |

```
src/mymodule/group1/file1.ts        ← source
src/mymodule/group1/file1.test.ts   ← test (same directory)
```

**Exception — separate test folder:** When the framework makes co-location impractical (e.g. Python's common `tests/` convention), or when the community strongly favors a separate folder, a dedicated test root (e.g. `tests/`) is allowed. In that case the test folder MUST mirror the source folder structure exactly:

```
src/mymodule/group1/file1.py          ← source
tests/mymodule/group1/file1_test.py   ← test (mirrored path)
```

Do not flatten or reorganize paths when using a separate test folder.

---

#### 05-should-extract-shared-setup

When setup logic is repeated across two or more test files, it SHOULD be centralized (`src/test-utils/`, `internal/testutil/`, `tests/conftest.py`).

```typescript
// src/test-utils/order-factory.ts
export function makeOrder(overrides: Partial<Order> = {}): Order {
  return { id: "ord-1", items: [{ sku: "A", qty: 1, price: 10 }], status: "pending", ...overrides };
}
```

---

#### 06-should-avoid-mocks

Tests SHOULD use the lowest-cost alternative that exercises real behavior:

1. **Real implementation** — MUST be preferred
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
