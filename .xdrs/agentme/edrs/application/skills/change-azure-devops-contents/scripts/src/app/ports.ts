export type Output = {
  out: (text: string) => void;
  err: (text: string) => void;
};

// Outbound connector to the Azure CLI; returns stdout and throws with the CLI stderr on failure.
export type AzPort = {
  run: (args: readonly string[]) => string;
};

// Outbound connector that reads the items JSON from a file, or from stdin when no file is given.
export type InputPort = {
  read: (file: string | undefined) => string;
};

// Outbound connector that hands a request body to the CLI as a file, so no text goes through a shell.
export type BodyFilePort = {
  withFile: <T>(content: string, use: (file: string) => T) => T;
};

// Outbound connector that turns markdown into the HTML Azure DevOps stores; undefined when no converter is installed.
export type MarkdownPort = {
  toHtml: (markdown: string) => string | undefined;
};

export type Deps = {
  az: AzPort;
  input: InputPort;
  bodyFile: BodyFilePort;
  markdown: MarkdownPort;
  output: Output;
};
