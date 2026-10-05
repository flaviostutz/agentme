export type Output = {
  out: (text: string) => void;
  err: (text: string) => void;
};

export type HttpResult = {
  status: number;
  location: string | undefined;
  contentType: string | undefined;
  // Undefined when the status is not 200 or the body was larger than the requested limit.
  bytes: Uint8Array | undefined;
};

// Outbound connector for credential-less reads; redirects are never followed automatically.
export type HttpPort = {
  get: (url: string, maxBytes: number) => Promise<HttpResult>;
};

// Outbound connector that resolves a host name to its IP addresses.
export type DnsPort = {
  lookup: (host: string) => Promise<string[]>;
};

export type Deps = {
  http: HttpPort;
  dns: DnsPort;
  output: Output;
};
