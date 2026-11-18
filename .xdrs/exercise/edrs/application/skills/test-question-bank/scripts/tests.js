'use strict';
// The four question bank tests. Each returns { md, checks, data }; checks are { level: 'FAIL'|'WARN', test, text }.
const { createEngine } = require('./engine');
const S = require('./population');
const { mean, sd, corr, rmse, pctl, share, LEVELS } = S;

// Thresholds are defined by exercise-edr-policy-103. Keep this table and the Policy equal.
const T = {
  perProfile: { levelCorr: 0.85, withinOne: 0.95, goodEnough: 0.8, measured: 0.9, charBias: 0.15 },
  allProfiles: { profileCorr: 0.9, profileBias: 0.1, falseHigh: 0.05, charBias: 0.15 },
  alpha: { min: 0.7, max: 0.9, minItems: 3, minPairs: 30, noise: 1.5 },
  stress: { identified: 0.8, falseAlarm: 0.1, invalidFlagged: 0.5, neurotypicalHigh: 0.1, honestMae: 0.15 },
};

const f2 = (x) => (Number.isFinite(x) ? (x >= 0 ? ' ' : '') + x.toFixed(2) : '  n/a');
const pct = (x) => (Number.isFinite(x) ? `${(100 * x).toFixed(0)}%` : 'n/a');
const table = (head, rows) => [`| ${head.join(' | ')} |`, `|${head.map(() => '---').join('|')}|`, ...rows.map((r) => `| ${r.join(' | ')} |`), ''];
const levelNames = Object.keys(LEVELS);
const sessionLen = (people) => { const q = people.map((p) => p.res.answers.length); return `${mean(q).toFixed(0)} (p5 ${pctl(q, 0.05)}, p95 ${pctl(q, 0.95)})`; };

function levelRecovery(groups) { // groups: one array of scores per ordered level
  const ms = groups.map(mean);
  const cuts = ms.slice(0, -1).map((m, i) => (m + ms[i + 1]) / 2);
  let ex = 0, w1 = 0, tot = 0;
  groups.forEach((a, i) => a.forEach((v) => { const c = cuts.filter((t) => v >= t).length; tot++; if (c === i) ex++; if (Math.abs(c - i) <= 1) w1++; }));
  const lv = groups.flatMap((a, i) => a.map(() => i));
  return { corr: corr(lv, groups.flat()), exact: ex / tot, withinOne: w1 / tot, means: ms };
}

