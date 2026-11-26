import * as fs from 'node:fs';

export type Keywords = { readonly pii: readonly string[]; readonly special: readonly string[] };

// Multi-word keywords use `_` between words; matching ignores case, accents and word separators.
export const DEFAULT_KEYWORDS: Keywords = {
  pii: [
    // English
    'email',
    'phone',
    'telephone',
    'mobile_number',
    'address',
    'street',
    'postcode',
    'zip_code',
    'postal_code',
    'birth_date',
    'date_of_birth',
    'dob',
    'birthday',
    'ssn',
    'social_security',
    'passport',
    'national_id',
    'tax_id',
    'driver_license',
    'drivers_license',
    'ip_address',
    'first_name',
    'last_name',
    'full_name',
    'surname',
    'username',
    'device_id',
    'cookie_id',
    'advertising_id',
    'iban',
    'credit_card',
    'card_number',
    // Portuguese
    'nome',
    'sobrenome',
    'nascimento',
    'data_nascimento',
    'cpf',
    'telefone',
    'celular',
    'endereco',
    // Spanish
    'nombre',
    'apellido',
    'nacimiento',
    'fecha_nacimiento',
    'telefono',
    'direccion',
    'dni',
    'correo',
    // French
    'nom',
    'prenom',
    'naissance',
    'adresse',
    'courriel',
    // German
    'vorname',
    'nachname',
    'geburtsdatum',
    'geburtstag',
    'anschrift',
    'telefonnummer',
    'strasse',
    'steuernummer',
    'sozialversicherungsnummer',
  ],
  special: [
    // English
    'health',
    'medical',
    'diagnosis',
    'religion',
    'ethnicity',
    'biometric',
    'genetic',
    'sexual_orientation',
    'trade_union',
    'union_membership',
    'political',
    'disability',
    'criminal_record',
    'conviction',
    // Portuguese
    'saude',
    'diagnostico',
    'religiao',
    'etnia',
    'biometria',
    'orientacao_sexual',
    'sindicato',
    'politico',
    // Spanish
    'salud',
    'biometrico',
    'orientacion_sexual',
    // French
    'sante',
    'diagnostic',
    'ethnie',
    'biometrique',
    'orientation_sexuelle',
    'syndicat',
    'politique',
    // German
    'gesundheit',
    'diagnose',
    'biometrisch',
    'sexuelle_orientierung',
    'gewerkschaft',
    'politisch',
  ],
};

type Compiled = { readonly label: string; readonly words: readonly string[] };
export type KeywordMatcher = {
  readonly pii: (line: string) => string[];
  readonly special: (line: string) => string[];
};

const IDENTIFIER = /[\p{L}_][\p{L}\p{N}_-]*/gu;

const strip = (value: string): string => value.normalize('NFD').replaceAll(/\p{M}/gu, '');

// Splits an identifier into lowercase words on separators, camelCase and acronym boundaries.
export const splitWords = (identifier: string): string[] =>
  strip(identifier)
    .replaceAll(/([a-z\d])([A-Z])/gu, '$1 $2')
    .replaceAll(/([A-Z]+)([A-Z][a-z])/gu, '$1 $2')
    .split(/[^A-Za-z\d]+/u)
    .filter((word) => word !== '')
    .map((word) => word.toLowerCase());

const compile = (keywords: readonly string[]): Compiled[] =>
  keywords
    .map((label) => ({ label, words: splitWords(label) }))
    .filter((item) => item.words.length > 0);

const wordEquals = (word: string, expected: string, last: boolean): boolean =>
  word === expected || (last && word === `${expected}s`);

const containsSequence = (words: readonly string[], expected: readonly string[]): boolean =>
  words.some((_, start) =>
    expected.every((item, offset) =>
      wordEquals(words[start + offset] ?? '', item, offset === expected.length - 1),
    ),
  );

// "health" next to these words is a service health check, not health data.
const HEALTH_CHECK_WORDS = new Set([
  'check',
  'checks',
  'probe',
  'endpoint',
  'ready',
  'readiness',
  'liveness',
]);

const identifierMatches = (words: readonly string[], item: Compiled): boolean => {
  if (item.label === 'health' && words.some((word) => HEALTH_CHECK_WORDS.has(word))) return false;
  return containsSequence(words, item.words) || words.join('') === item.words.join('');
};

const matchLine = (compiled: readonly Compiled[], line: string): string[] => {
  const identifiers = (line.match(IDENTIFIER) ?? []).map((identifier) => splitWords(identifier));
  const labels = compiled
    .filter((item) => identifiers.some((words) => identifierMatches(words, item)))
    .map((item) => item.label);
  return [...new Set(labels)].sort();
};

