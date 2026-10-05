import { extractLinks, inlineAttachmentUrls, isAttachmentUrl } from './links';

const ATT = 'https://dev.azure.com/contoso/p-guid/_apis/wit/attachments/abc';

describe('links', () => {
  it('recognizes only same-organization attachment URLs', () => {
    expect(isAttachmentUrl(ATT, 'contoso')).toBe(true);
    expect(isAttachmentUrl(ATT, 'other')).toBe(false);
    expect(isAttachmentUrl('https://dev.azure.com/contoso/p/_workitems/edit/1', 'contoso')).toBe(
      false,
    );
  });

  it('finds inline images and decodes HTML entities', () => {
    const html = `<p><img src="${ATT}?fileName=a.png&amp;x=1" alt="a"> <img src="https://evil.example.com/x.png"></p>`;
    expect(inlineAttachmentUrls(html, 'contoso')).toEqual([`${ATT}?fileName=a.png&x=1`]);
  });

  it('extracts external links without attachments, the item itself and trailing punctuation', () => {
    const own = 'https://dev.azure.com/contoso/p/_workitems/edit/1';
    const text = `<a href="https://wiki.example.com/spec">spec</a> see https://other.example.com/x. ${own} ${ATT} https://wiki.example.com/spec`;
    expect(extractLinks(text, own, 'contoso')).toEqual([
      'https://wiki.example.com/spec',
      'https://other.example.com/x',
    ]);
  });
});
