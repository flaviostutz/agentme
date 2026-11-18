'use strict';
// Reference implementation of the exercise engine (exercise-adr-policy-101) and measurement formulas
// (exercise-edr-policy-101), used only to dry-run the registries with simulated respondents.
// It reads the registries and never changes them. When the Policies change, change this file with them.
const fs = require('fs');
const path = require('path');

const DOMAINS = ['attention', 'executive_function', 'sensory_processing', 'social_communication', 'thinking_patterns', 'emotional_experience', 'interests_learning', 'adaptation_environment'];
const DEFAULT_REGISTRY = path.join(__dirname, '../../../../../adrs/data/.assets');

function loadRegistry(dir = DEFAULT_REGISTRY) {
  const read = (f) => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  const questions = DOMAINS.flatMap((d) => {
    const file = path.join(dir, 'questions', `${d}.json`);
    if (!fs.existsSync(file)) return [];
    const r = JSON.parse(fs.readFileSync(file, 'utf8'));
    return r.questions || r;
  });
  return { dir, config: read('config.json'), characteristics: read('characteristics.json'), profiles: read('profiles.json'), questions };
}

// scope: profile id; when set, only the Characteristics of that Profile are asked about and judged
function createEngine(registry, { scope = null, config = {} } = {}) {
  const CFG = { ...registry.config, ...config };
  const CH = registry.characteristics;
  const chIds = CH.map((c) => c.id);
  const chDomain = Object.fromEntries(CH.map((c) => [c.id, c.domain]));
  const scoped = scope ? registry.profiles.find((p) => p.id === scope) : null;
  if (scope && !scoped) throw new Error(`unknown profile ${scope}`);
  const SC = scoped ? new Set(scoped.characteristics) : null;
  const inS = (id) => !SC || SC.has(id);

  const mainOf = (q) => q.characteristics.reduce((a, c) => (Math.abs(c.weight) > Math.abs(a.weight) ? c : a));
  const STAGE = { discovery: 0, exploration: 1, differentiation: 2, balancing: 3 };
  let BANK = registry.questions.map((q) => ({ ...q, routes: [...(q.routes || [])] }));
  BANK.forEach((q) => { q.main = mainOf(q); q.domain = chDomain[q.main.id]; q.stage = STAGE[q.type]; });
  if (SC) BANK = BANK.filter((q) => SC.has(q.main.id));
  const qById = {};
  BANK.forEach((q, i) => { q.idx = i; qById[q.id] = q; });
  BANK.forEach((q) => { q.routes = q.routes.filter((r) => qById[r.add]); });

  const carry = {}; chIds.forEach((c) => { carry[c] = []; });
  BANK.forEach((q) => q.characteristics.forEach((c) => carry[c.id] && carry[c.id].push(q)));
  const balQs = {};
  chIds.forEach((c) => { balQs[c] = carry[c].filter((q) => q.type === 'balancing' && q.characteristics.find((x) => x.id === c).weight < 0).map((q) => q.id); });

  const PEVAL = registry.profiles.filter((p) => !scoped || p.id === scoped.id);
  const P = PEVAL.length;
  const kc = {}; chIds.forEach((c) => { kc[c] = PEVAL.filter((p) => p.characteristics.includes(c)).length; });
  const pw = {}; chIds.forEach((c) => { pw[c] = kc[c] ? (P - kc[c] + 1) / P : 1; });

  const centre = (q, v) => (q.answer === 'frequency' ? 2 * v - 1 : v);

  // ---- measurement (exercise-edr-policy-101) ----
  function charState(c, answers) {
    const ent = [];
    for (const a of answers) {
      const q = qById[a.q]; const x = q.characteristics.find((z) => z.id === c); if (!x) continue;
      ent.push({ w: x.weight, e: a.v === null ? null : x.weight * centre(q, a.v) });
    }
    const nn = ent.filter((e) => e.e !== null);
    const n = nn.length, total = ent.length;
    const out = { n, total, score: null, margin: Infinity, se: null, state: 'open' };
    if (n) {
      const V1 = nn.reduce((s, e) => s + Math.abs(e.w), 0), V2 = nn.reduce((s, e) => s + e.w * e.w, 0);
      out.score = Math.max(-1, Math.min(1, nn.reduce((s, e) => s + e.e, 0) / V1));
      if (n >= CFG.min_answered) {
        const den = V1 - V2 / V1;
        const s = den > 1e-9 ? Math.sqrt(nn.reduce((t, e) => t + Math.abs(e.w) * (e.e / Math.abs(e.w) - out.score) ** 2, 0) / den) : 0;
        const neff = V1 * V1 / V2;
        out.margin = 1.96 * s / Math.sqrt(neff); out.se = s / Math.sqrt(neff);
      } else out.se = CFG.evidence_sd / Math.sqrt(n);
    }
    const unc = total ? (total - n) / total : null;
    if (total >= CFG.giveup_min_asked && unc >= CFG.uncertainty_giveup) out.state = 'given_up';
    else if (out.margin < Infinity) {
      let stable = false;
      if (n > CFG.stability_window) {
        stable = true; let V = 0, S = 0; const run = [];
        for (const e of nn) { V += Math.abs(e.w); S += e.e; run.push(S / V); }
        for (let i = n - CFG.stability_window; i < n; i++) if (Math.abs(run[i] - out.score) > CFG.stability_delta) stable = false;
      }
      const asked = new Set(answers.map((a) => a.q));
      const bal = Math.abs(out.score) <= CFG.balancing_min_score || balQs[c].length === 0 || balQs[c].some((id) => asked.has(id));
      if ((out.margin <= CFG.margin_stop || stable) && bal) out.state = 'settled';
    }
    return out;
  }
  const allStates = (answers) => { const s = {}; chIds.forEach((c) => { s[c] = charState(c, answers); }); return s; };

  // ---- response quality (exercise-edr-policy-101 response quality rule) ----
  function responseQuality(answers, st) {
    const out = { flagged: false, reasons: [], meanMargin: null, keying: null, spread: null };
    const measured = chIds.filter((c) => st[c].n >= CFG.min_answered);
    if (measured.length < CFG.quality_min_characteristics) return out;
    const mean = (a) => a.reduce((s, x) => s + x, 0) / a.length;
    out.meanMargin = mean(measured.map((c) => st[c].margin));
    const gaps = [];
    for (const c of chIds) {
      const pos = [], neg = [];
      for (const a of answers) {
        if (a.v === null) continue;
        const q = qById[a.q]; const z = q.characteristics.find((t) => t.id === c); if (!z) continue;
        (z.weight > 0 ? pos : neg).push(Math.sign(z.weight) * centre(q, a.v));
      }
      if (pos.length && neg.length) gaps.push(Math.abs(mean(pos) - mean(neg)));
    }
    if (gaps.length) out.keying = mean(gaps);
    const sc = chIds.map((c) => st[c].score).filter((s) => s !== null), m = mean(sc);
    out.spread = Math.sqrt(mean(sc.map((s) => (s - m) ** 2)));
    if (out.meanMargin > CFG.quality_margin_max) out.reasons.push('scattered');
    if (out.keying !== null && out.keying > CFG.quality_keying_max) out.reasons.push('keying');
    if (out.spread < CFG.quality_spread_min && Math.abs(m) <= CFG.quality_flat_max_mean) out.reasons.push('flat');
    out.flagged = out.reasons.length > 0;
    return out;
  }

  function profileResults(st, plist, answers) {
    const flagged = answers ? responseQuality(answers, st).flagged : false;
    return plist.map((p) => {
      const ev = p.characteristics.filter((c) => st[c].score !== null);
      const k = ev.length; const r = { id: p.id, k, score: null, margin: Infinity, wscore: null, wmargin: Infinity, well: false };
      if (!k) return r;
      r.score = ev.reduce((s, c) => s + st[c].score, 0) / k;
      r.margin = 1.96 * Math.sqrt(ev.reduce((s, c) => s + st[c].se ** 2, 0)) / k;
      const W = ev.reduce((s, c) => s + pw[c], 0);
      r.wscore = ev.reduce((s, c) => s + pw[c] * st[c].score, 0) / W;
      r.wmargin = 1.96 * Math.sqrt(ev.reduce((s, c) => s + pw[c] ** 2 * st[c].se ** 2, 0)) / W;
      const cs = p.characteristics;
      r.measured = cs.filter((c) => st[c].n >= CFG.min_answered).length / cs.length;
      r.settled = cs.filter((c) => st[c].state !== 'open').length / cs.length;
      r.well = !flagged && r.measured >= CFG.profile_measured_ratio && r.settled >= CFG.profile_settled_ratio && r.margin <= CFG.profile_margin_stop;
      return r;
    });
  }

  // ---- flow (exercise-adr-policy-101): one queue, routes, refill, gap filling ----
  const openIn = (q, st) => q.characteristics.filter((c) => inS(c.id) && st[c.id].state === 'open');
  function runSession(answerFn) {
    const answers = []; let queue = []; const queued = new Set(), asked = new Set(); let ins = 0;
    const add = (q, byLast) => { if (asked.has(q.id) || queued.has(q.id)) return; queue.push({ q, ins: ins++, byLast: !!byLast }); queued.add(q.id); };
    const refill = (st) => { for (const q of BANK) if (!asked.has(q.id) && q.characteristics.some((c) => inS(c.id) && st[c.id].state === 'open' && st[c.id].n > 0)) add(q); };
    BANK.filter((q) => q.type === 'discovery').forEach((q) => add(q));
    let last = null, goodAt = null, st = allStates(answers);
    for (;;) {
      queue = queue.filter((it) => openIn(it.q, st).length); queued.clear(); queue.forEach((it) => queued.add(it.q.id));
      if (!queue.length) { refill(st); if (!queue.length) break; }
      let best = null, bk = null;
      for (const it of queue) {
        const open = openIn(it.q, st);
        const key = [it.byLast ? 0 : 1, last && it.q.domain === last.domain ? 0 : 1, Math.min(...open.map((c) => st[c.id].n)), it.q.stage, it.ins];
        let lt = !bk;
        if (!lt) for (let i = 0; i < key.length; i++) if (key[i] !== bk[i]) { lt = key[i] < bk[i]; break; }
        if (lt) { best = it; bk = key; }
      }
      queue = queue.filter((it) => it !== best); queued.delete(best.q.id);
      const q = best.q; asked.add(q.id);
      const v = answerFn(q);
      answers.push({ q: q.id, v }); last = q;
      queue.forEach((it) => { it.byLast = false; });
      if (v !== null) for (const r of q.routes) if ((r.when === 'gte' && v >= r.threshold) || (r.when === 'lte' && v <= r.threshold)) add(qById[r.add], true);
      st = allStates(answers);
      const gaps = chIds.filter((c) => inS(c) && kc[c] > 0 && st[c].state === 'open' && st[c].n < CFG.min_answered && chDomain[c] === q.domain);
      for (const c of gaps) {
        if (queue.some((it) => it.q.characteristics.some((x) => x.id === c))) continue;
        const cand = carry[c].filter((x) => !asked.has(x.id) && !queued.has(x.id)).sort((a, b) => a.stage - b.stage || a.idx - b.idx)[0];
        if (cand) add(cand);
      }
      if (goodAt === null) {
        const withEv = profileResults(st, PEVAL, answers).filter((r) => r.k > 0);
        if (withEv.length && withEv.every((r) => r.well)) goodAt = answers.length;
      }
    }
    return { answers, st, goodAt };
  }

  return { CFG, CH, BANK, PROFILES: registry.profiles, PEVAL, chIds, chDomain, qById, kc, pw, runSession, profileResults, responseQuality, centre, scope };
}

module.exports = { DOMAINS, DEFAULT_REGISTRY, loadRegistry, createEngine };
