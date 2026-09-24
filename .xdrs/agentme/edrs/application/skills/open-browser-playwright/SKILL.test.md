---
skill: open-browser-playwright
skill-version: "1.0.0"
---

## Test Scenarios

### Scenario 1: Public page with SKIP_SSO, auto-picked port, tidy and detach

**Trigger / Input**

"Show me https://example.com and read its heading." No skill port is involved. Ports 9390-9399 are free.

**Expected Behaviour**

The agent runs `SKIP_SSO=true node scripts/open-browser.js example https://example.com` without `--cdp-port`. The script launches Edge on the scratch profile copy, skips the SSO check, and prints `RESULT: opened`, `USER: skipped` and `CDP: http://127.0.0.1:9390`, exiting 0. The agent attaches with `playwright-cli -s=example-attach attach --cdp=http://127.0.0.1:9390`, reads the heading from a snapshot, then runs `tidy example` followed by `detach`.

**Assertions**

- [ ] Agent calls `scripts/open-browser.js` with `SKIP_SSO=true` and no `--cdp-port`.
- [ ] Script prints a `CDP:` endpoint on `127.0.0.1` with a port in 9390-9399.
- [ ] Agent attaches to the printed endpoint with a separate `<session>-attach` session.
- [ ] Agent ends with `tidy <session>` and `detach`, and never runs `close` or `browser.close()`.

### Scenario 2: Connector with its own CDP port attaches to the foundation

**Trigger / Input**

A connector skill declares `cdp-port: "9231"` in its metadata and needs the SSO-protected page `https://tickets.example.com/queue`. The user is already signed in to Edge.

**Expected Behaviour**

The connector runs `node scripts/open-browser.js tickets https://tickets.example.com/queue --cdp-port=9231`. The script confirms the Entra ID user, opens the target, prints `RESULT: authenticated` and `CDP: http://127.0.0.1:9231`, and exits 0. The connector's own script then calls `chromium.connectOverCDP('http://127.0.0.1:9231')`, opens its own page, extracts the data and closes only that page.

**Assertions**

- [ ] Connector passes exactly its declared `--cdp-port=9231` to the foundation script.
- [ ] Connector attaches to the printed `CDP:` endpoint and never launches a browser, copies a profile or calls `playwright-cli open`.
- [ ] Connector closes only the pages it opened and never closes the browser.

### Scenario 3: No user found on the Entra page (exit 11)

**Trigger / Input**

"Open https://portal.example.com." The site uses a non-Microsoft identity provider, so the Entra ID check finds no user. `SSO_CHECK_URL` is not set.

**Expected Behaviour**

The script leaves the window on the Entra page and exits 11 with `RESULT: sso-check-url-required`. The agent keeps the window open and asks one question following the Question Checklist: a title, a context line saying no Entra ID user was found, option A (recommended) to sign in in the open window and option B to give a page that shows the signed-in email, each with its consequence. After the answer, it runs the matching `wait` command.

**Assertions**

- [ ] Agent does not close or relaunch the browser after exit 11.
- [ ] Agent asks exactly one question with a context line, a consequence for each option, and "(recommended)" on one option, and fills the question-UI fields instead of "see above".
- [ ] Agent waits for the human's answer before running `wait`, and passes `SSO_CHECK_URL` only when option B is chosen.
