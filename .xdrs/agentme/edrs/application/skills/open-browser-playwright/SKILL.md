---
name: open-browser-playwright
description: >
  Mandatory foundation for all browser automation (agentme-edr-128). Opens a visible Microsoft Edge
  window on a per-session copy of the user's signed-in profile, confirms the SSO user (or skips the
  check with SKIP_SSO=true for public sites), opens the target page and prints a localhost CDP
  endpoint that callers attach to with Playwright. Use whenever a user or skill needs to open, show,
  browse, scrape or automate any web page, SSO-protected or public, and before any connector skill
  drives a browser.
metadata:
  author: flaviostutz
  version: "1.0.0"
  updated: 2026-09-24
---

## Overview

Browser automation on company sites fails with blank or incognito profiles: device-compliance checks (e.g. Intune Conditional Access) and SSO need the user's real signed-in Edge profile. Chromium refuses remote debugging on the real profile, so the script [scripts/open-browser.js](scripts/open-browser.js) works on a scratch copy of it, one per session name, created on first use and reused afterwards.

The script opens one visible Edge window with remote debugging bound to `127.0.0.1`. It checks that a user is signed in on the Entra ID My Account page (`https://myaccount.microsoft.com/?ref=MeControl`) or on `SSO_CHECK_URL`, opens the target page, and prints the result with the CDP endpoint. With `SKIP_SSO=true` it skips the sign-in check for public sites. The same script also reports sign-in problems, waits for a manual sign-in (`wait`) and closes leftover task tabs (`tidy`).

This skill is the only allowed way to open a browser for automation ([agentme-edr-128](../../128-browser-automation-foundation.md)). Connector skills run Step 1 with the port from their own `metadata.cdp-port`, then attach to the printed endpoint (Step 3) and run their own scripts. Ad-hoc use (a user asking to see a page, or a skill without a declared port) passes no port, and the script picks a free one in 9390-9399. Each session has its own profile copy and state file, so sessions with different names run side by side.

### Inputs

#### Required

- `url`: http(s) page to open

#### Optional

- `session`: session name (default: site name)
- `size`: `WIDTHxHEIGHT` (default `1300x900`)
- `--cdp-port`: caller's `metadata.cdp-port`, connectors only
- `SKIP_SSO=true`: public sites without sign-in
- `SSO_CHECK_URL`: https page showing the signed-in email
- `SSO_WAIT_SECONDS`: sign-in check timeout (default 45)
- Task to run on the opened page

### Outputs

#### Contents

- `RESULT`, `USER`, `SESSION`, `PAGE` and `CDP` lines
- Content extracted by the requested task

#### Changes

- One visible Edge window left open
- Per-session profile copy and state file (OS temp)

### Halt Conditions

- No target URL can be derived from the request
- Microsoft Edge or its profile not found
- User does not sign in within the wait

### User Interaction

- Sign in in the open window (exit 10)
- Choose how to check SSO (exit 11)

### Runtime Requirements

- Microsoft Edge, signed in for SSO sites
- Node.js 22+ with `npx`
- macOS or Linux; Windows is experimental

## Instructions

Start right away; don't explore the repo first. Script paths are relative to this skill's folder. Run each command on its own, not chained with others, and keep stderr visible.

### Question Checklist

Every question to the human MUST follow [`agentme-edr-003`](../../../principles/003-hitl-question-content.md):

- [ ] **01**: Title, then one context line stating what was found and the current state.
- [ ] **03**: 2-4 options, each stating what it does and its main consequence.
- [ ] **05**: Self-contained, with terms explained. Number batched questions (Q1, Q2) and ask at most 5 per round.
- [ ] **06**: Fill every question-UI field (header, question, message, option labels, option descriptions) with as much of the question and consequences as fits; condense before truncating. If anything was cut, also put the full question in chat first. Never reduce the UI to "see above".
- [ ] **07**: Phase gates summarise what was produced, open risks, and what each option causes next, in under 80 words.
- [ ] **08**: When the human asks for clarification, re-ask with more context (examples, files, impact) and never repeat the same wording.
- [ ] **11**: Use the template `Q<n>: <title>` / context / `- A: (recommended) <option>. <consequences>.` Keep the whole question under 140 words. Never apply a recommendation without the human's answer.

### Step 1: Open the browser

```sh
node scripts/open-browser.js <session> <url> [WIDTHxHEIGHT] [--cdp-port=<port>]
```

