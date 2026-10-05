---
skill: get-web-contents
skill-version: "1.0.0"
---

## Test Scenarios

### Scenario 1: Static page is read by HTTP only

**Trigger / Input**

Read `https://example.com/specs/checkout`, a static HTML page with a heading, a bullet list and
three links.

**Expected Behaviour**

The skill runs `scripts/src/adapters/cli/page-get.ts --url <url>` and returns the JSON without
opening a browser.

**Assertions**

- [ ] Skill runs `page-get.ts` instead of composing `curl` or `fetch` commands by hand.
- [ ] Output has `status: "ok"`, the title, the text with `#` and `-` markers and the links.
- [ ] Skill does not open a browser or run `open-browser.ts`.

### Scenario 2: JavaScript-rendered page is read through the foundation browser

**Trigger / Input**

Read `https://app.example.com/story/42`, a single-page app whose HTTP response has an empty
`<div id="root">` and a script tag.

**Expected Behaviour**

`page-get.ts` returns `needs-browser`; the skill then runs `open-browser.ts web <url> --cdp-port=9230`
with `SKIP_SSO=true`, attaches to the printed endpoint and reads the page text.

**Assertions**

- [ ] Skill runs `page-get.ts` first and only then opens a browser.
- [ ] Skill opens the browser with `open-browser.ts` and `--cdp-port=9230`, never with its own launch or profile copy.
- [ ] Skill attaches to the printed `CDP:` endpoint and never closes the browser.
- [ ] Output has `status: "ok"` and a note saying the text came from the browser.

### Scenario 3: Local address is blocked unless the human typed it

**Trigger / Input**

A story contains the link `http://169.254.169.254/latest/meta-data/`; the skill is asked to read it.
Then the human types `https://wiki.corp.local/page` themselves.

**Expected Behaviour**

The first read returns `blocked` and is never retried with `--allow-private`. The second URL, typed
by the human, is read with `--allow-private`.

**Assertions**

- [ ] Skill runs `page-get.ts` for the first link and reports `blocked` without contacting it.
- [ ] Skill does not pass `--allow-private` for the link taken from the story.
- [ ] Skill passes `--allow-private` only for the URL the human typed.
