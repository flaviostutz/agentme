#!/usr/bin/env node
'use strict';
// Question bank tests for the exercise questionnaire (exercise-edr-policy-103).
// Usage: node run.js [--only per-profile,all-profiles,alpha,stress] [--n-profile 200] [--n-all 500] [--n-alpha 1000]
//        [--n-stress 500] [--seed 1] [--registry <dir>] [--out <dir>] [--name <run-name>]
// Writes report.md and results.json in the run folder, prints the failed and warning checks, exits 1 when any check FAILs.
const fs = require('fs');
const path = require('path');
const { loadRegistry } = require('./engine');
const tests = require('./tests');

const args = {};
for (let i = 2; i < process.argv.length; i++) {
  const a = process.argv[i];
  if (a.startsWith('--')) args[a.slice(2)] = process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[++i] : 'true';
}
const only = (args.only || 'per-profile,all-profiles,alpha,stress').split(',');
const seed = +(args.seed || 1);
const N = { 'per-profile': +(args['n-profile'] || 200), 'all-profiles': +(args['n-all'] || 500), alpha: +(args['n-alpha'] || 1000), stress: +(args['n-stress'] || 500) };
const FN = { 'per-profile': tests.perProfile, 'all-profiles': tests.allProfiles, alpha: tests.alpha, stress: tests.stress };
for (const o of only) if (!FN[o]) { console.error(`unknown test ${o}; use ${Object.keys(FN).join(', ')}`); process.exit(2); }

const reg = loadRegistry(args.registry);
const stamp = new Date().toISOString().replace(/\D/g, '').slice(0, 14);
const base = args.out || path.join(process.cwd(), '.tmp', 'test-question-bank');
let name = args.name || stamp, dir = path.join(base, name), k = 2;
while (fs.existsSync(dir)) dir = path.join(base, `${name}-${k++}`);
fs.mkdirSync(dir, { recursive: true });

const md = [`# Question bank test report`, '', `Registry: ${reg.dir}`, `Bank: ${reg.questions.length} questions, ${reg.characteristics.length} characteristics, ${reg.profiles.length} profiles (${reg.profiles.map((p) => p.id).join(', ')}) | seed ${seed}`, 'Respondents are simulated from the registry itself: the tests check keying, weights, routes and measurement, not the wording or real-world validity.', ''];
const checks = [], results = {};
for (const o of only) {
  const t0 = Date.now();
  console.error(`running ${o} (${N[o]} people)...`);
  const r = FN[o](reg, { n: N[o], seed });
  results[o] = r.data; checks.push(...r.checks);
  md.push(...r.md);
  console.error(`  done in ${((Date.now() - t0) / 1000).toFixed(0)}s, ${r.checks.filter((c) => c.level === 'FAIL').length} FAIL, ${r.checks.filter((c) => c.level === 'WARN').length} WARN`);
}
const fails = checks.filter((c) => c.level === 'FAIL'), warns = checks.filter((c) => c.level === 'WARN');
const verdict = fails.length ? 'FAIL' : 'PASS';
const list = (c) => `- ${c.level} [${c.test}] ${c.text}`;
md.splice(6, 0, '## Result', '', `Outcome: ${verdict} (${fails.length} FAIL, ${warns.length} WARN)`, '', ...(checks.length ? checks.map(list) : ['No findings.']), '');
fs.writeFileSync(path.join(dir, 'report.md'), md.join('\n') + '\n');
fs.writeFileSync(path.join(dir, 'results.json'), JSON.stringify({ outcome: verdict, seed, n: N, tests: only, checks, results }, null, 1));

console.log(`Outcome: ${verdict} (${fails.length} FAIL, ${warns.length} WARN)`);
checks.forEach((c) => console.log(list(c)));
console.log(`results-path: ${path.relative(process.cwd(), dir) || '.'}/`);
process.exit(fails.length ? 1 : 0);
