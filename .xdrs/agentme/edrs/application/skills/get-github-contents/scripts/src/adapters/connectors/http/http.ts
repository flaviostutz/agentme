import type { HttpPort } from '../../../app/ports';

const readLimited = async (
  response: Response,
  maxBytes: number,
): Promise<Uint8Array | undefined> => {
  const declared = Number(response.headers.get('content-length') ?? 0);
  if (declared > maxBytes) return undefined;
  const buffer = new Uint8Array(await response.arrayBuffer());
  return buffer.byteLength > maxBytes ? undefined : buffer;
};

// Plain GET with no credentials and no automatic redirects.
export const httpConnector: HttpPort = {
  get: async (url, maxBytes) => {
    const response = await fetch(url, { redirect: 'manual', signal: AbortSignal.timeout(30_000) });
    const ok = response.status === 200;
    return {
      status: response.status,
      location: response.headers.get('location') ?? undefined,
      contentType: response.headers.get('content-type') ?? undefined,
      bytes: ok ? await readLimited(response, maxBytes) : undefined,
    };
  },
};
