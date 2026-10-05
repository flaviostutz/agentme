import type { Deps } from './ports';

export type World = {
  deps: Deps;
  stdout: string[];
  stderr: string[];
  azCalls: string[][];
  files: Map<string, number>;
  removed: string[];
};

type Options = {
  az?: (args: readonly string[]) => string;
  // Bytes a download writes for a given `--output-file` path (default 4).
  downloadSize?: (path: string) => number | undefined;
  // Fake converter: undefined models a missing pandoc.
  markdown?: ((html: string) => string | undefined) | 'missing';
};

export const createWorld = (options: Options = {}): World => {
  const world: World = {
    deps: undefined as unknown as Deps,
    stdout: [],
    stderr: [],
    azCalls: [],
    files: new Map(),
    removed: [],
  };
  const convert = options.markdown ?? ((html: string): string => `md:${html}`);
  world.deps = {
    az: {
      run: (args): string => {
        world.azCalls.push([...args]);
        if (!options.az) throw new Error('unexpected az call');
        const output = args.indexOf('--output-file');
        const target = output === -1 ? undefined : args[output + 1];
        if (target !== undefined) {
          const size = options.downloadSize ? options.downloadSize(target) : 4;
          if (size !== undefined) world.files.set(target, size);
        }
        return options.az(args);
      },
    },
    files: {
      mkdirp: (): void => undefined,
      size: (file): number | undefined => world.files.get(file),
      remove: (file): void => {
        world.files.delete(file);
        world.removed.push(file);
      },
    },
    markdown: {
      fromHtml: (html): string | undefined => (convert === 'missing' ? undefined : convert(html)),
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
