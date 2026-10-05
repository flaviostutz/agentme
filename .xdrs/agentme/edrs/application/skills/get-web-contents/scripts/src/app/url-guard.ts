import { usageError } from '../shared/errors';

import type { DnsPort } from './ports';

const IPV4 = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
const BLOCKED_SUFFIXES = ['.localhost', '.local', '.internal', '.localdomain'];

const isPrivateIpv4 = (octets: readonly number[]): boolean => {
  const [a = 0, b = 0] = octets;
  return (
    a === 0 ||
    a === 10 ||
    a === 127 ||
    (a === 100 && b >= 64 && b <= 127) ||
    (a === 169 && b === 254) ||
    (a === 172 && b >= 16 && b <= 31) ||
    (a === 192 && b === 168) ||
    a >= 224
  );
};

const mappedIpv4 = (address: string): number[] | undefined => {
  const rest = address.slice('::ffff:'.length);
  const dotted = IPV4.exec(rest);
  if (dotted) return dotted.slice(1).map(Number);
  const hex = /^([0-9a-f]{1,4}):([0-9a-f]{1,4})$/.exec(rest);
  if (!hex) return undefined;
  const high = Number.parseInt(hex[1] ?? '0', 16);
  const low = Number.parseInt(hex[2] ?? '0', 16);
  return [high >> 8, high % 256, low >> 8, low % 256];
};

// True for loopback, link-local, private, shared, multicast and unspecified addresses.
export const isPrivateAddress = (raw: string): boolean => {
  const address = raw.replaceAll(/^\[|\]$/g, '').toLowerCase();
  const v4 = IPV4.exec(address);
  if (v4) return isPrivateIpv4(v4.slice(1).map(Number));
  if (address === '::' || address === '::1') return true;
  if (address.startsWith('::ffff:')) {
    const octets = mappedIpv4(address);
    return octets ? isPrivateIpv4(octets) : true;
  }
  const first = Number.parseInt(address.split(':')[0] || '0', 16);
  // fc00::/7 unique local, fe80::/10 link-local, ff00::/8 multicast (compared by their leading bits).
  return first >> 9 === 126 || first >> 6 === 1018 || first >> 8 === 255;
};

const isIpLiteral = (host: string): boolean => IPV4.test(host) || host.includes(':');

export const parseWebUrl = (raw: string): URL => {
  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    throw usageError(`not a valid URL: ${raw}`);
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw usageError(`only http and https URLs are supported: ${raw}`);
  }
  if (url.username || url.password) {
    throw usageError('URLs with embedded credentials are not supported');
  }
  return url;
};

// Returns the reason why a host must not be contacted, or undefined when it is allowed.
// `allowedPrivateHost` is the one private host the human typed on purpose.
export const blockedReason = async (
  host: string,
  dns: DnsPort,
  allowedPrivateHost: string | undefined,
): Promise<string | undefined> => {
  const name = host.replaceAll(/^\[|\]$/g, '').toLowerCase();
  if (name === allowedPrivateHost) return undefined;
  if (name === 'localhost' || BLOCKED_SUFFIXES.some((suffix) => name.endsWith(suffix))) {
    return `${name} is a local host name`;
  }
  const addresses = isIpLiteral(name) ? [name] : await dns.lookup(name);
  const bad = addresses.find((address) => isPrivateAddress(address));
  return bad === undefined ? undefined : `${name} resolves to the private address ${bad}`;
};
