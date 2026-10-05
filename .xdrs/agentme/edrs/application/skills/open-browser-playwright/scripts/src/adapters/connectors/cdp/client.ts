import { COMMAND_TIMEOUT_MS } from '../../../shared/constants';
import type { Cdp, CdpResult } from '../../../shared/types';

type PendingCall = {
  resolve: (value: CdpResult) => void;
  reject: (reason: Error) => void;
  timer: ReturnType<typeof setTimeout>;
};

type CdpMessage = { id?: number; result?: CdpResult; error?: { message: string } };

// Minimal Chrome DevTools Protocol client over the global WebSocket (Node.js 22+).
export const connectCdp = async (wsUrl: string): Promise<Cdp> =>
  new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    const pending = new Map<number, PendingCall>();
    let nextId = 1;

    const client: Cdp = {
      send: async (method, params = {}, sessionId?) =>
        new Promise<CdpResult>((resolveCall, rejectCall) => {
          const id = nextId;
          nextId += 1;
          const timer = setTimeout(() => {
            pending.delete(id);
            rejectCall(new Error(`CDP ${method} timed out`));
          }, COMMAND_TIMEOUT_MS);
          pending.set(id, { resolve: resolveCall, reject: rejectCall, timer });
          ws.send(
            JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params }),
          );
        }),
      close: () => {
        ws.close();
      },
    };

    ws.addEventListener('open', (): void => {
      resolve(client);
    });
    ws.addEventListener('error', (): void => {
      reject(new Error(`cannot connect to ${wsUrl}`));
    });
    ws.addEventListener('message', (event): void => {
      const message = JSON.parse(String(event.data)) as CdpMessage;
      const call = typeof message.id === 'number' ? pending.get(message.id) : undefined;
      if (!call || typeof message.id !== 'number') return;
      pending.delete(message.id);
      clearTimeout(call.timer);
      if (message.error) call.reject(new Error(message.error.message));
      else call.resolve(message.result ?? {});
    });
    ws.addEventListener('close', (): void => {
      for (const call of pending.values()) {
        clearTimeout(call.timer);
        call.reject(new Error('CDP connection closed'));
      }
      pending.clear();
    });
  });
