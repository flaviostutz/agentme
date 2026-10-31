# Focus card template

Used by Phase 4's guided path. Rendered fresh, as its own chat message, before any question is
asked; every field keeps this exact label and order every time, even when blank.

- **PR**: <auto-summary> -- <PR link>
- **Comment**: <X> of <Y> -- <short title>
- **Author**: <author-raw>
- **Said**: <comment-raw, verbatim>
- **Thread**: <every entry in replies-raw, verbatim and in order, never truncated, or "(no replies yet)">
- **Thread summary**: <thread-summary, generated fresh, never persisted -- only when replies-raw has more than 3 entries, shown above the thread as an aid, never a replacement for it>
- **Diff at time of comment**: <diff-hunk-raw fenced block, or "(PR conversation)">
- **Current code**: <source-lines fenced block, an unavailable note, or "(PR conversation)" -- shown only when it differs from the diff above, otherwise omitted>
- **Suggested fix**: <suggested-fix fenced block -- omitted together with the next field when "(none)">
- **Suggested fix assessment**: <accept-as-is|evolve-with-changes|not-recommended, with a short rationale>
- **Type**: <type>
- **Possible user intention**: <possible-user-intention, or blank>
- **Criticality**: <criticality> -- <full rationale, generated fresh, never persisted>
- **Resolvable**: <"reply-only -- cannot be resolved" note, shown only when can_resolve is false>
- **Possible follow-ups**:
  - <candidate next action 1> -- <consequence: effect on the PR, effort, what it postpones>
  - <candidate next action 2> -- <consequence>
- **Recommended action**: <reply|wontfix|fix> -- <one-line reason; the human still decides>
- **Similar comments**: <omitted unless similar-to is non-empty and undecided -- "1 of N near-identical -- file:line, file:line, ...">
- **Open original**: <comment-url>
