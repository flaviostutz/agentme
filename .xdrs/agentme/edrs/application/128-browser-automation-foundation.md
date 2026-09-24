---
name: agentme-edr-policy-128-browser-automation-foundation
description: Makes open-browser-playwright the single entry point for all browser automation, defines how connector skills attach to its CDP endpoint with their own port, how the endpoint is handled and where browser or SSO fixes go. Use when writing or running any skill or agent that opens, drives or attaches to a web browser.
apply-to: All skills and agents that open, drive or attach to a web browser, in every scope that follows agentme
valid-from: 2026-09-24
---

# agentme-edr-policy-128: Browser automation foundation

## Context and Problem Statement

Connector skills that each open a browser their own way duplicate profile copies, CDP setup and SSO workarounds, which drift apart and break. How should skills and agents get a signed-in browser, and where do browser fixes live?

## Decision Outcome

**Single foundation skill with CDP attach**

Every browser session MUST be opened by the open-browser-playwright foundation skill; connector skills pass their own CDP port, then attach to the printed localhost CDP endpoint and run their own scripts.

### Details

Definitions: the **foundation** is [open-browser-playwright](skills/open-browser-playwright/SKILL.md); a **connector** is any skill that drives a browser to integrate with a system (see [agentme-edr-127](127-external-system-adapter-skills.md)); an **ad-hoc session** is a browser opened for a user or a skill without a declared port; an **attach session** is the automation client connected to the foundation's CDP endpoint.

#### 01-foundation-skill-mandatory

Any skill or agent that needs a browser, for scraping integrations or for showing a page to the user, on SSO-protected or public sites, MUST open it with the foundation before any navigation or content extraction.

- SSO mode is the default. `SKIP_SSO=true` MAY be used only for sites known to need no sign-in.
- A skill from a locked or external scope (e.g. `_core`) that needs a browser MUST run on a browser opened through the foundation. The locked skill MUST NOT be edited to do so.
- A skill that drives a browser, or calls a connector that does, MUST list the foundation in its `## References`.
- A consuming scope MAY replace the foundation only through an explicit policy of its own that names the replacement skill and declares the override in its `## Conflicts` section.

---

#### 02-connectors-call-foundation-then-attach

A connector MUST call the foundation with its own session name and exactly the port declared in its `metadata.cdp-port` (rule 05), wait until the foundation prints its result, then attach to the printed `CDP:` endpoint and run its own scripts there. It MUST attach with `playwright-cli -s=<session>-attach attach --cdp=<endpoint>` or the Playwright Node API `chromium.connectOverCDP(<endpoint>)`. Using the Node API this way needs no `## Conflicts` section.

Ad-hoc use and locked skills call the foundation without a port and attach the same way to the auto-picked endpoint it prints.

---

#### 03-no-duplicate-browser-setup

Skills and agents other than the foundation MUST NOT launch a browser (`spawn`, `playwright-cli open`, `chromium.launch`), copy or point at a browser profile, use a blank or incognito profile, or kill browser processes. They MUST drive the browser only through a CDP attach to an endpoint the foundation printed in the same task.

---

#### 04-foundation-owns-browser-tweaks

Profile, SSO, window, CDP and tab workarounds that apply to more than one site MUST be made in the foundation skill or its scripts, not in a connector. Site-specific page handling (e.g. a site's own login button) MAY stay in the connector.

---

#### 05-cdp-port-declaration

A skill that drives a browser MUST declare one quoted port as `cdp-port` under `metadata:` in its SKILL.md frontmatter (e.g. `cdp-port: "9231"`).

- The port MUST be in the range 9230-9389 and unique across all skills in every scope. Before choosing one, the author MUST search all `SKILL.md` files for `cdp-port:` and take the lowest unused port.
- The range 9390-9399 is reserved for sessions opened without `--cdp-port`; the foundation picks the lowest free port there. Skills MUST NOT declare it.
- The foundation itself declares no port.

---

#### 06-cdp-endpoint-handling

- Every foundation session MUST expose its CDP endpoint bound to `127.0.0.1` only. Connectors MUST reject non-localhost endpoints.
- The endpoint MUST NOT be persisted, forwarded or logged outside the running task. The foundation's private per-session state file is the only exception.
- The browser window MUST stay visible so the user can follow and intervene.
- Connectors MUST close only the pages they opened, including tabs the browser opens because of their actions (e.g. popups), and MUST NOT close the browser.
- At the end of the task, the top-level agent MUST run the foundation's `tidy` subcommand and end its attach session with `detach`, never `close`. The window stays open until the user closes it.

---

#### 07-vendor-cli-logins-exempt

Vendor CLI login flows that open a browser on their own (e.g. `az login`, `gh auth login`) MAY follow their own login procedure; rules 01-06 do not apply to them.

---

#### Testing

The foundation is verified by its `SKILL.test.md` per [agentme-edr-017](../principles/017-skill-testing.md) and by the offline unit tests of its script helpers per [agentme-edr-122](122-unit-test-requirements.md). Connectors verify rule 02 in their own `SKILL.test.md` with at least one assertion that they attach to the printed endpoint and never launch or close the browser.

## References

- [open-browser-playwright](skills/open-browser-playwright/SKILL.md) - the foundation skill
- [agentme-edr-127](127-external-system-adapter-skills.md) - external system adapter skills
- [agentme-edr-017](../principles/017-skill-testing.md) - skill testing
