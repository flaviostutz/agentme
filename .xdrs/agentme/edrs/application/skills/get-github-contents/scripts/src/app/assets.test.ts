import { extractAssets, extractLinks, isAssetUrl } from './assets';

describe('isAssetUrl', () => {
  it.each([
    'https://github.com/user-attachments/assets/1234-abcd',
    'https://github.com/user-attachments/files/55/spec.pdf',
    'https://github.com/acme/widgets/files/77/log.txt',
    'https://private-user-images.githubusercontent.com/1/x.png?jwt=abc',
    'https://user-images.githubusercontent.com/1/x.png',
    'https://github-production-user-asset-6210df.s3.amazonaws.com/1/x.png',
  ])('allows %s', (url) => {
    expect(isAssetUrl(url)).toBe(true);
  });

  it.each([
    'http://github.com/user-attachments/assets/1',
    'https://github.com/acme/widgets/issues/1',
    'https://169.254.169.254/latest/meta-data',
    'https://evil.example.com/user-attachments/assets/1',
    'https://githubusercontent.com.evil.example/x.png',
    'not a url',
  ])('rejects %s (security)', (url) => {
    expect(isAssetUrl(url)).toBe(false);
  });
});

describe('extractAssets', () => {
  it('reads images and file links from rendered html and decodes entities', () => {
    const html =
      '<p><img src="https://private-user-images.githubusercontent.com/1/x.png?jwt=a&amp;b=2" alt="mock"></p>' +
      '<a href="https://github.com/user-attachments/files/55/spec.pdf">spec.pdf</a>' +
      '<a href="https://example.com/page">page</a>' +
      '<img src="https://evil.example.com/p.png" alt="evil">';
    expect(extractAssets(html)).toEqual([
      { name: 'mock', url: 'https://private-user-images.githubusercontent.com/1/x.png?jwt=a&b=2' },
      { name: 'spec.pdf', url: 'https://github.com/user-attachments/files/55/spec.pdf' },
    ]);
  });

  it('names an image without alt text after its path', () => {
    const [asset] = extractAssets('<img src="https://github.com/user-attachments/assets/abc-123">');
    expect(asset?.name).toBe('abc-123');
  });

  it('returns nothing for plain text', () => {
    expect(extractAssets('')).toEqual([]);
  });
});

describe('extractLinks', () => {
  it('lists unique external URLs without attachments, own URL or trailing punctuation', () => {
    const text =
      'See https://wiki.example.com/spec. Also (https://github.com/acme/other/issues/3), ' +
      'https://github.com/user-attachments/assets/1 and https://github.com/acme/widgets/issues/1 twice https://wiki.example.com/spec';
    expect(extractLinks(text, 'https://github.com/acme/widgets/issues/1')).toEqual([
      'https://wiki.example.com/spec',
      'https://github.com/acme/other/issues/3',
    ]);
  });
});
