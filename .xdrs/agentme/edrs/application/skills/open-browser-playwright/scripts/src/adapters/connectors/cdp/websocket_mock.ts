// Reusable fake of the global WebSocket: replies to every JSON-RPC message through a scriptable handler.
export type FakeHandler = (
  method: string,
  params: Record<string, unknown>,
) => Record<string, unknown> | Error | 'silent';

type Listener = (event: { data: string }) => void;

export class FakeWebSocket {
  static handler: FakeHandler = (): Record<string, unknown> => ({});

  static failConnect = false;

  private readonly listeners = new Map<string, Listener[]>();

  constructor(readonly url: string) {
    setTimeout((): void => {
      this.emit(FakeWebSocket.failConnect ? 'error' : 'open', '');
    }, 0);
  }

  addEventListener(type: string, listener: Listener): void {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  send(data: string): void {
    const message = JSON.parse(data) as {
      id: number;
      method: string;
      params: Record<string, unknown>;
    };
    const reply = FakeWebSocket.handler(message.method, message.params);
    if (reply === 'silent') return;
    const payload =
      reply instanceof Error
        ? { id: message.id, error: { message: reply.message } }
        : { id: message.id, result: reply };
    setTimeout((): void => {
      this.emit('message', JSON.stringify(payload));
    }, 0);
  }

  close(): void {
    setTimeout((): void => {
      this.emit('close', '');
    }, 0);
  }

  private emit(type: string, data: string): void {
    for (const listener of this.listeners.get(type) ?? []) listener({ data });
  }
}

export const installFakeWebSocket = (): (() => void) => {
  const original = Object.getOwnPropertyDescriptor(globalThis, 'WebSocket');
  Object.defineProperty(globalThis, 'WebSocket', {
    value: FakeWebSocket,
    configurable: true,
    writable: true,
  });
  FakeWebSocket.handler = (): Record<string, unknown> => ({});
  FakeWebSocket.failConnect = false;
  return (): void => {
    if (original) Object.defineProperty(globalThis, 'WebSocket', original);
  };
};
