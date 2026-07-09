---
name: agentme-edr-policy-121-coding-best-practices
description: Defines cross-language coding practices for keeping code readable, modular, and synchronized with tests and documentation. Apply across projects adopting agentme engineering standards.
apply-to: All software projects
valid-from: 2026-05-25
---

# agentme-edr-policy-121: Coding best practices

## Context and Problem Statement

Without consistent coding standards, codebases tend to accumulate large, hard-to-navigate files, tangled logic, and documentation that drifts out of sync with the implementation. This leads to slower onboarding, harder maintenance, and higher defect rates.

What coding practices should be followed across all languages and projects to keep code readable, maintainable, and well-structured?

## Decision Outcome

**Apply a set of language-agnostic structural and organizational practices that keep files small, logic decomposed, types co-located, tests co-located, and documentation always in sync.**

### Details

#### 01-keep-files-short

A file MUST NOT exceed **400 lines**. When a file grows beyond this limit, split related functions or types into separate, focused modules.

One exception are test files, which normally are bigger than the tested resources.

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

When a function's main logic contains well-defined sections and **any individual section exceeds ~20 lines**, each section MUST be extracted into its own named function. The outer function becomes an orchestrator that calls the extracted helpers in sequence.

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

#### 03-put-entry-point-function-first

Place the **entry-point function** (the outermost caller) at the **top** of the file. All helper or sub-functions it calls internally MUST appear **below** it.

**Example (Python):**

```python
def process_order(order):          # entry point at the top
    _validate_order(order)
    total = _calculate_price(order)
    _persist_order(order, total)

def _validate_order(order): ...
def _calculate_price(order) -> Decimal: ...
def _persist_order(order, total): ...
```

---

#### 04-keep-readme-tests-and-examples-in-sync

Every change to a public interface, behavior, or configuration option MUST be reflected in:

- `README.md` — update usage examples, option tables, and feature descriptions.
- Unit/integration tests — update or add tests that cover the changed behavior.
- `examples/` resources — update runnable examples so they continue to work.

---

#### 05-declare-types-in-file-where-used

Types used in only **one** file MUST be declared in that same file. Move a type to a shared module only when it is referenced in two or more files.

---

#### 06-keep-test-files-next-to-source

Test files MUST be placed beside the source file they cover, following the co-location and naming conventions defined in [agentme-edr-122 rule 04](122-unit-test-requirements.md). For Rust, use inline `#[cfg(test)]` modules instead of a separate test file.
