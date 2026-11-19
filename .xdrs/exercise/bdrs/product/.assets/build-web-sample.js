#!/usr/bin/env node
'use strict';
// Rebuilds the GENERATED regions of web-ui-functional-sample.html: the shared engine module and the registries
// (exercise-adr-policy-102.02-shared-engine-module, 102.05-registries-bundled-and-checked).
// Usage: node build-web-sample.js [--check]   (--check only reports whether the file is up to date)
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.join(__dirname, '../../..');
const engineFile = path.join(root, 'edrs/application/skills/test-question-bank/scripts/engine.js');
const lintFile = path.join(root, 'edrs/application/.assets/lint-registries.js');
const target = path.join(__dirname, 'web-ui-functional-sample.html');

const lint = spawnSync(process.execPath, [lintFile], { encoding: 'utf8' });
if (lint.status !== 0) {
  console.error(`Registry lint failed, the web sample is not built:\n${lint.stdout}${lint.stderr}`);
  process.exit(1);
}

const { loadRegistry } = require(engineFile);
const registry = loadRegistry();
delete registry.dir;
const safe = (text) => text.replace(/<\/(script)/gi, '<\\/$1').replace(/<!--/g, '<\\!--');
const regions = {
  engine: `<script>\n${safe(fs.readFileSync(engineFile, 'utf8'))}</script>`,
  registry: `<script>\nwindow.EXERCISE_REGISTRY = ${safe(JSON.stringify(registry))};\n</script>`
};

let html = fs.readFileSync(target, 'utf8');
for (const [name, content] of Object.entries(regions)) {
  const re = new RegExp(`(<!-- GENERATED:${name}:BEGIN -->\\n)[\\s\\S]*?(\\n?<!-- GENERATED:${name}:END -->)`);
  if (!re.test(html)) { console.error(`marker ${name} not found in ${path.basename(target)}`); process.exit(1); }
  html = html.replace(re, (_, a, b) => `${a}${content}\n${b.replace(/^\n/, '')}`);
}

if (process.argv.includes('--check')) {
  const same = fs.readFileSync(target, 'utf8') === html;
  console.log(same ? 'web sample is up to date' : 'web sample is out of date: run build-web-sample.js');
  process.exit(same ? 0 : 1);
}
fs.writeFileSync(target, html);
console.log(`built ${path.basename(target)}: ${registry.questions.length} questions, ${registry.characteristics.length} characteristics, ${registry.profiles.length} profiles`);
