# Demo Script: JSON Validator Planning Session

## Setup

- Open VS Code with an empty folder
- Open a Copilot chat ready for `/plan`
- Open a terminal in the same folder

---

## Initial prompt

```
/plan
I need a Node.js script that reads a JSON file from disk and tells me if it's valid.
```

---

## Planning prompts — use these to drive the session with the audience

Each prompt is a round. After each response, pause and discuss with the audience before sending the next.

```
check for more features I would probably need but that are not part of the plan. ask questions
```

```
what happens if the file doesn't exist? ask questions
```

```
dry run if I send a file with 10GB in size
```

```
what happens if we have 10 million files?
```

```
explore if all types of input would work with this utility
```

```
is the plan doing everything we asked in the beginning?
```

```
how are you making sure those things are implemented correctly?
```

```
verify all references in the plan. ask questions
```

```
check for edge cases we didn't discuss yet. ask questions
```

```
check for consistency and ask questions
```

```
show me a diagram explaining the overall feature structure
```

```
show a diagram from the user perspective
```

```
explain to me what this utility does
```

```
how could I distribute this utility?
```

```
can we simplify anything?
```

```
check for consistency and ask questions
```

```
check for consistency and ask questions
```

```
check for consistency and ask questions
```

---

## Scope vote (after the first 2-3 rounds)

Ask the audience: **"Which of these should we include? Which should we leave out?"**

Suggested scope: CLI binary, JSON format only, relative path, exit 0/1, stderr.
Out of Scope: schema validation, stdin, multiple files, distribution.

---

## Implementation

Once the plan is converged and scoped:

- `index.js` — CLI entry point + validator using `fs` and `JSON.parse`
- `index.test.js` — 3 cases with `node:test` + `node:assert`

```sh
node --test
echo '{"ok":true}' > valid.json && node index.js valid.json; echo exit: $?
echo 'not json' > bad.json && node index.js bad.json; echo exit: $?
```

---

## Fallback

**If `/plan` doesn't ask questions**: send `"check for consistency and ask questions"` and the planning rounds will start naturally.

**If `node --test` fails**: teaching moment for Concept 5 — the verification step caught what the plan missed.
