'use strict';
// Simulated respondents and small statistics helpers for the question bank tests.
// Respondents answer from a hidden "stance" per Characteristic (the truth the engine should recover), derived
// from the severity of each Profile they hold. They test keying, weights and routes, not the wording.

function rng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
function gauss(r) { const u = 1 - r(), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
const clamp = (x, a = -1, b = 1) => Math.max(a, Math.min(b, x));
const U = (r, a, b) => a + (b - a) * r();
const pick = (r, a) => a[Math.floor(r() * a.length)];
const mean = (a) => a.reduce((s, x) => s + x, 0) / (a.length || 1);
const sd = (a) => { const m = mean(a); return Math.sqrt(mean(a.map((x) => (x - m) ** 2))); };
const variance = (a) => { const m = mean(a); return a.reduce((s, x) => s + (x - m) ** 2, 0) / (a.length - 1); };
const rmse = (a) => Math.sqrt(mean(a.map((x) => x * x)));
const pctl = (a, p) => { const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };
const corr = (x, y) => {
  const mx = mean(x), my = mean(y); let a = 0, b = 0, c = 0;
  x.forEach((v, i) => { a += (v - mx) * (y[i] - my); b += (v - mx) ** 2; c += (y[i] - my) ** 2; });
  return a / Math.sqrt(b * c);
};
const share = (a, f) => (a.length ? a.filter(f).length / a.length : NaN);

const LEVELS = { none: 0, low: 0.25, medium: 0.5, high: 0.75 };
const BANDS = { low: [0.18, 0.32], medium: [0.42, 0.58], high: [0.68, 0.85] };

// stance of a Characteristic = highest severity among the Profiles the person holds that list it; -0.2 otherwise
function stanceFrom(profiles, chIds, severities, base, idio, r) {
  const stance = {};
  chIds.forEach((c) => {
    let m = null;
    profiles.forEach((p, j) => { if (severities[j] > 0 && p.characteristics.includes(c)) m = m === null ? severities[j] : Math.max(m, severities[j]); });
    stance[c] = clamp((base ? base(c) : (m === null ? -0.2 : m)) + (idio ? idio * gauss(r) : 0));
  });
  return stance;
}
const toScale = (q, x) => { const y = Math.round((clamp(x) + 1) * 2) / 2 - 1; return q.answer === 'frequency' ? (y + 1) / 2 : y; };

// Standard respondent: nominal level per Profile (0 = none), small variation, 3% skips.
function simplePerson({ profiles, chIds, nominal, seed, noise = 1 }) {
  const pr = rng(1000 + seed), ar = rng(900000 + seed);
  const sev = nominal.map((n) => (n > 0 ? clamp(n + 0.05 * gauss(pr), 0.05, 1) : 0));
  const stance = stanceFrom(profiles, chIds, sev, null, 0, pr);
  const quirk = {}; chIds.forEach((c) => { quirk[c] = 0.2 * gauss(pr); });
  const answer = (q) => {
    if (ar() < 0.03) return null;
    const x = Math.sign(q.main.weight) * (stance[q.main.id] + quirk[q.main.id]) + noise * 0.25 * gauss(ar);
    return toScale(q, x);
  };
  return { nominal, stance, quirk, answer, seed, noise };
}

// Archetypes for the stress test. Profiles are taken from the registry, so new Profiles are covered automatically.
function archetypes(profiles, domains, chIds, chDomain) {
  const P = profiles.length;
  const inDomain = (d) => new Set(chIds.filter((c) => chDomain[c] === d));
  const bandLevels = (r, idxs, bands) => profiles.map((_, j) => (idxs.includes(j) ? U(r, ...BANDS[pick(r, bands)]) : 0));
  const some = (r, k) => { const idx = profiles.map((_, j) => j).sort(() => r() - 0.5).slice(0, Math.min(k, P)); return profiles.map((_, j) => (idx.includes(j) ? U(r, 0.1, 0.9) : 0)); };
  const zero = () => profiles.map(() => 0);
  const single = (band) => (r, i) => { const t = i % P; return { levels: bandLevels(r, [t], [band]), target: t, band }; };
  return [
    // group, name, weight, build(r, indexWithinArchetype) -> spec
    ['honest', 'neurotypical', 6, () => ({ levels: zero() })],
    ['honest', 'single_low', 8, single('low')],
    ['honest', 'single_medium', 8, single('medium')],
    ['honest', 'single_high', 8, single('high')],
    ['honest', 'double_mixed', 14, (r) => ({ levels: some(r, 2) })],
    ['honest', 'triple_mixed', 10, (r) => ({ levels: some(r, 3) })],
    ['honest', 'all_profiles_mixed', 6, (r) => ({ levels: some(r, P) })],
    ['honest', 'one_domain_pocket', 4, (r) => { const d = pick(r, domains); const cs = inDomain(d); const h = U(r, 0.6, 0.95); return { levels: zero(), stance: (c) => (cs.has(c) ? h : -0.2) }; }],
    ['honest', 'pattern_matches_none', 4, (r) => ({ levels: zero(), stance: () => U(r, -0.6, 0.9) })],
    ['distorted', 'masker', 4, (r) => ({ levels: some(r, 2), mask: true })],
    ['distorted', 'contrarian', 3, (r) => ({ levels: some(r, 3), invert: true })],
    ['distorted', 'extreme_responder', 3, (r) => ({ levels: some(r, 3), extreme: true })],
    ['distorted', 'fatigue', 3, (r) => ({ levels: some(r, 3), fatigue: true })],
    ['distorted', 'skipper', 3, (r) => ({ levels: some(r, 2), skip: U(r, 0.4, 0.7) })],
    ['distorted', 'flip_flopper', 3, (r) => ({ levels: some(r, 2), flip: 0.3 })],
    ['invalid', 'random_answers', 4, () => ({ levels: zero(), fixed: 'random' })],
    ['invalid', 'yes_sayer', 3, () => ({ levels: zero(), fixed: 0.9 })],
    ['invalid', 'no_sayer', 2, () => ({ levels: zero(), fixed: -0.9 })],
    ['invalid', 'midpoint', 2, () => ({ levels: zero(), fixed: 0 })],
    ['invalid', 'straight_line', 2, (r) => ({ levels: zero(), fixed: pick(r, [-1, -0.5, 0.5, 1]), exact: true })],
  ];
}

// Stress respondent: per-person noise, acquiescence, skips and the distortions of the archetype.
function stressPerson({ profiles, chIds, chDomain, spec, seed, noiseScale = 1 }) {
  const pr = rng(seed * 100003 + 11), ar = rng(seed * 7919 + 500000);
  const idio = U(pr, 0.2, 0.45);
  const stance = stanceFrom(profiles, chIds, spec.levels, spec.stance, idio, pr);
  const ans = {};
  chIds.forEach((c) => {
    let s = stance[c];
    if (spec.mask && ['social_communication', 'emotional_experience', 'adaptation_environment'].includes(chDomain[c])) s *= 0.35;
    if (spec.invert) s = -s;
    ans[c] = s;
  });
  const noise = U(pr, 0.2, 0.65) * noiseScale, acq = 0.12 * gauss(pr), skip = spec.skip ?? U(pr, 0, 0.08);
  let k = 0;
  const answer = (q) => {
    k++;
    if (ar() < skip) return null;
    let x;
    if (spec.fixed === 'random') x = U(ar, -1, 1);
    else if (spec.fixed !== undefined) x = spec.exact ? spec.fixed : spec.fixed + 0.15 * gauss(ar);
    else {
      const Wq = q.characteristics.reduce((s, z) => s + Math.abs(z.weight), 0);
      const blend = q.characteristics.reduce((s, z) => s + z.weight * ans[z.id], 0) / Wq;
      const base = 0.7 * ans[q.main.id] * Math.sign(q.main.weight) + 0.3 * blend;
      const fat = spec.fatigue ? 1 + 3 * Math.max(0, (k - 80) / 120) : 1;
      x = base + acq + noise * fat * gauss(ar);
      if (spec.flip && ar() < spec.flip) x = -x;
      if (spec.extreme) x = Math.abs(x) < 0.1 ? 0 : Math.sign(x);
    }
    return toScale(q, x);
  };
  return { stance, answer };
}

module.exports = { rng, gauss, clamp, U, pick, mean, sd, variance, rmse, pctl, corr, share, LEVELS, BANDS, simplePerson, stressPerson, archetypes };
