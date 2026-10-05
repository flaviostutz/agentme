export type Output = {
  out: (text: string) => void;
  err: (text: string) => void;
};

// Outbound connector to the Azure CLI; returns stdout and throws with the CLI stderr on failure.
export type AzPort = {
  run: (args: readonly string[]) => string;
};

export type FilesPort = {
  mkdirp: (dir: string) => void;
  // Size in bytes of an existing file, or undefined when it does not exist.
  size: (file: string) => number | undefined;
  remove: (file: string) => void;
};

// Outbound connector that turns the HTML Azure DevOps stores into markdown; undefined when no converter is installed.
export type MarkdownPort = {
  fromHtml: (html: string) => string | undefined;
};

export type Deps = {
  az: AzPort;
  files: FilesPort;
  markdown: MarkdownPort;
  output: Output;
};
