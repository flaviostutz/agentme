export type HubItem = { readonly id: string; readonly mayBeNotApplicable: boolean };

// Must stay identical to the item table in agentme-adr-policy-501 rule 06 (a test enforces it).
export const ITEMS: readonly HubItem[] = [
  { id: 'roles', mayBeNotApplicable: false },
  { id: 'dpo', mayBeNotApplicable: true },
  { id: 'ropa', mayBeNotApplicable: true },
  { id: 'dpia', mayBeNotApplicable: true },
  { id: 'processors-and-transfers', mayBeNotApplicable: true },
  { id: 'retention', mayBeNotApplicable: false },
  { id: 'lawful-bases-and-consents', mayBeNotApplicable: false },
  { id: 'dsr-and-breach-runbooks', mayBeNotApplicable: false },
];

export const APPLICABILITY_ID = 'applicability';

export type Field = { readonly value: string; readonly line: number };

export type Block = {
  readonly id: string;
  readonly line: number;
  readonly fields: Readonly<Record<string, Field>>;
};

const BLOCK_HEADING = /^####\s+\d+-([\da-z-]+)\s*$/u;
const ANY_HEADING = /^#{1,6}\s/u;
const FIELD_LINE = /^([A-Z][A-Za-z-]*):[ \t]*(.*?)\s*$/u;

// Reads `#### NN-<id>` blocks and their `Key: value` lines; the first occurrence of a key wins.
export const parseBlocks = (text: string): Block[] => {
  const blocks: { id: string; line: number; fields: Record<string, Field> }[] = [];
  let current: { id: string; line: number; fields: Record<string, Field> } | undefined;
  for (const [index, raw] of text.split(/\r?\n/u).entries()) {
    const heading = BLOCK_HEADING.exec(raw);
    if (heading) {
      current = { id: heading[1] ?? '', line: index + 1, fields: {} };
      blocks.push(current);
    } else if (ANY_HEADING.test(raw)) {
      current = undefined;
    } else if (current) {
      const field = FIELD_LINE.exec(raw);
      const key = field?.[1];
      if (key !== undefined && !(key in current.fields)) {
        current.fields[key] = { value: field?.[2] ?? '', line: index + 1 };
      }
    }
  }
  return blocks;
};

export const fieldValue = (block: Block, key: string): string | undefined => {
  const value = block.fields[key]?.value;
  return value === undefined || value === '' ? undefined : value;
};