export const createMatcher = (keywords: Keywords): KeywordMatcher => {
  const pii = compile(keywords.pii);
  const special = compile(keywords.special);
  return { pii: (line) => matchLine(pii, line), special: (line) => matchLine(special, line) };
};

const stringList = (value: unknown, key: string): string[] => {
  if (value === undefined) return [];
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'string')) {
    throw new TypeError(`keywords file: "${key}" must be an array of strings`);
  }
  return value as string[];
};

// Reads a JSON file `{ "pii": [], "special": [] }` that extends the defaults.
export const loadKeywords = (file: string | undefined): Keywords => {
  if (file === undefined) return DEFAULT_KEYWORDS;
  let parsed: unknown;
  try {
    parsed = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (error) {
    throw new TypeError(`keywords file cannot be read as JSON: ${(error as Error).message}`);
  }
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    throw new TypeError('keywords file must contain a JSON object');
  }
  const record = parsed as Record<string, unknown>;
  return {
    pii: [...DEFAULT_KEYWORDS.pii, ...stringList(record['pii'], 'pii')],
    special: [...DEFAULT_KEYWORDS.special, ...stringList(record['special'], 'special')],
  };
};

export type PatternRule = { readonly name: string; readonly pattern: RegExp };

export const TRACKER_RULES: readonly PatternRule[] = [
  {
    name: 'google-analytics',
    pattern: /google-analytics|googleanalytics|\bgtag\b|googletagmanager|\bga\('create'/iu,
  },
  {
    name: 'segment',
    pattern: /@segment\/|analytics-node|cdn\.segment\.com|segment\.io|segment\.com/iu,
  },
  { name: 'mixpanel', pattern: /mixpanel/iu },
  { name: 'amplitude', pattern: /amplitude/iu },
  { name: 'hotjar', pattern: /hotjar/iu },
  {
    name: 'facebook-pixel',
    pattern: /\bfbq\(|connect\.facebook\.net|fbevents|facebook[-_ ]?pixel/iu,
  },
  {
    name: 'sentry-session-replay',
    pattern: /@sentry\/replay|replayIntegration|replaysSessionSampleRate|replaysOnErrorSampleRate/u,
  },
  { name: 'doubleclick', pattern: /doubleclick/iu },
  { name: 'fullstory', pattern: /fullstory/iu },
  { name: 'posthog', pattern: /posthog/iu },
  { name: 'matomo', pattern: /matomo|piwik/iu },
  { name: 'microsoft-clarity', pattern: /clarity\.ms/iu },
  { name: 'heap', pattern: /heapanalytics|heap\.load/iu },
  { name: 'datadog-rum', pattern: /@datadog\/browser-rum/iu },
  { name: 'linkedin-insight', pattern: /snap\.licdn\.com|_linkedin_partner_id/iu },
  { name: 'tiktok-pixel', pattern: /analytics\.tiktok\.com|ttq\.load/iu },
];

export const LLM_RULES: readonly PatternRule[] = [
  { name: 'openai', pattern: /openai/iu },
  { name: 'anthropic', pattern: /anthropic/iu },
  { name: 'langchain', pattern: /langchain|langgraph/iu },
  { name: 'bedrock', pattern: /bedrock/iu },
  { name: 'vertex-ai', pattern: /vertex[-_ ]?ai|aiplatform/iu },
  {
    name: 'google-generative-ai',
    pattern: /@google\/generative-ai|google-genai|generativelanguage/iu,
  },
  { name: 'cohere', pattern: /\bcohere\b/iu },
  { name: 'mistral', pattern: /mistralai/iu },
  { name: 'huggingface', pattern: /huggingface|hugging-face/iu },
  { name: 'llamaindex', pattern: /llama[-_]?index/iu },
  { name: 'litellm', pattern: /litellm/iu },
  { name: 'ollama', pattern: /\bollama\b/iu },
];

const REGION_PATTERN =
  /\b(?:(?:us|eu|ap|sa|ca|me|af|il|cn)-(?:north|south|east|west|central|northeast|southeast|northwest|southwest|gov)-\d|europe-[a-z]+\d+|asia-[a-z]+\d+|us-(?:central|east|west)\d|(?:west|north|south|east|central)europe|(?:east|west|central|northcentral|southcentral)us\d?|southeastasia|eastasia)\b/gu;

export const findRegionStrings = (line: string): string[] =>
  [...new Set(line.match(REGION_PATTERN) ?? [])].sort();

export const REGION_KEY = /\bregion["']?\s*[:=]/iu;

export const LOG_CALL =
  /\b(?:console\.\w+|loggers?\.\w+|logging\.\w+|log\.\w+|slog\.\w+|fmt\.Print\w*|System\.out\.print\w*)\s*\(|\b(?:print|println|printf|puts|echo)\b/u;
