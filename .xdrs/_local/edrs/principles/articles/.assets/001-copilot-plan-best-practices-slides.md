---
marp: true
theme: github
paginate: true
---

# Planning with Copilot
## Making AI Your Tool, Not Your Boss

Developer peers &nbsp;|&nbsp; 15 min talk + 15 min live demo

---

## The plan looked great

You asked Copilot to plan a feature. You implemented it.

Two days later:

- The file path it referenced **does not exist**
- The library API was **removed in v3**
- It silently made **three scope decisions** you never agreed to

**Sound familiar?**

Let's talk about why that happens — and how to stop it.

---

## LLMs are statistical, not deterministic

Same prompt → different output every time.

A plausible plan is **not** a correct plan.
The model never says "I'm not sure" — it always sounds confident.

**The key insight**: because it samples from a probability distribution,
repetition + multi-angle challenges can **converge toward correctness**.

That is why planning rounds work.

---

## Cognitive debt

> You are the thinker. The model is the executor.

You decide goals, scope, and tradeoffs.
The model researches, drafts, and fills deterministic gaps.

But this tool:

- **Forgets** context between sessions
- **Pretends** to have understood when it has not
- Is **always confident**, even when wrong

Every unvalidated AI decision = an invisible assumption that compounds.

---

## Concept 1 — Lock intent first

**Before you open /plan:**

1. Write the goal in **one sentence**
2. Write an explicit **Out of Scope** list

Every item on that list is a decision YOU made.
The model cannot silently re-include it later.

---

## Concept 2 — Recognize in-session decisions

When `/plan` drafts a step, it **picks without flagging** it as a decision.

**Two defenses:**

**(a) Proactive** — add to your prompt:
> `"check consistency and ask questions"`

**(b) Reactive** — scan the draft for any step where
the model made a choice on your behalf.
Stop and decide those explicitly.

---

## Concept 3 — Dry-run + consistency

Walk the most complex scenario through the plan step by step:

- Where does it **break**?
- Where are the **gaps**?
- Does step 3 produce **what step 4 expects**?

Example prompts:

> `"If the user submits a payment on a weekend, does this plan handle it correctly?"`
> `"If the file is empty, what does the plan say happens — is that what we want?"`
> `"What happens if the database goes down in the middle of processing a transaction? Ask questions"`
> `"Try to break the featuer and tell me what you found. ask questions"`
> `"What is missing that would leave this half-done for its consumer?"`

Do not accept the draft until you have walked it.

---

## Concept 4 — Rounds + convergence

Send the plan back with challenges:

> `"Check for more features I would probably need but that are not part of the plan. Ask questions."`
> `"Is the plan doing everything we asked in the beginning?"`
> `"How are you making sure those things are implemented correctly?"`
> `"Check for edge cases we didn't discuss yet. Ask questions."`
> `"Explore if all types of input would work with this utility"`
> `"Check for consistency and ask questions"`

**Stop when two consecutive rounds produce only trivial answers.**

Stopping because it *feels* done is not convergence.

---

## Concept 5 — Runnable verification in the plan

`"We will add tests"` is not a plan.

The plan must contain **exact verification steps**:

*Code:*
```sh
node --test
tsc --noEmit
```

*Documents / articles:*
```
- Read the article aloud — does the story flow naturally?
- Check if each section has a clear transition to the next
- Verify every link resolves to the correct target
```

Without executable steps, you cannot confirm the plan succeeded.

---

## Concept 6 — Unverified references

The most common single failure mode.

| Bad | Good |
|---|---|
| `fs.readFileSync('./config/settings.json')` | `[UNVERIFIED — check: ls ./config/settings.json]` |

The model references files, APIs, and packages it never inspected —
with full confidence.

**Before executing**: scan every reference in the plan.
Flag anything the model did not verify directly.

---

## Anti-patterns

**Planning theater**
Rounds that only confirm the plan against itself. Rounds must challenge, not validate.

**Agent self-validation**
The model resolves a subjective decision silently.
You are the oracle for intent; the model is the oracle for deterministic facts.

**Unverified references as facts**
Executing a plan with fabricated file paths or API calls that look correct
but were never inspected.

---

## Summary

| # | Concept | When |
|---|---|---|
| 1 | Lock intent + Out of Scope list | Before /plan |
| 2 | Recognize silent picks + ask it to ask you | Reading the draft |
| 3 | Dry-run the hardest scenario | After draft |
| 4 | Rounds until 2 trivial-answer rounds | Iterate |
| 5 | Exact verification commands in the plan | In the output |
| 6 | Scan for unverified references | Before executing |

---

## Live demo

**Prompt to paste** (verbatim):
```
/plan
I need a Node.js script that reads a JSON file from disk and tells me
if it's valid.
```

**Audience dynamics** — /plan will surface: CLI vs lib? schema vs format? path? exit codes? stderr vs file? stdin? multiple files? &rarr; **audience votes** what's in and what's Out of Scope.

**Constraints** (15 min): ~3 planning rounds (~8 min) + implementation (~5 min) + `node --test` (~2 min). No install step — plain Node.js, zero dependencies.

---

## Take-home

Want a structured procedure that enforces all six practices
with mandatory phases, consistency checks, and a pre-execution readiness gate?

**`refine-plan-mode`**

```
.xdrs/agentme/edrs/principles/skills/
  refine-plan-mode/SKILL.md
```

---

## References

- [Article: copilot-plan-best-practices](../001-copilot-plan-best-practices.md)
- [Demo script](demo-script.md)
- [refine-plan-mode](../../../../../agentme/edrs/principles/skills/refine-plan-mode/SKILL.md)
