'use strict';
// Rebuilds the GENERATED regions of web-ui-functional-sample.html: the shared engine module and the registries.
// It first runs the registry lint and stops when it fails.
// Usage: node build-web-sample.js [--check]   (--check only reports whether the file is up to date)
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.join(__dirname, '../../..');
const sample = path.join(__dirname, 'web-ui-functional-sample.html');
const engineFile = path.join(root, 'edrs/application/skills/test-question-bank/scripts/engine.js');
const lintFile = path.join(root, 'edrs/application/.assets/lint-registries.js');
const check = process.argv.includes('--check');

const lint = spawnSync(process.execPath, [lintFile], { encoding: 'utf8' });
if (lint.status !== 0) {
  process.stderr.write(`${lint.stdout}${lint.stderr}`);
  console.error('registry lint failed: the web sample was not built');
  process.exit(1);
}

const { loadRegistry } = require(engineFile);
const { config, characteristics, profiles, questions } = loadRegistry();
// "<" is escaped so that no text in the registries can end the inline script
const registry = JSON.stringify({ config, characteristics, profiles, questions }).replace(/</g, '\\u003c');
const engine = fs.readFileSync(engineFile, 'utf8').replace(/\n+$/, '');

const regions = {
  engine: `<script>\n${engine}\n</script>`,
  registry: `<script>\nwindow.EXERCISE_REGISTRY = ${registry};\n</script>`,
};

const before = fs.readFileSync(sample, 'utf8');
let html = before;
for (const [name, body] of Object.entries(regions)) {
  const re = new RegExp(`(<!-- GENERATED:${name}:BEGIN -->\\n)[\\s\\S]*?(\\n?<!-- GENERATED:${name}:END -->)`);
  if (!re.test(html)) { console.error(`GENERATED:${name} markers not found in ${path.basename(sample)}`); process.exit(1); }
  html = html.replace(re, (m, a, b) => `${a}${body}\n${b.replace(/^\n/, '')}`);
}

if (check) {
  console.log(html === before ? 'web sample is up to date' : 'web sample is out of date: run build-web-sample.js');
  process.exit(html === before ? 0 : 1);
}
fs.writeFileSync(sample, html);
console.log(`built ${path.basename(sample)}: ${questions.length} questions, ${characteristics.length} characteristics, ${profiles.length} profiles`);
