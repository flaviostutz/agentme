export type Output = {
  out: (text: string) => void;
  err: (text: string) => void;
};

// Outbound connector to the GitHub CLI; returns stdout and throws with the CLI stderr on failure.
export type GhPort = {
  run: (args: readonly string[]) => string;
};

export type HttpResult = {
  status: number;
  location: string | undefined;
  contentType: string | undefined;
  // Undefined when the body was larger than the requested limit.
  bytes: Uint8Array | undefined;
};

// Outbound connector for credential-less downloads; redirects are never followed automatically.
export type HttpPort = {
  get: (url: string, maxBytes: number) => Promise<HttpResult>;
};

export type FilesPort = {
  mkdirp: (dir: string) => void;
  write: (file: string, bytes: Uint8Array) => void;
};

export type Deps = {
  gh: GhPort;
  http: HttpPort;
  files: FilesPort;
  output: Output;
};