// ---------------------------------------------------------------- 1. each Profile alone
function perProfile(reg, { n, seed }) {
  const md = ['## 1. Each profile alone', '', `Only the characteristics of one profile are asked and judged. ${n} simulated people per profile, level none/low/medium/high in equal shares, the other profiles at none.`, ''];
  const checks = [], data = {};
  const summary = [];
  for (const p of reg.profiles) {
    const eng = createEngine(reg, { scope: p.id });
    const people = [];
    for (let i = 0; i < n; i++) {
      const lvl = levelNames[i % levelNames.length];
      const person = S.simplePerson({ profiles: reg.profiles, chIds: eng.chIds, nominal: reg.profiles.map((x) => (x.id === p.id ? LEVELS[lvl] : 0)), seed: seed + i });
      const res = eng.runSession(person.answer);
      people.push({ lvl, person, res, pr: eng.profileResults(res.st, eng.PEVAL, res.answers)[0] });
    }
    const scored = people.filter((x) => x.pr.score !== null);
    const groups = levelNames.map((l) => scored.filter((x) => x.lvl === l).map((x) => x.pr.score));
    const rec = levelRecovery(groups);
    const good = share(people, (x) => x.res.goodAt !== null);
    const rows = p.characteristics.map((c) => {
      const items = eng.BANK.filter((q) => q.main.id === c).length;
      const sc = people.filter((x) => x.res.st[c].score !== null);
      const bias = mean(sc.map((x) => x.res.st[c].score - x.person.stance[c]));
      return { c, items, answers: mean(people.map((x) => x.res.st[c].n)), measured: share(people, (x) => x.res.st[c].n >= eng.CFG.min_answered), settled: share(people, (x) => x.res.st[c].state !== 'open'), bias, corr: corr(sc.map((x) => x.res.st[c].score), sc.map((x) => x.person.stance[c])) };
    });
    md.push(`### ${p.id} (${p.characteristics.length} characteristics, ${eng.BANK.length} questions in scope)`, '');
    md.push(`Questions asked ${sessionLen(people)} | good enough reached ${pct(good)} | score vs level: correlation ${rec.corr.toFixed(3)}, level correct ${pct(rec.exact)}, within one ${pct(rec.withinOne)}`, '');
    md.push(...table(['level', 'n', 'mean score', 'sd'], levelNames.map((l, i) => [l, String(groups[i].length), f2(rec.means[i]), sd(groups[i]).toFixed(2)])));
    md.push(...table(['characteristic', 'main items', 'answers', 'measured', 'settled', 'bias vs truth', 'corr'], rows.map((r) => [r.c, r.items, r.answers.toFixed(1), pct(r.measured), pct(r.settled), f2(r.bias), r.corr.toFixed(2)])));
    const t = T.perProfile;
    if (!(rec.corr >= t.levelCorr)) checks.push({ level: 'FAIL', test: 'per-profile', text: `${p.id}: score follows the level with correlation ${rec.corr.toFixed(3)} (< ${t.levelCorr})` });
    if (!(rec.withinOne >= t.withinOne)) checks.push({ level: 'FAIL', test: 'per-profile', text: `${p.id}: level within one step for ${pct(rec.withinOne)} (< ${pct(t.withinOne)})` });
    if (!(good >= t.goodEnough)) checks.push({ level: 'WARN', test: 'per-profile', text: `${p.id}: good enough reached in ${pct(good)} of sessions (< ${pct(t.goodEnough)}); profile margin or size may not fit its margin_stop (profile override or profile_margin_stop)` });
    rows.filter((r) => r.measured < t.measured).forEach((r) => checks.push({ level: 'WARN', test: 'per-profile', text: `${p.id}/${r.c}: measured in only ${pct(r.measured)} of sessions (< ${pct(t.measured)})` }));
    rows.filter((r) => Math.abs(r.bias) > t.charBias).forEach((r) => checks.push({ level: 'WARN', test: 'per-profile', text: `${p.id}/${r.c}: score is ${f2(r.bias).trim()} away from the true trait (> ${t.charBias})` }));
    summary.push([p.id, sessionLen(people), pct(good), rec.corr.toFixed(3), pct(rec.exact), pct(rec.withinOne), f2(mean(rows.map((r) => Math.abs(r.bias))))]);
    data[p.id] = { questions: mean(people.map((x) => x.res.answers.length)), goodEnough: good, levelCorr: rec.corr, levelCorrect: rec.exact, withinOne: rec.withinOne, characteristics: rows };
  }
  md.splice(4, 0, ...table(['profile', 'questions asked', 'good enough', 'corr', 'level correct', 'within one', 'mean abs bias'], summary));
  return { md, checks, data };
}

