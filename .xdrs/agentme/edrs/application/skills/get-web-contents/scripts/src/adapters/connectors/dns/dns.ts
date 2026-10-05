import { lookup } from 'node:dns/promises';

import type { DnsPort } from '../../../app/ports';

export const dnsConnector: DnsPort = {
  lookup: async (host) => {
    const entries = await lookup(host, { all: true });
    return entries.map((entry) => entry.address);
  },
};
