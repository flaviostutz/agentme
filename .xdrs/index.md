# XDR Standards Index

This index points to all type- and scope-specific XDR indexes. XDRs (Decision Records) cover Architectural (ADR), Business (BDR), and Engineering (EDR) decisions. Each scope has its own canonical index that lists all XDRs for that scope, organized by subject.

## Scope Indexes

XDRs in scopes listed last override the ones listed first

### _core

Decisions about how XDRs work
[View _core ADRs Index](_core/adrs/index.md)
[View _core BDRs Index](_core/bdrs/index.md)

---

### agentme

Opiniated set of decisions and skills for common development tasks

[View agentme EDRs Index](agentme/edrs/index.md)

---

### _local (reserved)

Project-local XDRs that must not be shared with other contexts. Always keep this scope last so its decisions override or extend all scopes listed above. Keep `_local` canonical indexes in the workspace tree only; do not link them from this shared index. Readers and tools should still try to discover existing `_local` indexes in the current workspace by default.
