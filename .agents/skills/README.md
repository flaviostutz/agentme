# .agents/skills

Symlinks that expose skills to agents (relative links, see `_core-adr-policy-018`).

| Link | Target |
|------|--------|
| `manage-investment-portfolio` | `../../.xdrs/_local/bdrs/finance/skills/manage-investment-portfolio` |
| `review` | `../../.xdrs/_core/adrs/principles/skills/review` |
| `write-xdrs-doc` | `../../.xdrs/_core/adrs/principles/skills/write-xdrs-doc` |

`manage-investment-portfolio` is created by hand because the skill is local (`_local` scope) and is not distributed through filedist. Recreate it with:

`ln -s ../../.xdrs/_local/bdrs/finance/skills/manage-investment-portfolio .agents/skills/manage-investment-portfolio`
