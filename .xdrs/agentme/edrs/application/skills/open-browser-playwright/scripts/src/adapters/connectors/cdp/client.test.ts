import { connectCdp } from './client';
import { FakeWebSocket, installFakeWebSocket } from './websocket_mock';

describe('connectCdp', () => {
  let restore: () => void;

  beforeEach(() => {
    restore = installFakeWebSocket();
  });

  afterEach(() => {
    restore();
    jest.useRealTimers();
  });

  it('sends commands and resolves with the result', async () => {
    const seen: string[] = [];
    FakeWebSocket.handler = (method, params) => {
      seen.push(`${method}:${JSON.stringify(params)}`);
      return { ok: true };
    };
    const cdp = await connectCdp('ws://127.0.0.1:1/devtools/browser/x');
    await expect(cdp.send('Target.getTargets')).resolves.toEqual({ ok: true });
    await expect(cdp.send('Runtime.evaluate', { expression: '1' }, 'S1')).resolves.toEqual({
      ok: true,
    });
    expect(seen).toEqual(['Target.getTargets:{}', 'Runtime.evaluate:{"expression":"1"}']);
    cdp.close();
  });

  it('rejects when the browser answers with an error', async () => {
    FakeWebSocket.handler = () => new Error('boom');
    const cdp = await connectCdp('ws://127.0.0.1:1/x');
    await expect(cdp.send('Bad.method')).rejects.toThrow('boom');
  });

  it('rejects when the connection cannot be opened', async () => {
    FakeWebSocket.failConnect = true;
    await expect(connectCdp('ws://127.0.0.1:1/x')).rejects.toThrow('cannot connect');
  });

  it('rejects pending calls when the connection closes', async () => {
    FakeWebSocket.handler = () => 'silent';
    const cdp = await connectCdp('ws://127.0.0.1:1/x');
    const pending = cdp.send('Never.answered');
    cdp.close();
    await expect(pending).rejects.toThrow('CDP connection closed');
  });

  it('rejects calls that never get an answer', async () => {
    jest.useFakeTimers();
    FakeWebSocket.handler = () => 'silent';
    const connecting = connectCdp('ws://127.0.0.1:1/x');
    await jest.advanceTimersByTimeAsync(0);
    const cdp = await connecting;
    const outcome = expect(cdp.send('Slow.method')).rejects.toThrow('timed out');
    await jest.advanceTimersByTimeAsync(15_000);
    await outcome;
  });
});
