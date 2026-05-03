# _core Scope Overview

## Overview

The `_core` scope defines the XDR framework itself: how decision records, skills, research, articles, and plans are structured, written, versioned, and discovered. This scope is aimed at engineers, architects, and business analysts who build or consume XDR-based documentation.

## Content

### What this scope covers

The `_core` scope is the foundation that all other scopes inherit from. It establishes the rules and conventions that every XDR document, skill, article, research, and plan must follow regardless of which team, product, or domain produces them.

If you are evaluating whether to adopt XDRs, setting up a new XDR project, or extending the framework with your own scopes, start here.

### Framework structure and organization

The core architectural decision [_core-adr-001](adrs/principles/001-xdrs-core.md) defines the fundamental building blocks: three decision types (ADR for architecture, BDR for business, EDR for engineering), scopes as grouping boundaries, subjects as topic categories within each type, and a folder layout that keeps everything discoverable. It also defines the index system (canonical type indexes, scope indexes, and the root index) that ties the collection together.

### Document writing standards

Each artifact type has its own writing standard:

- **XDR documents** follow [_core-adr-002](adrs/principles/002-xdr-standards.md), which defines the mandatory template, frontmatter metadata, applicability rules, conflict handling, and word limits that keep decisions concise and authoritative.
- **Structured XDRs** with individually referenceable rules follow the extension [_core-adr-008](adrs/principles/008-xdr-standards-structured.md), adding numbered rule blocks and a dot-notation citation syntax.
- **Skills** follow [_core-adr-003](adrs/principles/003-skill-standards.md), using the agentskills format so they work for both humans and AI agents on an automation gradient from fully manual to fully automated.
- **Articles** follow [_core-adr-004](adrs/principles/004-article-standards.md), providing synthetic views that combine and link multiple XDRs, research, and skills without replacing them as the source of truth.
- **Research** follows [_core-adr-006](adrs/principles/006-research-standards.md), using an IMRAD-based structure for studies that back decisions with reproducible evidence.
- **Plans** follow [_core-adr-007](adrs/principles/007-plan-standards.md), capturing ephemeral execution plans with problem context, proposed solutions, milestones, and deliverables that are deleted after implementation.

### Versioning and distribution

[_core-adr-005](adrs/principles/005-semantic-versioning-for-xdr-packages.md) defines how XDR packages use semantic versioning to communicate upgrade impact when decisions are shared across repositories or teams.

### Usage policy

The business decision [_core-bdr-001](bdrs/principles/001-xdr-decisions-and-skills-usage.md) establishes how agents and humans must use XDR decisions and skills, separating policy authority (which lives in XDRs) from execution guidance (which lives in skills).

### Available skills

The `_core` scope ships with six skills that automate the most common framework operations:

- **001-lint** reviews code and files against applicable XDRs
- **002-write-xdr** guides creation of a new decision record
- **003-write-skill** guides creation of a new skill package
- **004-write-article** guides creation of a new article
- **005-write-research** guides creation of a new research document
- **006-write-plan** guides creation of a new execution plan

### Getting started

For a narrative introduction to the framework, including how elements differ, how to decide whether an XDR applies, and how to extend the framework with your own scopes, see the overview article [_core-article-001](adrs/principles/articles/001-xdrs-overview.md).

## Type Indexes

- [ADRs Index](adrs/index.md) - Architectural decisions about the XDR framework structure and standards
- [BDRs Index](bdrs/index.md) - Business and operational decisions about framework usage policy
