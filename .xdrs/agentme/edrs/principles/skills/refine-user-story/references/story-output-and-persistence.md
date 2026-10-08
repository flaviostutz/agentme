# Story persistence and output template

Detail for Phase 8 of `refine-user-story`: how the refined story is persisted locally and the
template of the story. The skill reads this file when it reaches Phase 8.

## Initiative document integration

After producing the final story output, persist it according to the active initiative context from Phase 1.

**When an XDRS initiative doc is active (Phase 1 selected or created an initiative):**
1. Determine the NNN and slug for the story detail file:
   - **Placeholder story** (Phase 1 picked a pending story): extract the NNN and slug from the placeholder file's `**Story ID:**` line. Reuse them for the refined file.
   - **New story** (Phase 1 chose "New story" or a new epic was created): use the next available NNN in the initiative's `.assets/` folder (list existing `userstory-NNN-*.md` files, increment the highest; start at 001 if empty). Derive the slug by kebab-casing the refined `## Title`, keeping at most 7 words, e.g. `save-payment-method-future-checkouts`.
2. Write the refined story as `.assets/userstory-NNN-slug.md` inside the initiative's `.assets/` folder using the output template, including the `**Story ID:** userstory-NNN-slug` line at the top (no `**Status:**` line — absence of the status field indicates a refined story).
3. In the initiative doc, update the task entry link text in the active Milestone: change `[Brief description — pending]` to `[Refined Story Title]` (keep the same `.assets/userstory-NNN-slug.md` path). For new stories, insert a new task entry `- [Refined Story Title]{.assets/userstory-NNN-slug.md}`.
4. When splitting: for each non-chosen slice, create a placeholder file at `.assets/userstory-NNN-slug.md` containing:
   - `**Story ID:** userstory-NNN-slug`
   - `**Status:** to-be-refined`
   - A `## Title` with the preliminary description of the slice.
   - A `## Notes from intake` section with any relevant context captured in this session: split rationale, relationship to the current story, any API or business details already known.
   - A `## Related` section linking to the current story being refined.
   Assign NNNs sequentially after the highest existing one in `.assets/` (the current story's file already written by step 2 counts as existing). Insert a task entry `- [Slice description — pending]{.assets/userstory-NNN-slug.md}` in the same Milestone (or a new Milestone if the split reveals a distinct Feature). Do NOT offer TODO.md for deferred slices.
5. Add a back-link to the epic initiative at the bottom of the story detail file: `**Epic initiative:** [NNN-epic-slug.md]{../NNN-epic-slug.md}` (the `../` resolves from `.assets/` up to `initiatives/`).

**When no XDRS initiative doc is active ("start fresh" or no XDRS scope):**
- Ask the user where to save the refined story (default: `userstory-NNN-slug.md` at workspace root).
- If split/deferred stories exist, use `vscode_askQuestions` to ask whether to add them to an existing epic initiative, create a new epic initiative, or save to `TODO.md` per `agentme-edr-001` (Phase 8). Apply the chosen action.

## Output Template

```
**Story ID:** userstory-NNN-slug

## Title
[required — <10 words, outcome-focused, e.g. "Add fraud-check endpoint for payment processing"]

## User Story
[required — <50 words]
As a [role], I want to [action], so that [benefit].

## Scope
[required — <200 words. List features, behaviors, screens, or services in scope with key characteristics and points of attention.]
- [feature or behavior — characteristic / point of attention]

## Edge Cases
[optional — <50 words. Known edge cases and how each should be handled.]
- [edge case — expected handling]

## Out of Scope
[optional — <30 words. What will not be touched; deferred to later or handled elsewhere.]
- [out-of-scope item]

## Constraints
[optional — <30 words. Any rule, technology, regulatory, or business constraint that must be respected.]
- [constraint]

## Detailed Specs
[Required when any API, integration, or data detail was discovered or Phase 5 examples were confirmed. Mark N/A if none.
 A story lacking sufficient detail here is not ready for implementation. Examples never replace API or data-contract details.]
- [External API / integration: endpoint, method, payload, auth, behavior]
- [Data field: type, format, valid values, meaning, constraints]
- [Doc link: URL or file path — what it covers]
- [Contact: name/role — what they own or can clarify]
- [Process rule or business constraint not captured in Constraints above]
- [Example: what it demonstrates — confirmed Phase 5 sample, verbatim; mark illustrative if not binding]

## Acceptance Criteria
[required — <50 words. Verifiable checklist confirming the story is done.]
- [ ] [verifiable outcome]

## Attachments
[highly desirable — screenshots, mockups, or diagrams illustrating the feature.]
- [attachment]

**Epic initiative:** [NNN-epic-slug.md](../NNN-epic-slug.md)
*(omit when no XDRS initiative doc is active)*
```
