import type { Deps, HttpResult } from './ports';

export type World = {
  deps: Deps;
  stdout: string[];
  stderr: string[];
  httpCalls: string[];
  dnsCalls: string[];
};

type Options = {
  http?: (url: string) => HttpResult;
  dns?: (host: string) => string[];
};

export const html = (
  body: string,
  status = 200,
  contentType = 'text/html; charset=utf-8',
): HttpResult => ({
  status,
  location: undefined,
  contentType,
  bytes: new TextEncoder().encode(body),
});

export const redirect = (location: string, status = 302): HttpResult => ({
  status,
  location,
  contentType: undefined,
  bytes: undefined,
});

export const createWorld = (options: Options = {}): World => {
  const world: World = {
    deps: undefined as unknown as Deps,
    stdout: [],
    stderr: [],
    httpCalls: [],
    dnsCalls: [],
  };
  world.deps = {
    http: {
      get: async (url): Promise<HttpResult> => {
        world.httpCalls.push(url);
        if (!options.http) throw new Error('unexpected http call');
        return options.http(url);
      },
    },
    dns: {
      lookup: async (host): Promise<string[]> => {
        world.dnsCalls.push(host);
        return options.dns ? options.dns(host) : ['93.184.216.34'];
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
