import { downloadAssets, mergeAssets } from './attachments';
import { createWorld } from './world_mock';

const url = (id: string): string => `https://dev.azure.com/contoso/p/_apis/wit/attachments/${id}`;
const options = { dir: '.tmp/x', org: 'contoso' };

describe('mergeAssets', () => {
  it('keeps the first entry per file and drops invalid URLs', () => {
    expect(
      mergeAssets([
        { name: 'spec.pdf', url: url('a'), size: 5 },
        { name: 'image', url: `${url('A')}?fileName=img.png` },
        { name: 'bad', url: 'nonsense' },
      ]),
    ).toEqual([{ name: 'spec.pdf', url: url('a'), size: 5 }]);
  });
});

describe('downloadAssets', () => {
  it('downloads through az rest with the output file (happy flow)', () => {
    const world = createWorld({ az: () => '' });
    const result = downloadAssets([{ name: 'my spec.pdf', url: url('a') }], options, world.deps);
    expect(result).toEqual([{ name: 'my spec.pdf', url: url('a'), path: '.tmp/x/1-my_spec.pdf' }]);
    expect(world.azCalls[0]).toEqual([
      'rest',
      '--resource',
      '499b84ac-1321-427f-aa17-267ca6975798',
      '--method',
      'GET',
      '--uri',
      `${url('a')}?api-version=7.1`,
      '--output-file',
      '.tmp/x/1-my_spec.pdf',
    ]);
  });

  it('never sends the token to a host outside the organization (security)', () => {
    const world = createWorld({ az: () => '' });
    const result = downloadAssets(
      [
        { name: 'a', url: 'https://evil.example.com/_apis/wit/attachments/1' },
        { name: 'b', url: 'https://dev.azure.com/other/p/_apis/wit/attachments/1' },
      ],
      options,
      world.deps,
    );
    expect(result.map((item) => ('error' in item ? item.error : 'ok'))).toEqual([
      'host not allowed',
      'host not allowed',
    ]);
    expect(world.azCalls).toEqual([]);
  });

  it('skips files that are too large before and after the download', () => {
    const world = createWorld({ az: () => '', downloadSize: () => 11 * 1024 * 1024 });
    const result = downloadAssets(
      [
        { name: 'declared', url: url('a'), size: 11 * 1024 * 1024 },
        { name: 'actual', url: url('b') },
      ],
      options,
      world.deps,
    );
    expect(result.map((item) => ('error' in item ? item.error : 'ok'))).toEqual([
      'file is larger than 10 MB',
      'file is larger than 10 MB',
    ]);
    expect(world.removed).toEqual(['.tmp/x/2-actual']);
  });

  it('reports a failed download and a missing output without aborting', () => {
    const failing = createWorld({
      az: () => {
        throw Object.assign(new Error('Command failed'), { stderr: 'ERROR: 403 Forbidden\n' });
      },
    });
    expect(downloadAssets([{ name: 'a', url: url('a') }], options, failing.deps)).toEqual([
      { name: 'a', url: url('a'), error: 'ERROR: 403 Forbidden' },
    ]);
    const empty = createWorld({ az: () => '', downloadSize: (): undefined => undefined });
    expect(downloadAssets([{ name: 'a', url: url('a') }], options, empty.deps)).toEqual([
      { name: 'a', url: url('a'), error: 'download produced no file' },
    ]);
    const plain = createWorld({
      az: () => {
        throw new Error('boom');
      },
    });
    expect(downloadAssets([{ name: 'a', url: url('a') }], options, plain.deps)).toEqual([
      { name: 'a', url: url('a'), error: 'boom' },
    ]);
  });

  it('caps the number of downloads (edge case)', () => {
    const world = createWorld({ az: () => '' });
    const assets = Array.from({ length: 22 }, (_, index) => ({
      name: `f${index}`,
      url: url(`id${index}`),
    }));
    const result = downloadAssets(assets, options, world.deps);
    expect(world.azCalls).toHaveLength(20);
    expect(result[20]).toMatchObject({ error: 'skipped: more than 20 attachments' });
  });
});
