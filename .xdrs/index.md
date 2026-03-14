# XDR Standards Index

This index points to all type- and scope-specific XDR indexes. XDRs (Decision Records) cover Architectural (ADR), Business (BDR), and Engineering (EDR) decisions. Each scope has its own canonical index that lists all XDRs for that scope, organized by subject.

## Scope Indexes

XDRs in scopes listed last override the ones listed first

### _core

Decisions about how XDRs work
[View general ADRs Index](_core/adrs/index.md)

---

### agentkit

Opiniated set of decisions and skills for common development tasks

[View agentkit EDRs Index](agentkit/edrs/index.md)

---

### _local (reserved)

Project-local XDRs that must not be shared with other contexts. Always keep this scope last so its decisions override or extend all scopes listed above. Add specific `_local` ADR/BDR/EDR index links here when present.

[View _local BDRs Index](_local/bdrs/index.md)

[View _local ADRs Index](_local/adrs/index.md)
