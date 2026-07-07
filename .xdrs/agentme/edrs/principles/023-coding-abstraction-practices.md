---
name: agentme-edr-policy-023-coding-abstraction-practices
description: Defines when abstractions (functions, classes, wrappers, factories) are justified and when they must be avoided. Tightly related to agentme-edr-policy-002-coding-best-practices.
apply-to: All software projects
valid-from: 2026-05-29
---

# agentme-edr-policy-023: Coding abstraction practices

## Context and Problem Statement

Abstractions (helper functions, wrapper classes, factories, indirection layers) can clarify intent and reduce duplication — but when applied without discipline they obscure logic, force unnecessary navigation, and inflate codebases. Teams need clear criteria for when an abstraction earns its place versus when it adds unjustified indirection.

What principles should guide the decision to introduce — or reject — an abstraction?

## Decision Outcome

**Apply a bias toward explicit, functional, input→processing→output code. Introduce abstractions only when they demonstrably add value in logic, intent, reusability or readability.**

### Details

#### 01-prioritize-functional-programming

Prefer functional programming: pure functions with clear input → processing → output flow. Object-oriented patterns (classes, inheritance) MAY only be used when there is a clear benefit from the additional abstraction they bring — e.g., when complex context management or true inheritance hierarchies are intrinsically part of the best solution for a problem.

---

#### 02-prefer-explicit-calls-over-indirections

Developers SHOULD prefer a sequence of direct calls to libraries and resources to keep logic straightforward. Avoid:

- Aspect-oriented programming (AOP)
- Implicit context injection / dependency injection containers
- Magic decorators that alter control flow invisibly

These patterns obfuscate the main program flow and create behavioral indirections that require prior knowledge of state machines living outside the code itself.

*When indirection is acceptable:* Framework-mandated patterns (middleware chains, React context, etc.) where the reader already expects the indirection.

---

#### 03-trivial-wrappers-are-prohibited

A function that merely delegates to another function or API call without adding meaningful logic, domain intent, or readability **MUST be inlined**. A wrapper is justified only when it:

- Encapsulates non-trivial logic (validation, retry, transformation).
- Communicates a domain concept the underlying expression does not convey.
- Improves readability of a complex flow by giving a clear name to a cohesive block of work.

**Bad — trivial wrapper:**

```typescript
function getUser(id: string) {
  return db.users.findById(id);
}
```

**Good — adds domain intent:**

```typescript
function isEligibleForTrial(user: User): boolean {
  return !user.hasSubscription && user.createdAt > trialCutoffDate && !user.isBanned;
}
```

---

#### 04-object-factories-must-add-value

A function that constructs an object (e.g., configuration, options) is only justified if it:

- Performs validation or assertion.
- Computes values dynamically based on inputs.
- Combines data in a non-linear or conditional way.
- Is reused by multiple callers.

A function that restructures simple static data in an almost 1-to-1 mapping forces the reader to trace indirection for no benefit and MUST be inlined.

**Bad — trivial factory:**

```typescript
function createConfig(port: number, host: string) {
  return { port, host };
}
```

**Good — adds validation and defaults:**

```typescript
function createServerConfig(opts: Partial<ServerOpts>): ServerConfig {
  if (opts.port && (opts.port < 1 || opts.port > 65535)) {
    throw new Error(`Invalid port: ${opts.port}`);
  }
  return {
    port: opts.port ?? 3000,
    host: opts.host ?? 'localhost',
    timeout: computeTimeout(opts.environment),
  };
}
```

---

#### 05-abstractions-for-business-logic-are-encouraged

Developers SHOULD extract domain logic into a named function when it:

- Encapsulates a business rule so the reader does not need to parse low-level conditions to understand domain intent.
- Communicates intent at a glance, making compound conditions or multi-step checks self-describing.

**Example:**

```typescript
// Good — named function conveys business intent
if (isAllowed(event)) { ... }

// Bad — forces reader to decode domain meaning from raw conditions
if (event.status === 'active' && event.role !== 'guest' && event.quota > 0) { ... }
```

---

#### 06-idiomatic-framework-patterns-are-exempt

React hooks, higher-order components, middleware chains, and similar patterns established by the framework in use MUST NOT be treated as unnecessary abstraction. The reader already expects them, and fighting the framework's idioms creates more confusion than it removes.

This exemption does not override other rules — a trivial wrapper inside a hook is still prohibited.
