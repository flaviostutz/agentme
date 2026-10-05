import {
  browserIdFromVersion,
  findNonceTarget,
  nonceStartUrl,
  pageTargets,
  parseState,
  serializeState,
} from './state';

describe('session state', () => {
  it('round-trips and applies defaults', () => {
    const state = {
      port: 9390,
      browserId: 'abc-1',
      user: 'me@example.com',
      tabId: 'T1',
      baseline: ['B1'],
    };
    expect(parseState(serializeState(state))).toEqual(state);
    expect(parseState(serializeState({ port: 9231, browserId: 'x' }))).toEqual({
      port: 9231,
      browserId: 'x',
      user: '',
    });
  });

  it('rejects bad input and drops wrongly typed fields', () => {
    expect(parseState('not json')).toBeUndefined();
    expect(parseState('null')).toBeUndefined();
    expect(parseState('{"port":"9390","browserId":"x"}')).toBeUndefined();
    expect(parseState('{"port":1,"browserId":"x","user":5,"tabId":7,"baseline":["a",3]}')).toEqual({
      port: 1,
      browserId: 'x',
      user: '',
      baseline: ['a'],
    });
  });
});

describe('browserIdFromVersion', () => {
  it('reads the browser websocket id', () => {
    expect(
      browserIdFromVersion({ webSocketDebuggerUrl: 'ws://127.0.0.1:9390/devtools/browser/1a-2b' }),
    ).toBe('1a-2b');
    expect(browserIdFromVersion({})).toBeUndefined();
  });
});

describe('nonce targets', () => {
  it('finds the nonce start page only on page targets', () => {
    const url = nonceStartUrl('n0nce');
    expect(url).toMatch(/^data:/);
    const targets = [
      { type: 'other', url, targetId: 'O' },
      { type: 'page', url: 'edge://newtab/', targetId: 'A' },
      { type: 'page', url, targetId: 'B' },
    ];
    expect(findNonceTarget(targets, 'n0nce')?.targetId).toBe('B');
    expect(findNonceTarget(targets, 'other')).toBeUndefined();
    expect(pageTargets(targets).map((target) => target.targetId)).toEqual(['A', 'B']);
  });
});