- Pass `--cdp-port` only from a connector, with its own `metadata.cdp-port` (9230-9389, [agentme-edr-128](../../128-browser-automation-foundation.md) rule 05). Without it, the script picks the lowest free port in 9390-9399.
- Prefix `SKIP_SSO=true` only for public sites that need no sign-in. Any other value keeps SSO mode.
- Session names match `[A-Za-z0-9_-]{1,32}`; `wait` and `tidy` are reserved.

It prints:

```text
RESULT: authenticated | opened | sign-in-required | sso-check-url-required
USER: <email> | skipped | none
SESSION: <session>
PAGE: [<title>](<url>)
CDP: http://127.0.0.1:<port>
```

If the session is already open on the same port (or no port was requested), the script reuses the window and opens the target in a new tab. A session open on a different port is closed and launched again on the requested one.

### Step 2: Handle the result

| Exit | Result | Action |
|---|---|---|
| 0 | `authenticated` / `opened` | Go to Step 3 |
| 2 | Edge or profile not found | Tell the user to install Edge and sign in once, or set `EDGE_PATH` / `EDGE_PROFILE_DIR`; halt |
| 3 | Browser failed to open (or no session for `wait`) | Report stderr; rerun Step 1 once, then halt |
| 4 | Port in use or held by another browser | See Edge Cases (port busy); never pick another skill's port |
| 5 | CDP endpoint did not answer | Rerun Step 1 once, then halt |
| 10 | `sign-in-required` | Ask the user to sign in (below), then run `wait` |
| 11 | `sso-check-url-required` | Ask the SSO check question (below) |
| 64 | Invalid arguments | Fix the command; never retry unchanged |

`authenticated` means a signed-in email was found on the check page's own host and the target then loaded without a sign-in title or identity-provider URL. `opened` (SKIP_SSO) means the page loaded. Both can still be wrong when a site shows a login form under a normal title, or an error page. When the content matters, take a snapshot after attaching to confirm.

**Exit 10**: tell the user which window and site need a sign-in, and ask them to sign in there. Do NOT close or relaunch the window. Then run:

```sh
node scripts/open-browser.js wait <session> <url> [seconds]
```

`wait` polls for the signed-in user (default 300s), then opens the target, keeping the session's port. It prints the same lines.

**Exit 11**: the Entra ID check found no user, and no `SSO_CHECK_URL` was set. The window is left on the Entra page. Ask one question, following the Question Checklist:

```text
Q1: How should the sign-in be checked for <site>?
The browser opened, but no signed-in Entra ID user was found on the Microsoft account page.
- A: (recommended) Sign in on the Microsoft page in the open window. The skill then continues with `wait`.
- B: Give a page of <site> that shows your signed-in email. The skill checks that page instead, for this run only.
```

For A, run `wait <session> <url>`. For B, run `SSO_CHECK_URL=<https page> node scripts/open-browser.js wait <session> <url>`. The URL is not saved anywhere.

### Step 3: Attach and run the task

Attach only to a `CDP:` endpoint the script printed in this task, and only if it is `http://127.0.0.1:<port>`. With playwright-cli, use a separate `<session>-attach` session:

```sh
npx --package=@playwright/cli@latest playwright-cli -s=<session>-attach attach --cdp=<CDP>
npx --package=@playwright/cli@latest playwright-cli -s=<session>-attach snapshot
```

Other common commands: `goto <url>`, `click <ref>`, `fill <ref> <text>`, `screenshot`, `eval "<js>"`, `tab-list`. With the Playwright Node API:

```js
const browser = await chromium.connectOverCDP(cdpUrl);
const context = browser.contexts()[0]; // the signed-in context
const page = await context.newPage();   // work in your own page
// ...
await page.close();                     // close only pages you opened
// never call browser.close()
```

If the endpoint stops answering, rerun Step 1 with the same session name and port, then attach again.

### Step 4: Finish

At the end of the whole task, the top-level agent tidies the session and detaches. Connectors called by it skip this step.

```sh
node scripts/open-browser.js tidy <session>
npx --package=@playwright/cli@latest playwright-cli -s=<session>-attach detach
```

`tidy` closes the tabs the task opened except the newest one, and keeps tabs that were open before the task. It prints `RESULT: tidied` (or `no-session`). Never run `close` or `Browser.close`: the window stays open until the user closes it.

## Examples

- "Show me https://example.com" → `SKIP_SSO=true node scripts/open-browser.js example https://example.com`; report the `PAGE` line, then `tidy example` and `detach`.
- "Open our internal wiki page" → `node scripts/open-browser.js wiki https://wiki.example.com/start`; on exit 10, ask the user to sign in and run `wait wiki https://wiki.example.com/start`.
- A connector with `cdp-port: "9231"` runs `node scripts/open-browser.js tickets https://tickets.example.com --cdp-port=9231`, then its own script calls `chromium.connectOverCDP('http://127.0.0.1:9231')`.