// ---------------------------------------------------------------- 2. all profiles together
function allProfiles(reg, { n, seed }) {
  const eng = createEngine(reg);
  const P = reg.profiles;
  const md = ['## 2. All profiles together', '', `Every characteristic is asked. ${n} simulated people with a random level (none, low, medium, high) for each profile independently, plus about 5% holding none. Truth is the mean true trait of the profile's characteristics, so overlaps between profiles are counted as true.`, ''];
  const vals = Object.values(LEVELS);
  const people = [];
  for (let i = 0; i < n; i++) {
    const r = S.rng(seed * 31 + i);
    const nominal = P.map(() => (i % 20 === 0 ? 0 : S.pick(r, vals)));
    const person = S.simplePerson({ profiles: P, chIds: eng.chIds, nominal, seed: seed + 50000 + i });
    const res = eng.runSession(person.answer);
    const profs = eng.profileResults(res.st, eng.PEVAL, res.answers);
    people.push({ nominal, person, res, profs, oracle: P.map((p) => mean(p.characteristics.map((c) => person.stance[c]))) });
  }
  const good = share(people, (x) => x.profs.filter((r) => r.k > 0).every((r) => r.well));
  md.push(`Questions asked ${sessionLen(people)} of ${eng.BANK.length} | good enough for every profile in ${pct(good)} of sessions`, '');
  const t = T.allProfiles, checks = [], data = { profiles: {}, characteristics: [] };
  const rows = P.map((p, j) => {
    const pp = people.filter((x) => x.profs[j].score !== null);
    const s = pp.map((x) => x.profs[j].score), o = pp.map((x) => x.oracle[j]);
    const rec = levelRecovery(vals.map((v) => pp.filter((x) => x.nominal[j] === v).map((x) => x.profs[j].score)));
    const r = { id: p.id, corr: corr(s, o), bias: mean(s.map((v, i) => v - o[i])), rmse: rmse(s.map((v, i) => v - o[i])), falseHigh: share(pp.filter((x) => x.oracle[j] < 0.15), (x) => x.profs[j].score >= 0.3), falseLow: share(pp.filter((x) => x.oracle[j] >= 0.5), (x) => x.profs[j].score < 0.3), level: rec.corr, withinOne: rec.withinOne, good: share(people.filter((x) => x.profs[j].k > 0), (x) => x.profs[j].well) };
    data.profiles[p.id] = r;
    return r;
  });
  md.push('### Per profile: measured score against the truth', '');
  md.push(...table(['profile', 'corr with truth', 'bias', 'rmse', 'false high (truth < 0.15, read >= 0.3)', 'false low (truth >= 0.5, read < 0.3)', 'level corr', 'level within one', 'well explored'], rows.map((r) => [r.id, r.corr.toFixed(3), f2(r.bias), r.rmse.toFixed(3), pct(r.falseHigh), pct(r.falseLow), r.level.toFixed(3), pct(r.withinOne), pct(r.good)])));
  rows.forEach((r) => {
    if (!(r.corr >= t.profileCorr)) checks.push({ level: 'FAIL', test: 'all-profiles', text: `${r.id}: score follows the true trait with correlation ${r.corr.toFixed(3)} (< ${t.profileCorr}) when all profiles are present` });
    if (Math.abs(r.bias) > t.profileBias) checks.push({ level: 'WARN', test: 'all-profiles', text: `${r.id}: mean bias ${f2(r.bias).trim()} (> ${t.profileBias}); questions of other profiles may pull the score` });
    if (r.falseHigh > t.falseHigh) checks.push({ level: 'WARN', test: 'all-profiles', text: `${r.id}: reads high for ${pct(r.falseHigh)} of people whose true trait is low (> ${pct(t.falseHigh)})` });
  });

  md.push('### Shared characteristics between profiles (clash candidates)', '');
  const pairRows = [];
  for (let a = 0; a < P.length; a++) for (let b = a + 1; b < P.length; b++) {
    const sh = P[a].characteristics.filter((c) => P[b].characteristics.includes(c));
    pairRows.push([`${P[a].id} / ${P[b].id}`, String(sh.length), sh.length ? sh.slice(0, 6).join(', ') + (sh.length > 6 ? ', ...' : '') : '-']);
  }
  md.push(...table(['profile pair', 'shared', 'characteristics'], pairRows));

  md.push('### Characteristic score against the true trait (all 82 checked, worst 12 listed)', '');
  const chRows = eng.chIds.map((c) => {
    const sc = people.filter((x) => x.res.st[c].score !== null);
    return { c, profiles: P.filter((p) => p.characteristics.includes(c)).map((p) => p.id).join(', ') || '-', bias: mean(sc.map((x) => x.res.st[c].score - x.person.stance[c])), corr: corr(sc.map((x) => x.res.st[c].score), sc.map((x) => x.person.stance[c])), measured: share(people, (x) => x.res.st[c].n >= eng.CFG.min_answered) };
  });
  data.characteristics = chRows;
  md.push(...table(['characteristic', 'profiles', 'bias', 'corr', 'measured'], [...chRows].sort((a, b) => Math.abs(b.bias) - Math.abs(a.bias)).slice(0, 12).map((r) => [r.c, r.profiles, f2(r.bias), r.corr.toFixed(2), pct(r.measured)])));
  chRows.filter((r) => Math.abs(r.bias) > t.charBias).forEach((r) => checks.push({ level: 'WARN', test: 'all-profiles', text: `${r.c} (${r.profiles}): score is ${f2(r.bias).trim()} away from the true trait (> ${t.charBias})` }));
  return { md, checks, data };
}

