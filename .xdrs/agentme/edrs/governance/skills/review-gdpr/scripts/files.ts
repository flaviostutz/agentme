import { execFileSync } from 'node:child_process';
import * as fs from 'node:fs';
import path from 'node:path';

export const ALWAYS_SKIPPED_DIRS: ReadonlySet<string> = new Set([
  'node_modules',
  '.git',
  '.tmp',
  'dist',
  'build',
  'coverage',
]);

type IgnoreRule = { readonly regex: RegExp; readonly dirOnly: boolean; readonly anchored: boolean };

const globToRegExp = (glob: string): string => {
  let out = '';
  for (let index = 0; index < glob.length; index += 1) {
    const char = glob.charAt(index);
    if (char === '*' && glob.startsWith('**/', index)) {
      out += '(?:.*/)?';
      index += 2;
    } else if (char === '*' && glob.charAt(index + 1) === '*') {
      out += '.*';
      index += 1;
    } else if (char === '*') {
      out += '[^/]*';
    } else if (char === '?') {
      out += '[^/]';
    } else {
      out += char.replaceAll(/[$()+.[\\\]^{|}]/gu, String.raw`\$&`);
    }
  }
  return out;
};

// Basic .gitignore support for the non-git fallback: comments, `dir/`, `/anchored`, `*`, `**`, `?`. Negations are ignored.
export const parseGitignore = (text: string): IgnoreRule[] =>
  text
    .split(/\r?\n/u)
    .map((line) => line.trim())
    .filter((line) => line !== '' && !line.startsWith('#') && !line.startsWith('!'))
    .map((line) => {
      const dirOnly = line.endsWith('/');
      const body = dirOnly ? line.slice(0, -1) : line;
      const anchored = body.includes('/');
      return {
        regex: new RegExp(`^${globToRegExp(body.replace(/^\//u, ''))}$`, 'u'),
        dirOnly,
        anchored,
      };
    });

const isIgnored = (rules: readonly IgnoreRule[], relative: string, isDirectory: boolean): boolean =>
  rules.some(
    (rule) =>
      (!rule.dirOnly || isDirectory) &&
      rule.regex.test(rule.anchored ? relative : path.posix.basename(relative)),
  );

const readIgnoreRules = (dir: string): IgnoreRule[] => {
  try {
    return parseGitignore(fs.readFileSync(path.join(dir, '.gitignore'), 'utf8'));
  } catch {
    return [];
  }
};

const walk = (root: string): string[] => {
  const rules = readIgnoreRules(root);
  const found: string[] = [];
  const visit = (relativeDir: string): void => {
    let entries: fs.Dirent[] = [];
    try {
      entries = fs.readdirSync(path.join(root, relativeDir), { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const relative = relativeDir === '' ? entry.name : `${relativeDir}/${entry.name}`;
      if (entry.isDirectory()) {
        if (!ALWAYS_SKIPPED_DIRS.has(entry.name) && !isIgnored(rules, relative, true))
          visit(relative);
      } else if (!isIgnored(rules, relative, false)) {
        found.push(relative);
      }
    }
  };
  visit('');
  return found;
};

const gitList = (dir: string): string[] | undefined => {
  try {
    const output = execFileSync(
      'git',
      ['ls-files', '-z', '--cached', '--others', '--exclude-standard'],
      {
        cwd: dir,
        encoding: 'utf8',
        maxBuffer: 512 * 1024 * 1024,
        stdio: ['ignore', 'pipe', 'ignore'],
      },
    );
    return output.split('\0').filter((item) => item !== '');
  } catch {
    return undefined;
  }
};

const exists = (dir: string, relative: string): boolean => {
  try {
    return !fs.lstatSync(path.join(dir, relative)).isDirectory();
  } catch {
    return false;
  }
};

// Relative POSIX paths, sorted. Uses git when dir is inside a work tree, otherwise a manual walk.
export const listFiles = (dir: string): string[] => {
  const viaGit = gitList(dir);
  const candidates =
    viaGit === undefined ? walk(dir) : viaGit.filter((relative) => exists(dir, relative));
  return [...new Set(candidates)]
    .filter(
      (relative) =>
        !relative
          .split('/')
          .slice(0, -1)
          .some((segment) => ALWAYS_SKIPPED_DIRS.has(segment)),
    )
    .sort();
};
