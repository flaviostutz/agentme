import { playwrightCliBrowser, type Runner } from './browser';

const NOT_OPEN = "The browser 'x-attach' is not open, please run open first\n";
const TABS =
  '### Result\n- 0: [First](https://one.example/)\n- 1: (current) [AI](https://www.google.com/search?udm=50&q=x)\n';

const fake = (
  replies: (args: readonly string[]) => string,
): { exec: Runner; calls: string[][] } => {
  const calls: string[][] = [];
  return {
    calls,
    exec: async (_session, args) => {
      calls.push([...args]);
      return replies(args);
    },
  };
};

describe('playwrightCliBrowser', () => {
  it('attaches over the CDP port when the session is not open', async () => {
    let attached = false;
    const { exec, calls } = fake((args) => {
      if (args[0] === 'attach') {
        attached = true;
        return 'attached';
      }
      return attached ? TABS : NOT_OPEN;
    });
    await playwrightCliBrowser('x', 9231, exec).ensureSession();
    expect(calls.map((c) => c[0])).toEqual(['tab-list', 'attach', 'tab-list']);
    expect(calls[1]).toEqual(['attach', '--cdp=http://127.0.0.1:9231']);
  });

  it('does not attach again when the session is already open', async () => {
    const { exec, calls } = fake(() => TABS);
    await playwrightCliBrowser('x', 9231, exec).ensureSession();
    expect(calls).toEqual([['tab-list']]);
  });

  it('fails with a clear message when the browser cannot be reached', async () => {
    const { exec } = fake(() => NOT_OPEN);
    await expect(playwrightCliBrowser('x', 9231, exec).ensureSession()).rejects.toThrow(
      /cannot reach the browser on port 9231/,
    );
  });

  it('reads the new tab index from the current marker', async () => {
    const { exec, calls } = fake(() => TABS);
    expect(await playwrightCliBrowser('x', 1, exec).openTab('https://e.org/')).toBe(1);
    expect(calls[0]).toEqual(['tab-new', 'https://e.org/']);
  });

  it('fails when the new tab cannot be read', async () => {
    const { exec } = fake(() => '### Result\n');
    await expect(playwrightCliBrowser('x', 1, exec).openTab('https://e.org/')).rejects.toThrow(
      /new tab index/,
    );
  });

  it('finds a tab by URL text, selects and closes by index', async () => {
    const { exec, calls } = fake(() => TABS);
    const browser = playwrightCliBrowser('x', 1, exec);
    expect(await browser.findTab('udm=50')).toBe(1);
    expect(await browser.findTab('missing')).toBeUndefined();
    await browser.selectTab(1);
    await browser.closeTab(1);
    expect(calls.slice(-2)).toEqual([
      ['tab-select', '1'],
      ['tab-close', '1'],
    ]);
  });

  it('evaluates a page function and parses its JSON, including scalars', async () => {
    const replies = ['{\n  "a": 1\n}\n', '"text"\n', 'true\n'];
    const { exec, calls } = fake(() => replies.shift() ?? '');
    const browser = playwrightCliBrowser('x', 1, exec);
    const call = { name: 'f', source: '(() => 1)()' };
    expect(await browser.evalJson(call)).toEqual({ a: 1 });
    expect(await browser.evalJson(call)).toBe('text');
    expect(await browser.evalJson(call)).toBe(true);
    expect(calls[0]).toEqual(['--raw', 'eval', '() => (() => 1)()']);
  });

  it('turns a page error printed on stdout into a failure', async () => {
    const { exec } = fake(() => 'Error: x\n    at eval');
    await expect(
      playwrightCliBrowser('x', 1, exec).evalJson({ name: 'f', source: '(()=>1)()' }),
    ).rejects.toThrow(/page call failed: Error: x/);
  });

  it('fills the input with escaped text and presses Enter', async () => {
    const { exec, calls } = fake(() => '### Ran Playwright code\n```js\nawait page.x();\n```');
    await playwrightCliBrowser('x', 1, exec).fillAndSubmit('textarea', 'say "hi"\n');
    const code = calls[0]?.[1] ?? '';
    expect(calls[0]?.[0]).toBe('run-code');
    expect(code).toContain(String.raw`.fill("say \"hi\"\n")`);
    expect(code).toContain("press('Enter')");
  });

  it('fails when the fill reports an error', async () => {
    const { exec } = fake(() => 'Error: locator timeout');
    await expect(playwrightCliBrowser('x', 1, exec).fillAndSubmit('t', 'a')).rejects.toThrow(
      /page call failed/,
    );
  });
});