// ---------------------------------------------------------------- 3. Cronbach's alpha per characteristic
function alpha(reg, { n, seed }) {
  const eng = createEngine(reg);
  const P = reg.profiles, a = T.alpha;
  const md = ['## 3. Internal consistency (Cronbach alpha) per characteristic', '', `For each profile, ${n} simulated people hold that profile at none, low, medium or high (equal shares, answer noise x${a.noise}) and the other profiles at none. Items are the questions that list the characteristic as main. Every item is presented to every person and alpha is computed over the people who answered all items. Target ${a.min}-${a.max} (exercise-bdr-policy-604.12). A characteristic listed by several profiles is tested in each of them.`, ''];
  const score = (q, v) => (v === null || v === undefined ? null : eng.centre(q, v) * Math.sign(q.main.weight));
  const band = (x) => (Number.isNaN(x) ? 'not measured' : x < a.min ? 'LOW' : x > a.max ? 'HIGH' : 'ok');
  const sum = (list) => { const m = list.filter((r) => !Number.isNaN(r.alpha)).map((r) => r.alpha); return `ok ${list.filter((r) => r.band === 'ok').length}, LOW ${list.filter((r) => r.band === 'LOW').length}, HIGH ${list.filter((r) => r.band === 'HIGH').length}, not measured ${list.filter((r) => r.band === 'not measured').length}` + (m.length ? ` | mean ${mean(m).toFixed(2)}, min ${Math.min(...m).toFixed(2)}, max ${Math.max(...m).toFixed(2)}` : ''); };
  const head = ['characteristic', 'main items', 'complete respondents', 'alpha', 'band', 'note'];
  const checks = [], data = {};
  P.forEach((p, pi) => {
    const qsAll = eng.BANK.filter((q) => p.characteristics.includes(q.main.id));
    const full = [];
    for (let i = 0; i < n; i++) {
      const lvl = levelNames[i % levelNames.length];
      const person = S.simplePerson({ profiles: P, chIds: eng.chIds, nominal: P.map((x) => (x.id === p.id ? LEVELS[lvl] : 0)), seed: seed + 90000 + pi * 10000 + i, noise: a.noise });
      const row = {}; qsAll.forEach((q) => { row[q.id] = person.answer(q); });
      full.push(row);
    }
    const alphaOf = (qs) => {
      const rows = full.map((r) => qs.map((q) => score(q, r[q.id]))).filter((r) => r.every((v) => v !== null));
      if (rows.length < a.minPairs || qs.length < a.minItems) return { alpha: NaN, n: rows.length };
      const k = qs.length, cols = qs.map((_, j) => rows.map((r) => r[j]));
      const vt = S.variance(rows.map((r) => r.reduce((s, v) => s + v, 0)));
      return { alpha: (k / (k - 1)) * (1 - cols.reduce((s, c) => s + S.variance(c), 0) / vt), n: rows.length };
    };
    const rows = p.characteristics.map((c) => {
      const qs = qsAll.filter((q) => q.main.id === c);
      const r = alphaOf(qs), b = band(r.alpha);
      let note = '';
      if (b === 'LOW' || b === 'HIGH') {
        let best = null;
        qs.forEach((q) => { const d = alphaOf(qs.filter((x) => x !== q)); if (!Number.isNaN(d.alpha) && (!best || (b === 'LOW' ? d.alpha > best.alpha : d.alpha < best.alpha))) best = { id: q.id, alpha: d.alpha }; });
        note = b === 'LOW' ? (best ? `dropping ${best.id} gives ${best.alpha.toFixed(2)}` : 'too few items to drop one') : `${qs.length} main items; check for near duplicates or trim items`;
      }
      if (b === 'not measured') note = `${qs.length} main items, ${r.n} complete respondents`;
      return { c, items: qs.length, n: r.n, alpha: r.alpha, band: b, note };
    });
    data[p.id] = rows;
    md.push(`### ${p.id}`, '', sum(rows), '', ...table(head, rows.map((r) => [r.c, r.items, r.n, Number.isNaN(r.alpha) ? 'n/a' : r.alpha.toFixed(2), r.band, r.note])));
    rows.forEach((r) => {
      if (r.band === 'LOW') checks.push({ level: 'FAIL', test: 'alpha', text: `${p.id}/${r.c}: alpha ${r.alpha.toFixed(2)} < ${a.min}; ${r.note}` });
      if (r.band === 'HIGH') checks.push({ level: 'WARN', test: 'alpha', text: `${p.id}/${r.c}: alpha ${r.alpha.toFixed(2)} > ${a.max}; ${r.note}` });
      if (r.band === 'not measured') checks.push({ level: 'WARN', test: 'alpha', text: `${p.id}/${r.c}: not measured, ${r.note}; add main items (at least ${a.minItems})` });
    });
  });
  const listed = new Set(P.flatMap((p) => p.characteristics));
  const orphan = eng.chIds.filter((c) => !listed.has(c));
  if (orphan.length) { md.push(`Not tested because no profile lists them: ${orphan.join(', ')}`, ''); checks.push({ level: 'WARN', test: 'alpha', text: `characteristics in no profile are not tested: ${orphan.join(', ')}` }); }
  return { md, checks, data };
}