## Edge Cases

- **Why a profile copy**: Chromium refuses remote debugging on its real default user-data dir. The script copies `Default/` and `Local State` from the Edge user-data dir to `<tmp>/playwright-browser-<session>-profile`. It skips caches, `Service Worker`, `WebStorage`, lock files and session-restore files. Old copies MAY be deleted by hand when their session is closed.
- **Profile reuse and recovery**: an existing copy is reused as-is. The script re-creates it only when the browser fails to open on it, or the SSO check fails on it, and then retries once.
- **Restored tabs (security)**: session-restore files are never copied and are removed from the copy before each launch. Otherwise the user's real tabs, which hold live tokens, would reopen in the automation window. If an unrelated tab ever shows up, close it and delete `.playwright-cli/` snapshots captured while it was open.
- **Transient redirects**: SSO sites pass through `Sign In` and `Loading ...` pages before they land. The script keeps polling instead of judging the first title, and re-navigates every 5s while the tab is stuck on the check page.
- **Check page**: only an email found on the check page's own host counts, so a login or account-picker page listing the email never passes. `SSO_CHECK_URL` must be https with a plain host name.
- **Device compliance block** ("device not compliant"): the session is not using the copied profile. Always launch through this script, never with a blank profile.
- **macOS `Operation not permitted` or hidden window**: TCC can block access to the Edge profile when an agent spawns the process. Grant the parent app (e.g. VS Code) Full Disk Access and restart it.
- **Windows (experimental)**: Edge locks some files (e.g. cookies) while it runs. The script skips locked files with a warning; if SSO then fails, close Edge and rerun Step 1.
- **Port busy (exit 4)**: another process listens on the port, or a second session got the same port. Check it with `lsof -nP -iTCP:<port> -sTCP:LISTEN`, and list declared ports with `grep -rn "cdp-port:" --include=SKILL.md .`. Ask the user before stopping any process.
- **Parallel sessions**: different session names run side by side. Don't run Step 1 twice at the same time for the same session name.
- **Reuse keeps the window size**: a reused session keeps its size. Use playwright-cli `resize <w> <h>` after attaching.
- **CDP security**: while the port is open, any local process can act as the signed-in user. The endpoint is bound to `127.0.0.1`, printed only for this task, and stored only in the session's private state file.
- **Sensitive local files**: playwright-cli writes snapshots and logs to `.playwright-cli/` in the working directory. Keep it gitignored, and don't share request headers, which can hold access tokens.

## Anti-Patterns

- **Mistake:** A connector launching its own browser, copying the profile or calling `playwright-cli open`.
  **Why it happens:** Owning the browser looks simpler than depending on another skill.
  **Instead:** Run Step 1 with the connector's port, then attach in Step 3 ([agentme-edr-128](../../128-browser-automation-foundation.md) rules 02-03).
- **Mistake:** Pointing a browser at the real Edge profile directory.
  **Why it happens:** The real profile already holds the SSO cookies, so a copy looks redundant.
  **Instead:** Use the script's scratch copy. Chromium refuses CDP on the real profile.
- **Mistake:** Closing or relaunching the browser when a sign-in page appears.
  **Why it happens:** A login form looks like a failure to retry from scratch.
  **Instead:** Leave the window open, ask the user to sign in there, and run `wait`.
- **Mistake:** Ending the task with `playwright-cli close` or `browser.close()`.
  **Why it happens:** Cleaning up after yourself looks like good practice.
  **Instead:** Run `tidy`, then `detach`. The window stays open for the user.
- **Mistake:** Using `SKIP_SSO=true` to get past a failing sign-in.
  **Why it happens:** Skipping the check makes the command succeed.
  **Instead:** Use SKIP_SSO only for public sites. For SSO sites, follow Step 2.

## References

- [scripts/open-browser.js](scripts/open-browser.js) - opens the browser, checks SSO, waits and tidies tabs
- [agentme-edr-128](../../128-browser-automation-foundation.md) - browser automation foundation
- [agentme-edr-127](../../127-external-system-adapter-skills.md) - external system adapter skills
- [agentme-edr-003](../../../principles/003-hitl-question-content.md) - question content
- [agentme-edr-017](../../../principles/017-skill-testing.md) - skill testing
- [_core-adr-policy-003](../../../../../_core/adrs/principles/003-skill-standards.md) - skill standards
