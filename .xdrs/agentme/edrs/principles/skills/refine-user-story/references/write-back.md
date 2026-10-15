# Write-back to the source (step 6)

Detail for the write-back in step 6 of `refine-user-story`. Runs only when the story came from a
GitHub issue or an Azure DevOps work item and the story is saved locally. Public web pages have no
write-back.

## Offer

Ask with `vscode_askQuestions`: "Update the source item" (recommended) or "Keep the story local
only". Choosing local only ends the write-back after local tracking.

## What is written

1. **Original saved as a comment**: title and body as read, prefixed with "Original text before
   refinement (<date>):". Skill `change-<provider>-contents`, resource `issue-comment-create`
   (`{issueUrl, body}`) or `work-item-comment-create` (`{workItemUrl, body}`).
2. **Title and body updated**: the story's `## Title` becomes the title. The body is the whole
   story (every template section except `## Title`, the `**Story ID:**` line and the
   `**Epic initiative:**` line). Resource `issue-update` with `expectedUpdatedAt` set to the
   value read in step 1, or `work-item-update` with `expectedRev` set to the `rev` read in
   step 1 (use `bodyField` `Microsoft.VSTS.TCM.ReproSteps` for bugs). A result starting `stale:`
   means the item changed during refinement: stop, re-read the item, show what changed, and ask
   how to proceed. Never overwrite.
3. **One placeholder per deferred slice**: resource `issue-create` (`{repoUrl, title, body}`) or
   `work-item-create` (`{workItemUrl: <source>, type, title, body, areaPath, iterationPath}`
   with the source's own type, area and iteration). Title `[NEEDS REFINING] <slice title>`. Body
   holds the split context (objective, scope, context, split rationale) and a line
   "Split from <source URL>". No labels, no assignee. The refined item gets no link to the
placeholders". Rerunning the write-back returns `already-present` for slices already created.

Run the three steps in this order, one `change-<provider>-contents` run each. If step 1 fails,
do not run step 2.

## Confirmation

Stage 1 (before composing items) shows: System (`<owner>/<repo>#<n>` or
`<org>/<project>` work item `#<id>`), the three operations, old and new title, body length,
the placeholder titles, the source's visibility, and whether the body includes a Pending Questions
section with Open Questions (roles only). Add these warnings when they apply: the
source is closed, locked or archived; the type is Epic or Feature. When visibility is public
or `unknown`, add an explicit option "Publish to the public source" and treat any other answer
as a decline. Stage 2 (before running) lists the final items. Both follow
`change-<provider>-contents` Confirmation.

## Local tracking (always, even when write-back is declined or fails)

- Initiative active: placeholder files and links per `story-template-and-persistence.md`; add
  the source URL and the created placeholder URL to the story or placeholder file under a
  `## Source` section.
- No initiative: one `TODO.md` entry per deferred slice per `agentme-edr-001`; its `prompt`
  equals the placeholder body, and `dev notes` carries the source URL and the placeholder URL.

## Reporting

List each result (`verified`, `already-present`, `error`) with its URL. Report any other status
or exit code 1 to the human and never claim a write that was not `verified`.