// ---------------------------------------------------------------- 4. stress with a mixed population
function stress(reg, { n, seed }) {
  const eng = createEngine(reg);
  const P = reg.profiles, names = P.map((p) => p.id), t = T.stress, checks = [];
  const ARCH = S.archetypes(P, require('./engine').DOMAINS, eng.chIds, eng.chDomain);
  const W = ARCH.reduce((s, x) => s + x[2], 0);
  const people = [];
  ARCH.forEach((a) => {
    const count = Math.max(1, Math.round(n * a[2] / W));
    for (let i = 0; i < count; i++) {
      const id = people.length;
      const spec = a[3](S.rng(seed * 100003 + id), i);
      const sp = S.stressPerson({ profiles: P, chIds: eng.chIds, chDomain: eng.chDomain, spec, seed: seed * 1000 + id });
      const res = eng.runSession(sp.answer);
      const profs = eng.profileResults(res.st, eng.PEVAL, res.answers);
      people.push({ group: a[0], arch: a[1], spec, levels: spec.levels, stance: sp.stance, res, profs, quality: eng.responseQuality(res.answers, res.st), oracle: P.map((p) => mean(p.characteristics.map((c) => sp.stance[c]))), nq: res.answers.length });
    }
  });
  const honest = people.filter((p) => p.group === 'honest');
  const md = ['## 4. Stress test with a mixed population', '', `${people.length} simulated people: honest people with none, low, medium and high levels of each profile alone and in combinations of two, three or all profiles, characteristic pockets and patterns that match no profile; plus careless, distorted and invalid respondents (random, straight-line, yes-saying, contrarian, fatigue, skipping, masking). Answer noise, acquiescence and skips vary per person.`, ''];

  const bad = people.filter((p) => p.profs.some((r) => r.score !== null && (!Number.isFinite(r.score) || r.score < -1 || r.score > 1 || !Number.isFinite(r.wscore)))).length;
  const missing = people.filter((p) => p.profs.some((r) => r.score === null)).length;
  const nq = people.map((p) => p.nq);
  md.push('### Robustness', '', `Scores that are NaN or outside -1..1: ${bad} | sessions with no score for some profile: ${missing} | questions asked mean ${mean(nq).toFixed(0)}, min ${Math.min(...nq)}, p95 ${pctl(nq, 0.95)}, max ${Math.max(...nq)} of ${eng.BANK.length}`, '');
  if (bad) checks.push({ level: 'FAIL', test: 'stress', text: `${bad} sessions produced NaN or out-of-range profile scores` });
  if (missing) checks.push({ level: 'WARN', test: 'stress', text: `${missing} sessions ended without any evidence for some profile` });

  md.push('### Per person type', '');
  const archRows = ARCH.map((a) => {
    const g = people.filter((p) => p.arch === a[1]); if (!g.length) return null;
    const mae = g[0].group === 'invalid' ? NaN : mean(g.flatMap((p) => p.profs.map((r, j) => Math.abs(r.score - p.oracle[j]))));
    return [a[1], a[0], g.length, mean(g.map((p) => p.nq)).toFixed(0), Number.isNaN(mae) ? 'n/a' : mae.toFixed(3), pct(share(g, (p) => p.quality.flagged)), pct(share(g, (p) => p.profs.every((r) => r.well)))];
  }).filter(Boolean);
  md.push(...table(['type', 'group', 'n', 'questions', 'mean abs error vs truth', 'quality flagged', 'good enough'], archRows));

  md.push('### Low, medium and high levels of one profile', '', 'Mean score of the target profile for people holding only that profile, and the mean score on the other profiles (truth for those is not exactly zero when characteristics are shared).', '');
  const lvRows = [];
  P.forEach((p, j) => {
    const means = ['low', 'medium', 'high'].map((b) => {
      const g = honest.filter((x) => x.spec.target === j && x.spec.band === b);
      return { b, n: g.length, m: mean(g.map((x) => x.profs[j].score)), s: sd(g.map((x) => x.profs[j].score)), other: mean(g.flatMap((x) => x.profs.filter((_, k) => k !== j).map((r) => r.score))), oth: mean(g.flatMap((x) => x.oracle.filter((_, k) => k !== j))) };
    });
    lvRows.push([p.id, ...means.map((m) => `${f2(m.m)} ±${m.s.toFixed(2)} (n ${m.n})`), ...means.map((m) => f2(m.other))]);
    const okOrder = means.every((m) => m.n >= 3) && means[0].m < means[1].m && means[1].m < means[2].m;
    if (means.every((m) => m.n >= 3) && !okOrder) checks.push({ level: 'FAIL', test: 'stress', text: `${p.id}: mean score does not rise from low to medium to high (${means.map((m) => f2(m.m).trim()).join(', ')})` });
  });
  md.push(...table(['profile', 'low', 'medium', 'high', 'other profiles @low', '@medium', '@high'], lvRows));

  md.push('### Honest people: accuracy and identification', '');
  const err = honest.flatMap((p) => p.profs.map((r, j) => r.score - p.oracle[j]));
  const dom = honest.filter((p) => Math.max(...p.oracle) - [...p.oracle].sort((u, v) => v - u)[1] >= 0.15 && Math.max(...p.oracle) >= 0.3);
  const argmax = (a) => a.indexOf(Math.max(...a));
  const hitReg = share(dom, (p) => argmax(p.profs.map((r) => r.score)) === argmax(p.oracle));
  const hitW = share(dom, (p) => argmax(p.profs.map((r) => r.wscore)) === argmax(p.oracle));
  const neuro = honest.filter((p) => p.arch === 'neurotypical');
  const neuroHigh = share(neuro, (p) => p.profs.some((r) => r.score >= 0.3));
  md.push(`Mean error ${f2(mean(err))}, mean abs error ${mean(err.map(Math.abs)).toFixed(3)}, rmse ${rmse(err).toFixed(3)} | strongest profile identified (clear dominant profile, n ${dom.length}): regular score ${pct(hitReg)}, weighted score ${pct(hitW)} | neurotypical people with some profile >= 0.3: ${pct(neuroHigh)} (n ${neuro.length})`, '');
  if (!(mean(err.map(Math.abs)) <= t.honestMae)) checks.push({ level: 'WARN', test: 'stress', text: `honest people: mean abs error ${mean(err.map(Math.abs)).toFixed(3)} (> ${t.honestMae})` });
  if (dom.length >= 10 && !(hitW >= t.identified)) checks.push({ level: 'WARN', test: 'stress', text: `strongest profile identified for only ${pct(hitW)} of honest people with a clear dominant profile (< ${pct(t.identified)})` });
  if (neuro.length >= 10 && neuroHigh > t.neurotypicalHigh) checks.push({ level: 'WARN', test: 'stress', text: `${pct(neuroHigh)} of neurotypical people read >= 0.3 on some profile (> ${pct(t.neurotypicalHigh)})` });

  md.push('### Response quality flag', '');
  const fa = share(honest, (p) => p.quality.flagged);
  const inv = people.filter((p) => p.group === 'invalid'), dis = people.filter((p) => p.group === 'distorted');
  md.push(`Honest people flagged (false alarms): ${pct(fa)} | invalid respondents flagged: ${pct(share(inv, (p) => p.quality.flagged))} | distorted respondents flagged: ${pct(share(dis, (p) => p.quality.flagged))} | good enough shown to any person: ${pct(share(people, (p) => p.profs.every((r) => r.well)))}`, '');
  if (fa > t.falseAlarm) checks.push({ level: 'WARN', test: 'stress', text: `quality flag raised for ${pct(fa)} of honest people (> ${pct(t.falseAlarm)})` });
  if (inv.length >= 10 && share(inv, (p) => p.quality.flagged) < t.invalidFlagged) checks.push({ level: 'WARN', test: 'stress', text: `quality flag raised for only ${pct(share(inv, (p) => p.quality.flagged))} of invalid respondents (< ${pct(t.invalidFlagged)})` });

  md.push('### Worst honest cases', '');
  const worst = honest.map((p) => { const e = p.profs.map((r, j) => r.score - p.oracle[j]); const j = e.reduce((b, v, i) => (Math.abs(v) > Math.abs(e[b]) ? i : b), 0); return { p, j, e: e[j] }; }).sort((a, b) => Math.abs(b.e) - Math.abs(a.e)).slice(0, 8);
  md.push(...table(['type', 'profile', 'true trait', 'measured', 'margin', 'questions'], worst.map(({ p, j }) => [p.arch, names[j], f2(p.oracle[j]), f2(p.profs[j].score), p.profs[j].margin.toFixed(2), p.nq])));
  return { md, checks, data: { people: people.length, bad, missing, honestMae: mean(err.map(Math.abs)), hitWeighted: hitW, falseAlarm: fa } };
}

module.exports = { T, perProfile, allProfiles, alpha, stress };
