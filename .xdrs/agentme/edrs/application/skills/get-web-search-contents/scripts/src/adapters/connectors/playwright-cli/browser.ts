import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

import type { BrowserPort } from '../../../app/ports';
import { ExitError } from '../../../shared/errors';

const PLAYWRIGHT_CLI = '@playwright/cli@0.1.22';
const NOT_OPEN = /is not open/i;
const TAB_LINE = /^- (\d+): (\(current\) )?\[(.*)\]\((.*)\)$/;
const COMMAND_TIMEOUT_MS = 60_000;

type Tab = { index: number; current: boolean; url: string };

const execFileAsync = promisify(execFile);

export type Runner = (session: string, args: readonly string[]) => Promise<string>;

const run: Runner = async (session: string, args: readonly string[]): Promise<string> => {
  const { stdout } = await execFileAsync(
    'npx',
    ['-y', `--package=${PLAYWRIGHT_CLI}`, 'playwright-cli', `-s=${session}`, ...args],
    { timeout: COMMAND_TIMEOUT_MS, maxBuffer: 16 * 1024 * 1024 },
  );
  return stdout;
};

const parseTabs = (output: string): Tab[] =>
  output.split('\n').flatMap((line) => {
    const match = TAB_LINE.exec(line.trim());
    return match
      ? [{ index: Number(match[1]), current: match[2] !== undefined, url: match[4] ?? '' }]
      : [];
  });

// playwright-cli reports failures on stdout with exit code 0.
const failOnError = (output: string): string => {
  const first = output.trimStart().split('\n')[0] ?? '';
  if (first.startsWith('Error:'))
    throw new Error(`browser page call failed: ${first.slice(0, 200)}`);
  return output;
};

// Talks to the browser opened by open-browser-playwright over its CDP port; it never opens or quits the browser.
export const playwrightCliBrowser = (
  name: string,
  cdpPort: number,
  exec: Runner = run,
): BrowserPort => {
  const session = `${name}-attach`;
  const tabs = async (): Promise<Tab[]> => parseTabs(await exec(session, ['tab-list']));
  return {
    ensureSession: async (): Promise<void> => {
      const listed = await exec(session, ['tab-list']);
      if (!NOT_OPEN.test(listed)) return;
      await exec(session, ['attach', `--cdp=http://127.0.0.1:${cdpPort}`]);
      if (NOT_OPEN.test(await exec(session, ['tab-list']))) {
        throw new ExitError(
          1,
          `cannot reach the browser on port ${cdpPort}; open it first with open-browser-playwright`,
        );
      }
    },
    openTab: async (url): Promise<number> => {
      const opened = parseTabs(failOnError(await exec(session, ['tab-new', url]))).find(
        (tab) => tab.current,
      );
      if (!opened) throw new Error('could not read the new tab index');
      return opened.index;
    },
    findTab: async (urlPart): Promise<number | undefined> => {
      const open = await tabs();
      return open.find((tab) => tab.url.includes(urlPart))?.index;
    },
    selectTab: async (index): Promise<void> => {
      failOnError(await exec(session, ['tab-select', String(index)]));
    },
    closeTab: async (index): Promise<void> => {
      failOnError(await exec(session, ['tab-close', String(index)]));
    },
    evalJson: async (call): Promise<unknown> => {
      const output = await exec(session, ['--raw', 'eval', `() => ${call.source}`]);
      return JSON.parse(failOnError(output).trim() || 'null');
    },
    fillAndSubmit: async (selector, text): Promise<void> => {
      const code = `async page => { await page.locator(${JSON.stringify(selector)}).fill(${JSON.stringify(text)}); await page.keyboard.press('Enter'); }`;
      failOnError(await exec(session, ['run-code', code]));
    },
  };
};
