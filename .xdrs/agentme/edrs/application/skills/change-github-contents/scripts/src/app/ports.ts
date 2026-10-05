export type Output = {
  out: (text: string) => void;
  err: (text: string) => void;
};

// Outbound connector to the GitHub CLI; returns stdout and throws with the CLI stderr on failure.
export type GhPort = {
  run: (args: readonly string[]) => string;
};

// Outbound connector that reads the items JSON from a file, or from stdin when no file is given.
export type InputPort = {
  read: (file: string | undefined) => string;
};

export type Deps = {
  gh: GhPort;
  input: InputPort;
  output: Output;
};
