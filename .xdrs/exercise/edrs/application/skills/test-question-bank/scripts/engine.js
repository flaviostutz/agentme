'use strict';
// Reference implementation of the exercise engine (exercise-adr-policy-101) and measurement formulas
// (exercise-edr-policy-101). It runs in Node, where the test-question-bank skill dry-runs the registries with
// simulated respondents, and unchanged in the browser, where the web client feeds it Answers
// (exercise-adr-policy-102.02-shared-engine-module). It reads the registries and never changes them.
// When the Policies change, change this file with them.
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(typeof require === 'function' ? require : null);
  else root.ExerciseEngine = factory(null);
}(typeof self !== 'undefined' ? self : this, function (nodeRequire) {
const DOMAINS = ['attention', 'executive_function', 'sensory_processing', 'social_communication', 'thinking_patterns', 'emotional_experience', 'interests_learning', 'adaptation_environment'];

// Node only; the browser receives the registry as data
function loadRegistry(given) {
  const fs = nodeRequire('fs');
  const path = nodeRequire('path');
  const dir = given || path.join(__dirname, '../../../../../adrs/data/.assets');
  const read = (f) => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  const questions = DOMAINS.flatMap((d) => {
    const file = path.join(dir, 'questions', `${d}.json`);
    if (!fs.existsSync(file)) return [];
    const r = JSON.parse(fs.readFileSync(file, 'utf8'));
    return r.questions || r;
  });
  return { dir, config: read('config.json'), characteristics: read('characteristics.json'), profiles: read('profiles.json'), questions };
}

// profiles: ids of the analysed Profiles (default: every Profile), changeable in a session with setProfiles.
// scope: profile id used by the test skill; like profiles: [id] but the bank is also limited to the Questions whose
// main Characteristic belongs to that Profile.
function createEngine(registry, { scope = null, profiles = null, config = {} } = {}) {
  if (scope && profiles) throw new Error('use scope or profiles, not both');
  const CFG = { ...registry.config, ...config };
  const CH = registry.characteristics;
  const chIds = CH.map((c) => c.id);
  const chDomain = Object.fromEntries(CH.map((c) => [c.id, c.domain]));

  // everything that depends on which Profiles are analysed (exercise-adr-policy-101.10-analysed-profiles)
  function scopeOf(ids) {
    let list = registry.profiles;
    if (ids) {
      const want = new Set(ids);
      ids.forEach((id) => { if (!registry.profiles.some((p) => p.id === id)) throw new Error(`unknown profile ${id}`); });
      list = registry.profiles.filter((p) => want.has(p.id));
      if (!list.length) throw new Error('at least one profile must be analysed');
    }
    const SC = ids ? new Set(list.flatMap((p) => p.characteristics)) : null;
    const P = list.length;
    const kc = {}; chIds.forEach((c) => { kc[c] = list.filter((p) => p.characteristics.includes(c)).length; });
    const pw = {}; chIds.forEach((c) => { pw[c] = kc[c] ? (P - kc[c] + 1) / P : 1; });
    return { ids: list.map((p) => p.id), PEVAL: list, P, SC, inS: (id) => !SC || SC.has(id), kc, pw };
  }
  const base = scopeOf(scope ? [scope] : profiles);
  const { SC, PEVAL, P, kc, pw } = base;

  const mainOf = (q) => q.characteristics.reduce((a, c) => (Math.abs(c.weight) > Math.abs(a.weight) ? c : a));
  const STAGE = { discovery: 0, exploration: 1, differentiation: 2, balancing: 3 };
  let BANK = registry.questions.map((q) => ({ ...q, routes: [...(q.routes || [])] }));
  BANK.forEach((q) => { q.main = mainOf(q); q.domain = chDomain[q.main.id]; q.stage = STAGE[q.type]; });
  if (scope) BANK = BANK.filter((q) => SC.has(q.main.id));
  const qById = {};
  BANK.forEach((q, i) => { q.idx = i; qById[q.id] = q; });
  BANK.forEach((q) => { q.routes = q.routes.filter((r) => qById[r.add]); });

  const carry = {}; chIds.forEach((c) => { carry[c] = []; });
  BANK.forEach((q) => q.characteristics.forEach((c) => carry[c.id] && carry[c.id].push(q)));
  const balQs = {};
  chIds.forEach((c) => { balQs[c] = carry[c].filter((q) => q.type === 'balancing' && q.characteristics.find((x) => x.id === c).weight < 0).map((q) => q.id); });

  const centre = (q, v) => (q.answer === 'frequency' ? 2 * v - 1 : v);

  // ---- measurement (exercise-edr-policy-101) ----
  // Evidence entries per Characteristic are kept by the caller and appended to as answers arrive,
  // so a state is recomputed only for the Characteristics of the Question just answered.
  const entryOf = (q, x, v) => ({ w: x.weight, e: v === null ? null : x.weight * centre(q, v) });
  function charState(c, ent, asked) {
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
      const bal = Math.abs(out.score) <= CFG.balancing_min_score || balQs[c].length === 0 || balQs[c].some((id) => asked.has(id));
      if ((out.margin <= CFG.margin_stop || stable) && bal) out.state = 'settled';
    }
    return out;
  }
  const emptyStates = () => { const s = {}; chIds.forEach((c) => { s[c] = charState(c, [], new Set()); }); return s; };

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

  function profileResults(st, plist, answers, sc = base) {
    const pw = sc.pw;
    let quality = null; // response quality scans every answer, so it runs only when the other conditions hold
    const flagged = () => { if (quality === null) quality = answers ? responseQuality(answers, st).flagged : false; return quality; };
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
      r.well = r.measured >= CFG.profile_measured_ratio && r.settled >= CFG.profile_settled_ratio && r.margin <= (p.margin_stop ?? CFG.profile_margin_stop) && !flagged();
      return r;
    });
  }

  // ---- flow (exercise-adr-policy-101): one queue, routes, refill, gap filling ----
  // A session is stepped with next() and answer(v); the Profiles analysed can change between steps (setProfiles).
  function createSession(profileIds = null) {
    let sc = profileIds ? scopeOf(profileIds) : base;
    const answers = [], queued = new Set(), asked = new Set(), ents = {}, st = emptyStates();
    let queue = [], ins = 0, last = null, goodAt = null, pending = null, pendingIt = null;
    chIds.forEach((c) => { ents[c] = []; });
    const openIn = (q) => q.characteristics.filter((c) => sc.inS(c.id) && st[c.id].state === 'open');
    const add = (q, byLast) => { if (asked.has(q.id) || queued.has(q.id)) return; queue.push({ q, ins: ins++, byLast: !!byLast }); queued.add(q.id); };
    const prune = () => { queue = queue.filter((it) => openIn(it.q).length); queued.clear(); queue.forEach((it) => queued.add(it.q.id)); };
    const refill = () => { for (const q of BANK) if (!asked.has(q.id) && q.characteristics.some((c) => sc.inS(c.id) && st[c.id].state === 'open' && st[c.id].n > 0)) add(q); };
    BANK.filter((q) => q.type === 'discovery').forEach((q) => add(q));

    // the Question to ask now, or null when the session ended; asking it twice returns the same one
    function next() {
      if (pending) return pending;
      prune();
      if (!queue.length) { refill(); if (!queue.length) return null; }
      let best = null, bk = null;
      for (const it of queue) {
        const open = openIn(it.q);
        const key = [it.byLast ? 0 : 1, last && it.q.domain === last.domain ? 0 : 1, Math.min(...open.map((c) => st[c.id].n)), it.q.stage, it.ins];
        let lt = !bk;
        if (!lt) for (let i = 0; i < key.length; i++) if (key[i] !== bk[i]) { lt = key[i] < bk[i]; break; }
        if (lt) { best = it; bk = key; }
      }
      queue = queue.filter((it) => it !== best); queued.delete(best.q.id);
      asked.add(best.q.id);
      pending = best.q; pendingIt = best;
      return pending;
    }

    // asks a given Question instead of the one next() would choose; used when replaying Answers that remain after others were deleted
    function ask(id) {
      const q = qById[id];
      if (!q) throw new Error(`unknown question ${id}`);
      if (pending && pending.id === id) return pending;
      if (asked.has(id)) throw new Error(`question ${id} appears twice in the answers`);
      if (pending) { asked.delete(pending.id); queue.push(pendingIt); queued.add(pending.id); }
      queue = queue.filter((it) => it.q !== q); queued.delete(id);
      asked.add(id);
      pending = q; pendingIt = null;
      return pending;
    }

    // v: the stored value, or null when skipped
    function answer(v) {
      if (!pending) throw new Error('no question to answer; call next() first');
      const q = pending; pending = null;
      answers.push({ q: q.id, v }); last = q;
      queue.forEach((it) => { it.byLast = false; });
      if (v !== null) for (const r of q.routes) if ((r.when === 'gte' && v >= r.threshold) || (r.when === 'lte' && v <= r.threshold)) add(qById[r.add], true);
      for (const x of q.characteristics) { ents[x.id].push(entryOf(q, x, v)); st[x.id] = charState(x.id, ents[x.id], asked); }
      const gaps = chIds.filter((c) => sc.inS(c) && sc.kc[c] > 0 && st[c].state === 'open' && st[c].n < CFG.min_answered && chDomain[c] === q.domain);
      for (const c of gaps) {
        if (queue.some((it) => it.q.characteristics.some((x) => x.id === c))) continue;
        const cand = carry[c].filter((x) => !asked.has(x.id) && !queued.has(x.id)).sort((a, b) => a.stage - b.stage || a.idx - b.idx)[0];
        if (cand) add(cand);
      }
      if (goodAt === null) {
        const withEv = profileResults(st, sc.PEVAL, answers, sc).filter((r) => r.k > 0);
        if (withEv.length && withEv.every((r) => r.well)) goodAt = answers.length;
      }
    }

    // exercise-adr-policy-101.10-analysed-profiles: Answers are kept; the queue is re-checked against the new scope
    function setProfiles(ids) {
      if (pending) throw new Error('profiles can change only before the next question is chosen');
      const before = sc;
      sc = scopeOf(ids);
      prune();
      for (const q of BANK) {
        if (q.type !== 'discovery' || asked.has(q.id) || queued.has(q.id)) continue;
        if (q.characteristics.some((c) => sc.inS(c.id) && !before.inS(c.id) && st[c.id].state === 'open')) add(q);
      }
    }

    return {
      next, ask, answer, setProfiles, st, answers,
      get goodAt() { return goodAt; },
      get profiles() { return sc.ids; },
      get analysed() { return sc.PEVAL; },
      get weights() { return sc.pw; },
      inScope: (id) => sc.inS(id),
      // true when no Question that touches an open Characteristic of the Profile can still be offered
      exhausted: (id) => {
        const p = sc.PEVAL.find((x) => x.id === id);
        if (!p) return true;
        const open = new Set(p.characteristics.filter((c) => st[c].state === 'open'));
        const touches = (q) => q.characteristics.some((c) => open.has(c.id));
        if (!open.size) return true;
        if ((pending && touches(pending)) || queue.some((it) => touches(it.q))) return false;
        return !BANK.some((q) => !asked.has(q.id) && !queued.has(q.id) && touches(q) && q.characteristics.some((c) => sc.inS(c.id) && st[c.id].state === 'open' && st[c.id].n > 0));
      },
      results: () => profileResults(st, sc.PEVAL, answers, sc),
      quality: () => responseQuality(answers, st)
    };
  }

  function runSession(answerFn) {
    const s = createSession();
    for (let q = s.next(); q; q = s.next()) s.answer(answerFn(q));
    return { answers: s.answers, st: s.st, goodAt: s.goodAt };
  }

  // Rebuilds a session from the stored form (exercise-adr-policy-101.09-state-is-derived): the first analysed
  // Profiles, the Answers in order and the ordered Profile changes, each with the number of Answers when it happened.
  // onStep(session, index, question) runs after every Answer. Throws when the stored form does not match this engine.
  function replay({ profiles: first = null, answers = [], changes = [] } = {}, onStep = null) {
    const s = createSession(first);
    let ci = 0;
    const applyChanges = (n) => { while (ci < changes.length && changes[ci].at <= n) s.setProfiles(changes[ci++].profiles); };
    for (let i = 0; i < answers.length; i++) {
      applyChanges(i);
      s.next(); // keeps the queue evolving as in a live session; ask() corrects it when this Answer was not the engine's choice
      const q = s.ask(answers[i].q);
      const v = answers[i].v;
      if (v !== null) {
        const lo = q.answer === 'frequency' ? 0 : -1;
        if (typeof v !== 'number' || !Number.isFinite(v) || v < lo || v > 1) throw new Error(`answer ${i + 1} (${q.id}) is out of range`);
      }
      s.answer(v === null ? null : Math.round(v * 100) / 100);
      if (onStep) onStep(s, i, q);
    }
    applyChanges(answers.length);
    s.next();
    return s;
  }

  return { CFG, CH, BANK, PROFILES: registry.profiles, PEVAL, chIds, chDomain, qById, kc, pw, runSession, createSession, replay, profileResults, responseQuality, centre, scope };
}

return { DOMAINS, loadRegistry, createEngine };
}));
