---
name: agentme-edr-002-coding-best-practices
description: Defines cross-language coding practices for keeping code readable, modular, and synchronized with tests and documentation. Apply across projects adopting agentme engineering standards.
---

# agentme-edr-002: Coding best practices

## Context and Problem Statement

Without consistent coding standards, codebases tend to accumulate large, hard-to-navigate files, tangled logic, and documentation that drifts out of sync with the implementation. This leads to slower onboarding, harder maintenance, and higher defect rates.

What coding practices should be followed across all languages and projects to keep code readable, maintainable, and well-structured?

## Decision Outcome

**Apply a set of language-agnostic structural and organizational practices that keep files small, logic decomposed, types co-located, tests co-located, and documentation always in sync.**

### Implementation Details

#### 01-keep-files-short

A file must not exceed **400 lines**. When a file grows beyond this limit, split related functions or types into separate, focused modules.

One exception are test files, which normally are bigger than the tested resources.

*Why:* Large files make navigation slow, increase merge conflicts, and obscure the single-responsibility principle.

**Example (TypeScript):**

```
# before — one bloated file
src/
  orders.ts          # 650 lines: validation, pricing, persistence, notifications

# after — split by responsibility
src/
  orders/
    validation.ts    # 120 lines
    pricing.ts       #  95 lines
    persistence.ts   # 110 lines
    notifications.ts #  80 lines
    index.ts         #  30 lines  (re-exports the public API)
```

---

#### 02-apply-template-method-pattern

When a function's main logic contains well-defined sections and **any individual section exceeds ~20 lines**, extract each section into its own named function. The outer function becomes an orchestrator that calls the extracted helpers in sequence.

*Why:* Named sub-functions serve as inline documentation, are independently testable, and reduce cognitive load.

**Example (Python):**

```python
# before — one long function with implicit sections
def process_order(order):
    # --- validate ---          (~25 lines)
    if not order.items:
        raise ValueError("empty order")
    # ... more validation ...

    # --- calculate price ---   (~30 lines)
    subtotal = sum(i.price * i.qty for i in order.items)
    # ... discounts, taxes ...

    # --- persist ---           (~22 lines)
    db.save(order)
    # ... audit log ...

# after — template method style
def process_order(order):
    _validate_order(order)
    total = _calculate_price(order)
    _persist_order(order, total)

def _validate_order(order): ...
def _calculate_price(order) -> Decimal: ...
def _persist_order(order, total): ...
```

---

#### 03-keep-readme-tests-and-examples-in-sync

Every change to a public interface, behavior, or configuration option must be reflected in:

- `README.md` — update usage examples, option tables, and feature descriptions.
- Unit/integration tests — update or add tests that cover the changed behavior.
- `examples/` resources — update runnable examples so they continue to work.

*Why:* Stale documentation and broken examples erode trust and waste time for consumers of the code.

---

#### 04-declare-types-in-file-where-used

If a type (struct, interface, class, typedef, etc.) is used in only **one** file, declare it in that same file. Move a type to a shared module only when it is referenced in two or more files.

*Why:* Co-locating a type with its sole consumer removes the need to navigate to a separate types file and makes the type's purpose immediately obvious from context.

---

#### 05-keep-test-files-next-to-source

Where the language ecosystem supports it (e.g. JavaScript/TypeScript, Go, Rust), place test files **beside** the source file they cover and use a consistent naming convention rather than mirroring the source tree in a separate `tests/` folder.

**Recommended naming conventions:**

| Language / ecosystem | Source file      | Test file              |
|----------------------|------------------|------------------------|
| TypeScript / JS      | `app.ts`         | `app.test.ts`          |
| Go                   | `handler.go`     | `handler_test.go`      |
| Rust                 | `parser.rs`      | inline `#[cfg(test)]`  |
| Python               | `service.py`     | `service_test.py` (same directory, or `tests/` when the ecosystem convention dictates otherwise) |
