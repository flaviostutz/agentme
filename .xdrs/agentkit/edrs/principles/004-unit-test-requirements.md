# agentkit-edr-004: Unit test requirements

## Context and Problem Statement

Without clear unit testing standards, test suites tend to be inconsistent — some tests lack assertions, coverage is spotty, setup code is duplicated across files, and tests rely heavily on mocks that hide bugs by bypassing real logic. This reduces confidence in the test suite and increases maintenance burden.

What unit testing practices should be followed across all projects to ensure tests are meaningful, reliable, and maintainable?

## Decision Outcome

**Apply a set of concrete unit testing requirements that ensure every test asserts behavior, coverage stays high, setup logic is reusable, and mocks are used sparingly in favor of real code execution.**

### Implementation Details

#### 1. MUST have at least one assertion per test

Every test case **must** contain at least one explicit assertion. A test with no assertions provides no value — it can pass even when the code under test is completely broken.

*Why:* Tests without assertions produce false confidence. They appear green but verify nothing.

**Examples:**

```typescript
// bad — no assertion
it("processes the order", () => {
  processOrder(mockOrder);
});

// good — verifies a concrete outcome
it("processes the order and returns a confirmation id", () => {
  const result = processOrder(mockOrder);
  expect(result.confirmationId).toBeDefined();
});
```

```python
# bad — no assertion
def test_process_order():
    process_order(sample_order)

# good
def test_process_order_returns_confirmation():
    result = process_order(sample_order)
    assert result.confirmation_id is not None
```

---

#### 2. MUST maintain at least 80% code coverage

The test suite **must** achieve a minimum of **80% line/branch coverage** across all modules. Coverage must be measured and enforced as part of the CI pipeline — builds failing to meet the threshold must not be merged.

*Why:* A coverage floor ensures that the majority of code paths are exercised, catching regressions early and preventing untested logic from accumulating silently.

**Configuration example (Vitest / TypeScript):**

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: "v8",
      thresholds: {
        lines: 80,
        branches: 80,
      },
    },
  },
});
```

**Configuration example (pytest / Python):**

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-fail-under=80"
```

---

#### 3. SHOULD create shared utility functions for common test setup

When the same setup logic (fixtures, factory functions, seed data, helper wrappers) is repeated across two or more test files, extract it into a **shared test utility module** rather than duplicating it.

*Why:* Duplicated setup code is expensive to maintain — a single change to a data shape or constructor signature requires updates in every file. Centralizing it reduces noise and makes tests easier to read.

**Recommended locations:**

| Ecosystem       | Shared test utilities location           |
|-----------------|------------------------------------------|
| TypeScript / JS | `src/test-utils/` |
| Go              | `internal/testutil/`                     |
| Python          | `tests/conftest.py` (pytest fixtures)    |

**Example (TypeScript):**

```typescript
// src/test-utils/order-factory.ts
export function makeOrder(overrides: Partial<Order> = {}): Order {
  return {
    id: "ord-1",
    items: [{ sku: "A", qty: 1, price: 10 }],
    status: "pending",
    ...overrides,
  };
}

// src/orders/pricing.test.ts
import { makeOrder } from "../test-utils/order-factory";

it("applies discount for large orders", () => {
  const order = makeOrder({ items: [{ sku: "A", qty: 100, price: 10 }] });
  expect(calculateTotal(order)).toBeLessThan(1000);
});
```

---

#### 4. SHOULD avoid mocks — prefer testing real code

Mocks **should be avoided** unless they are unavoidable (e.g. external HTTP calls, time-sensitive operations, or hardware I/O). Prefer using real implementations, in-memory alternatives, or lightweight fakes over complex mock setups.

*Why:* Mocks test the shape of interactions, not the behavior of real code. A heavily mocked test can pass while the real integration is broken. As mock complexity increases, the test becomes harder to read and maintain than the code it is supposed to verify.

**Decision hierarchy for test doubles:**

1. **Real implementation** — use the actual code whenever feasible (fastest feedback, highest confidence).
2. **In-memory / lightweight fake** — e.g. an in-memory database, a stub HTTP server, a local filesystem.
3. **Recorded fixture** — capture real responses once and replay them (e.g. VCR cassettes, snapshot files).
4. **Mock / stub** — only when options 1–3 are impractical (e.g. rate-limited third-party APIs, irreversible operations).

**Examples:**

```typescript
// bad — mocking internal business logic
jest.mock("../pricing", () => ({ calculateTotal: () => 99 }));

it("charges the correct amount", () => {
  const charge = checkout(order);
  expect(charge).toBe(99); // only tests the mock, not the real calculation
});

// good — use the real pricing module
it("charges the correct amount", () => {
  const order = makeOrder({ items: [{ sku: "A", qty: 1, price: 99 }] });
  const charge = checkout(order);
  expect(charge).toBe(99); // verifies real behavior end-to-end
});
```

```python
# bad — patching internal logic
with patch("app.pricing.calculate_total", return_value=99):
    result = checkout(sample_order)
    assert result.amount == 99  # only validates the mock

# good — real call through the stack
sample_order = make_order(items=[Item(sku="A", qty=1, price=99)])
result = checkout(sample_order)
assert result.amount == 99
```

When a mock is genuinely necessary, keep it **narrow** (mock only the single boundary point) and **documented** (add a comment explaining why a real implementation cannot be used).
