export const SKILL_PORT_MIN = 9230;
export const SKILL_PORT_MAX = 9389;
export const AUTO_PORT_MIN = 9390;
export const AUTO_PORT_MAX = 9399;
export const DEFAULT_SIZE = '1300x900';
export const DEFAULT_CHECK_URL = 'https://myaccount.microsoft.com/?ref=MeControl';
export const DEFAULT_SSO_WAIT_SECONDS = 45;
export const DEFAULT_WAIT_SECONDS = 300;
export const SUBCOMMANDS = ['wait', 'tidy'];

export const CDP_STARTUP_MS = 15_000;
export const COMMAND_TIMEOUT_MS = 15_000;
export const RENAVIGATE_MS = 5000;

// Caches are large and session-restore files would reopen the user's own tabs (with live tokens).
export const PROFILE_EXCLUDES = new Set([
  'Cache',
  'Code Cache',
  'GPUCache',
  'GrShaderCache',
  'ShaderCache',
  'DawnGraphiteCache',
  'DawnWebGPUCache',
  'component_crx_cache',
  'Service Worker',
  'WebStorage',
  'Snapshots',
  'SingletonLock',
  'SingletonCookie',
  'SingletonSocket',
  'Sessions',
  'Current Session',
  'Current Tabs',
  'Last Session',
  'Last Tabs',
  'EdgeSessions',
]);
export const SESSION_RESTORE_FILES = [
  'Sessions',
  'Current Session',
  'Current Tabs',
  'Last Session',
  'Last Tabs',
  'EdgeSessions',
];
export const SINGLETON_FILES = ['SingletonLock', 'SingletonCookie', 'SingletonSocket'];

export const USAGE = [
  'Usage:',
  '  open-browser <session> <url> [WIDTHxHEIGHT] [--cdp-port=N]',
  '  open-browser wait <session> <url> [seconds]',
  '  open-browser tidy <session>',
].join('\n');
