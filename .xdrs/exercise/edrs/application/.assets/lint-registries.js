#!/usr/bin/env node
// Lints the exercise registries (exercise-edr-policy-102).
const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');

const dataDir = path.join(__dirname, '../../../adrs/data/.assets');
const errors = [];
const warnings = [];

const readJson = (file) => JSON.parse(fs.readFileSync(path.join(dataDir, file), 'utf8'));
const ajv = new Ajv({ allErrors: true });

function validate(schemaFile, data, label) {
  const schema = readJson(`schemas/${schemaFile}`);
  requireDescriptions(schema, schemaFile, '');
  const check = ajv.compile(schema);
  if (!check(data)) {
    for (const e of check.errors) errors.push(`${label}: ${e.instancePath} ${e.message}`);
  }
}

// every schema property must explain itself (exercise-adr-policy-202.02)
function requireDescriptions(node, file, where) {
  if (!node || typeof node !== 'object') return;
  for (const [name, prop] of Object.entries(node.properties || {})) {
    if (!prop.description) errors.push(`${file}: property ${where}${name} has no description`);
    requireDescriptions(prop, file, `${where}${name}.`);
    requireDescriptions(prop.items, file, `${where}${name}[].`);
  }
  requireDescriptions(node.items, file, where);
}

function findDuplicates(items, label) {
  const seen = new Set();
  for (const item of items) {
    if (seen.has(item.id)) errors.push(`${label}: duplicate id ${item.id}`);
    seen.add(item.id);
  }
}

const characteristics = readJson('characteristics.json');
const profiles = readJson('profiles.json');
const config = readJson('config.json');
validate('characteristic.schema.json', characteristics, 'characteristics.json');
validate('profile.schema.json', profiles, 'profiles.json');
validate('config.schema.json', config, 'config.json');

const questions = [];
const questionFiles = fs.readdirSync(path.join(dataDir, 'questions')).filter((f) => f.endsWith('.json'));
for (const file of questionFiles) {
  const list = readJson(`questions/${file}`);
  validate('question.schema.json', list, `questions/${file}`);
  if (Array.isArray(list)) list.forEach((q) => questions.push({ ...q, file }));
}

findDuplicates(characteristics, 'characteristics.json');
findDuplicates(profiles, 'profiles.json');
findDuplicates(questions, 'questions');

const charById = new Map(characteristics.map((c) => [c.id, c]));
const questionById = new Map(questions.map((q) => [q.id, q]));

for (const p of profiles) {
  for (const id of p.characteristics || []) {
    if (!charById.has(id)) errors.push(`profile ${p.id}: unknown characteristic ${id}`);
  }
}

function derivedDomain(q) {
  const known = (q.characteristics || []).filter((c) => charById.has(c.id));
  if (!known.length) return undefined;
  const top = known.reduce((best, c) => (Math.abs(c.weight) > Math.abs(best.weight) ? c : best));
  return charById.get(top.id).domain;
}

for (const q of questions) {
  for (const c of q.characteristics || []) {
    if (!charById.has(c.id)) errors.push(`question ${q.id}: unknown characteristic ${c.id}`);
  }
  const domain = derivedDomain(q);
  if (domain && `${domain}.json` !== q.file) {
    errors.push(`question ${q.id}: derived domain ${domain} does not match file ${q.file}`);
  }
  const [min, max] = q.answer === 'frequency' ? [0, 1] : [-1, 1];
  for (const r of q.routes || []) {
    if (!questionById.has(r.add)) errors.push(`question ${q.id}: route target ${r.add} does not exist`);
    if (r.add === q.id) errors.push(`question ${q.id}: routes to itself`);
    if (r.threshold < min || r.threshold > max) {
      errors.push(`question ${q.id}: threshold ${r.threshold} outside ${q.answer} range ${min}..${max}`);
    }
  }
}

// cycle detection (depth-first search with a recursion stack)
const state = new Map();
function visit(id, trail) {
  if (state.get(id) === 'done') return;
  if (state.get(id) === 'active') {
    errors.push(`route cycle: ${[...trail.slice(trail.indexOf(id)), id].join(' -> ')}`);
    return;
  }
  state.set(id, 'active');
  const q = questionById.get(id);
  for (const r of (q && q.routes) || []) if (questionById.has(r.add)) visit(r.add, [...trail, id]);
  state.set(id, 'done');
}
questions.forEach((q) => visit(q.id, []));

// reachability from discovery questions through routes
const reachable = new Set();
const stack = questions.filter((q) => q.type === 'discovery').map((q) => q.id);
while (stack.length) {
  const id = stack.pop();
  if (reachable.has(id)) continue;
  reachable.add(id);
  for (const r of (questionById.get(id) || {}).routes || []) stack.push(r.add);
}
for (const q of questions) {
  if (!reachable.has(q.id)) warnings.push(`question ${q.id}: not reachable from a discovery question`);
}

const usedChars = new Set(questions.flatMap((q) => (q.characteristics || []).map((c) => c.id)));
const profiledChars = new Set(profiles.flatMap((p) => p.characteristics || []));
const discoveryMain = new Set(
  questions
    .filter((q) => q.type === 'discovery' && (q.characteristics || []).length)
    .map((q) => q.characteristics.reduce((best, c) => (Math.abs(c.weight) > Math.abs(best.weight) ? c : best)).id)
);
for (const c of characteristics) {
  if (!usedChars.has(c.id)) warnings.push(`characteristic ${c.id}: no question`);
  if (!profiledChars.has(c.id)) warnings.push(`characteristic ${c.id}: not listed in any profile`);
  if (profiledChars.has(c.id) && !discoveryMain.has(c.id)) {
    warnings.push(`characteristic ${c.id}: no discovery question has it as main characteristic`);
  }
}

warnings.forEach((w) => console.warn(`warn: ${w}`));
errors.forEach((e) => console.error(`error: ${e}`));
console.log(
  `exercise registries: ${characteristics.length} characteristics, ${profiles.length} profiles, ` +
    `${questions.length} questions, ${errors.length} errors, ${warnings.length} warnings`
);
process.exit(errors.length ? 1 : 0);
