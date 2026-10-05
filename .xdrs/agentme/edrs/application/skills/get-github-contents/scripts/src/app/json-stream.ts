// `gh api --paginate` prints one JSON array per page back to back (e.g. `[..][..]`).
export const parseJsonStream = (text: string): unknown[] => {
  const values: unknown[] = [];
  let depth = 0;
  let start = -1;
  let inString = false;
  let escaped = false;
  for (let index = 0; index < text.length; index += 1) {
    const ch = text.charAt(index);
    if (inString) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
    } else if (ch === '"') {
      inString = true;
    } else if (ch === '[' || ch === '{') {
      if (depth === 0) start = index;
      depth += 1;
    } else if (ch === ']' || ch === '}') {
      depth -= 1;
      if (depth === 0) values.push(JSON.parse(text.slice(start, index + 1)));
    }
  }
  if (depth !== 0 || inString) throw new Error('truncated JSON output');
  return values;
};

export const flattenPages = <T>(text: string): T[] =>
  parseJsonStream(text).flatMap((value) => (Array.isArray(value) ? (value as T[]) : [value as T]));
