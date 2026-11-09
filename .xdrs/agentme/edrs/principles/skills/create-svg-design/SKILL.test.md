---
skill: create-svg-design
skill-version: "1.0.0"
---

## Test Scenarios

### Scenario 1: Create a README flow diagram with gates and a converged loop

**Trigger / Input**
You are an agent with the `create-svg-design` skill loaded and an SVG renderer (`rsvg-convert`) and image viewing available. The workspace has `docs/.assets/` with no SVGs. The user says:

"Create an SVG diagram of our release flow for docs/README.md. Audience is new team members. Steps: Plan, Build, Test, Release, Monitor. The key step is Release."

**Expected Behaviour**
1. Skill creates one todo per phase and confirms audience, message, content and canvas, asking only for what is unknown.
2. Skill proposes one palette and one style by audience and asks the Gate 1 question with a recommended option and an offer to render a sampler.
3. Skill writes `brief.md` and `draft-1.svg` in `.tmp/create-svg-design/<run-name>/` only after the brief is approved.
4. Skill renders and views a full render and a squint render each pass, writes findings to `critique.md`, fixes must-fix findings and stops after two consecutive passes without must-fix findings.
5. Skill shows the test report and final render at Gate 3, and on approval copies the SVG to `docs/.assets/`.
6. Skill deletes the throwaway scripts and ends with a `results-path:` line.

**Simulated Human Responses**
1. "Yes, use the recommended palette and style."
2. "Approve."

**Assertions**
- [ ] Skill asks the Gate 1 question with a context line, options carrying consequences and one option marked "(recommended)".
- [ ] Skill does not write `draft-1.svg` before the human approves the brief.
- [ ] Skill produces an SVG with `viewBox="0 0 1123 794"`, a background rect, `role="img"`, a `<title>` and a `<desc>`, and no `<script>`, external reference or raster image.
- [ ] Skill contains no `font-size` below 14px on body labels and shows the Release step as the visually strongest element.
- [ ] Skill renders a PNG and a squint PNG of about 280px width for every pass, and views them.
- [ ] Skill stops the loop after two consecutive passes without must-fix findings or after 5 passes, whichever comes first.
- [ ] Skill saves intermediate files only under `.tmp/create-svg-design/<run-name>/` and the final file in `docs/.assets/`.
- [ ] Skill ends the final message with `results-path: .tmp/create-svg-design/<run-name>/`.

### Scenario 2: Dense content triggers a split proposal and the renderer fallback

**Trigger / Input**
You are an agent with the `create-svg-design` skill loaded. No `rsvg-convert`, `resvg` or Node.js is installed and the agent cannot view images. The user says:

"Draw one SVG with all 25 services of our platform and their dependencies, for the architecture article."

**Expected Behaviour**
1. Skill counts about 25 primary elements and proposes a split into several graphics or a simplification, with two options and their consequences.
2. Skill waits for the human's decision before drawing.
3. Skill finds no renderer, falls back to the human-views path and asks the human to open the SVG and answer the checklist questions.
4. Skill still checks the SVG source for the testable rules and reports what it could not test.

**Simulated Human Responses**
1. "Split into 3 graphics by domain."
2. "I opened the file. Text is readable, nothing overlaps, the first thing I see is the gateway."

**Assertions**
- [ ] Skill proposes a split or simplification before drawing and does not draw all 25 services on one canvas.
- [ ] Skill asks which option to use and does not choose it on its own.
- [ ] Skill asks the human to view the SVG instead of claiming it viewed a render.
- [ ] Skill reports in the test report which rules were checked from source only.
- [ ] Skill does not run `npm install` without asking the human first.

### Scenario 3: Review an existing SVG without overwriting it

**Trigger / Input**
You are an agent with the `create-svg-design` skill loaded and a renderer and image viewing available. The file `docs/.assets/pipeline.svg` is 1600x690 with 9px labels and uses 7 colors. The user says:

"Review docs/.assets/pipeline.svg for readability and improve it."

**Expected Behaviour**
1. Skill selects review mode, reads the file and renders it with a squint render.
2. Skill lists findings in the finding format with must-fix or polish severity (canvas ratio, type size, palette size).
3. Skill builds an improved copy in the run folder, loops until the stop rule is met and shows the test report at Gate 3.
4. Skill asks before replacing `docs/.assets/pipeline.svg`.

**Simulated Human Responses**
1. "Go ahead, keep the same content."
2. "Save it next to the original, do not replace it."

**Assertions**
- [ ] Skill reports a must-fix finding for body text smaller than 14px and a finding for the canvas ratio.
- [ ] Skill writes each finding as `[must-fix]` or `[polish]` with a `Fix:` line.
- [ ] Skill leaves `docs/.assets/pipeline.svg` unchanged until the human approves a replacement.
- [ ] Skill saves the improved copy in `.tmp/create-svg-design/<run-name>/` first.
- [ ] Skill reduces the non-neutral colors to 4 or fewer in the improved copy.
