import type { Deps, HttpResult } from './ports';

export type World = {
  deps: Deps;
  stdout: string[];
  stderr: string[];
  ghCalls: string[][];
  httpCalls: string[];
  files: Map<string, Uint8Array>;
};

type Options = {
  gh?: (args: readonly string[]) => string;
  http?: (url: string) => HttpResult;
};

export const okBytes = (text: string, contentType = 'image/png'): HttpResult => ({
  status: 200,
  location: undefined,
  contentType,
  bytes: new TextEncoder().encode(text),
});

export const createWorld = (options: Options = {}): World => {
  const world: World = {
    deps: undefined as unknown as Deps,
    stdout: [],
    stderr: [],
    ghCalls: [],
    httpCalls: [],
    files: new Map(),
  };
  world.deps = {
    gh: {
      run: (args): string => {
        world.ghCalls.push([...args]);
        if (!options.gh) throw new Error('unexpected gh call');
        return options.gh(args);
      },
    },
    http: {
      get: async (url): Promise<HttpResult> => {
        world.httpCalls.push(url);
        if (!options.http) throw new Error('unexpected http call');
        return options.http(url);
      },
    },
    files: {
      mkdirp: (): void => undefined,
      write: (file, bytes): void => {
        world.files.set(file, bytes);
      },
    },
    output: {
      out: (text): void => {
        world.stdout.push(text);
      },
      err: (text): void => {
        world.stderr.push(text);
      },
    },
  };
  return world;
};
