#!/usr/bin/env node
'use strict';

/**
 * Safe read/update helper for a resolve-pr-comments tracking file
 * (.tmp/review-pr-<N>.md), keyed by each section's stable `id:` value
 * instead of its title text. See SKILL.md's "Editing the tracking file" note.
 *
 * Usage:
 *   update-section.js init <file> <pr-number> <pr-link> <auto-summary...>  (raw PR summary from stdin)
 *   update-section.js append-section <file>                               (full "### ..." section from stdin)
 *   update-section.js list <file> [--json]
 *   update-section.js get <file> <id> <field>
 *   update-section.js set <file> <id> <field> <value...>
 *   update-section.js set-block <file> <id> <field>   (new value read from stdin)
 *   update-section.js set-list <file> <id> <field>    (new items read from stdin, one per line)
 *
 * <id> is the section's "id:" value (e.g. "review-comment/1935286030"), not the title.
 */

const fs = require('fs');

const SCALAR_FIELDS = [
  'id',
  'status',
  'source',
  'author-raw',
  'comment-url',
  'type',
  'possible-user-intention',
  'suggested-fix-assessment',
  'criticality',
  'automation-suggestion',
  'action',
  'resolve-on-apply',
  'pending-reply',
];
const BLOCK_FIELDS = ['source-lines', 'diff-hunk-raw', 'suggested-fix', 'comment-raw', 'reply-draft'];
const LIST_FIELDS = ['replies-raw', 'possible-follow-ups', 'similar-to'];
const ALL_FIELDS = [...SCALAR_FIELDS, ...BLOCK_FIELDS, ...LIST_FIELDS];
const NEXT_FIELD_RE = new RegExp(`^(?:${ALL_FIELDS.join('|')}):`);

function usage() {
  return `Usage:
  update-section.js init <file> <pr-number> <pr-link> <auto-summary...>  (raw PR summary from stdin)
  update-section.js append-section <file>                               (full "### ..." section from stdin)
  update-section.js list <file> [--json]
  update-section.js get <file> <id> <field>
  update-section.js set <file> <id> <field> <value...>
  update-section.js set-block <file> <id> <field>   (new value read from stdin)
  update-section.js set-list <file> <id> <field>    (new items read from stdin, one per line)

<id> is the section's "id:" value (e.g. "review-comment/1935286030"), not the title.
Scalar fields: ${SCALAR_FIELDS.join(', ')}
Block fields (use set-block): ${BLOCK_FIELDS.join(', ')}
List fields (use set-list): ${LIST_FIELDS.join(', ')}`;
}

function headerIndices(lines) {
  const idx = [];
  lines.forEach((line, i) => {
    if (line.startsWith('### ')) idx.push(i);
  });
  return idx;
}

function findSectionById(lines, id) {
  const idx = headerIndices(lines);
  const matches = [];
  for (let s = 0; s < idx.length; s++) {
    const start = idx[s];
    const end = s + 1 < idx.length ? idx[s + 1] : lines.length;
    for (let i = start; i < end; i++) {
      const m = /^id:\s*(.*)$/.exec(lines[i]);
      if (m && m[1].trim() === id) {
        matches.push({ start, end, title: lines[start].slice(4).trim() });
        break;
      }
    }
  }
  if (matches.length === 0) throw new Error(`no section found with id: ${id}`);
  if (matches.length > 1) {
    throw new Error(`ambiguous: ${matches.length} sections found with id: ${id}`);
  }
  return matches[0];
}

// Locates `field:`'s own line plus the line range of any indented content that follows it
// (block-scalar `|` content or a `- ` list), stopping at the next known top-level field or
// the next section header -- never at a bare blank line, since block content legitimately
// contains blank lines.
function findField(lines, start, end, field) {
  const headRe = new RegExp(`^${field}:(.*)$`);
  const occurrences = [];
  for (let i = start; i < end; i++) {
    if (headRe.test(lines[i])) occurrences.push(i);
  }
  if (occurrences.length === 0) throw new Error(`field "${field}" not found in matched section`);
  if (occurrences.length > 1) {
    throw new Error(
      `field "${field}" appears ${occurrences.length} times in this section -- ambiguous, edit manually`,
    );
  }
  const lineIdx = occurrences[0];
  const suffix = headRe.exec(lines[lineIdx])[1].trim();
  let contentEnd = lineIdx + 1;
  let kind;
  if (suffix === '|') {
    kind = 'block';
    while (contentEnd < end && !NEXT_FIELD_RE.test(lines[contentEnd]) && !lines[contentEnd].startsWith('### ')) {
      contentEnd++;
    }
  } else if (suffix === '') {
    if (lineIdx + 1 < end && /^ {2}- /.test(lines[lineIdx + 1])) {
      kind = 'list';
      while (contentEnd < end && /^ {2}- /.test(lines[contentEnd])) contentEnd++;
    } else {
      kind = 'scalar';
    }
  } else {
    kind = 'scalar';
  }
  return { lineIdx, kind, suffix, contentStart: lineIdx + 1, contentEnd };
}

function requireKind(field, expectedKind, fieldSet, cmdHint) {
  if (!fieldSet.includes(field)) {
    throw new Error(`field "${field}" is not a ${expectedKind} field -- use ${cmdHint}`);
  }
}

function readStdin() {
  return fs.readFileSync(0, 'utf8');
}

function writeBack(file, lines, hadTrailingNewline) {
  let text = lines.join('\n');
  if (hadTrailingNewline && !text.endsWith('\n')) text += '\n';
  fs.writeFileSync(file, text);
}

function main(argv) {
  const [cmd, file, ...rest] = argv;
  if (!cmd || cmd === '--help' || cmd === '-h' || !file) {
    console.error(usage());
    process.exit(cmd === '--help' || cmd === '-h' ? 0 : 1);
    return;
  }

  if (cmd === 'init') {
    const [prNumber, prLink, ...summaryParts] = rest;
    if (!prNumber || !prLink || summaryParts.length === 0) {
      console.error(usage());
      process.exit(1);
      return;
    }
    if (fs.existsSync(file)) {
      throw new Error(`refusing to overwrite existing file: ${file}`);
    }
    const rawSummary = readStdin().replace(/\n$/, '');
    const autoSummary = summaryParts.join(' ');
    fs.writeFileSync(
      file,
      `# PR #${prNumber}\n\n${prLink}\n\n${rawSummary}\n\n**Summary**: ${autoSummary}\n`,
    );
    console.log('OK');
    return;
  }

  if (cmd === 'append-section') {
    if (!fs.existsSync(file)) {
      throw new Error(`file does not exist: ${file}`);
    }
    const stdin = readStdin().replace(/\n$/, '');
    if (!stdin.startsWith('### ')) {
      throw new Error('stdin must be a full section starting with "### "');
    }
    const stdinLines = stdin.split('\n');
    const idLine = stdinLines.find((l) => /^id:\s*/.test(l));
    if (!idLine) {
      throw new Error('stdin section is missing an "id:" line');
    }
    const newId = idLine.replace(/^id:\s*/, '').trim();
    const original = fs.readFileSync(file, 'utf8');
    const hadTrailingNewline = original.endsWith('\n');
    const lines = original.split('\n');
    let duplicate = true;
    try {
      findSectionById(lines, newId);
    } catch (err) {
      if (!/^no section found/.test(err.message)) throw err;
      duplicate = false;
    }
    if (duplicate) {
      throw new Error(`a section with id "${newId}" already exists in ${file}`);
    }
    const separator = lines[lines.length - 1] === '' ? [] : [''];
    writeBack(file, [...lines, ...separator, ...stdinLines], hadTrailingNewline);
    console.log('OK');
    return;
  }

  const original = fs.readFileSync(file, 'utf8');
  const hadTrailingNewline = original.endsWith('\n');
  const lines = original.split('\n');

  if (cmd === 'list') {
    const jsonOutput = rest.includes('--json');
    const idx = headerIndices(lines);
    const rows = [];
    for (let s = 0; s < idx.length; s++) {
      const start = idx[s];
      const end = s + 1 < idx.length ? idx[s + 1] : lines.length;
      const row = {
        id: '',
        'author-raw': '',
        status: '',
        criticality: '',
        'automation-suggestion': '',
        action: '',
        'pending-reply': '',
        'resolve-on-apply': '',
      };
      for (const key of Object.keys(row)) {
        try {
          const f = findField(lines, start, end, key);
          row[key] = f.suffix;
        } catch {
          // field absent in a malformed section -- leave blank, never fail `list`
        }
      }
      let similarTo = '';
      try {
        const f = findField(lines, start, end, 'similar-to');
        similarTo = lines
          .slice(f.contentStart, f.contentEnd)
          .map((l) => l.replace(/^ {2}- /, ''))
          .join(', ');
      } catch {
        // field absent in a malformed section -- leave blank, never fail `list`
      }
      rows.push({ ...row, title: lines[start].slice(4).trim(), 'similar-to': similarTo });
    }
    if (jsonOutput) {
      console.log(JSON.stringify(rows, null, 2));
      return;
    }
    // Bullets avoid relying on column/tab alignment, which breaks once field values vary in width.
    for (const row of rows) {
      console.log(`- id: ${row.id}`);
      console.log(`  title: ${row.title}`);
      console.log(`  author-raw: ${row['author-raw']}`);
      console.log(`  status: ${row.status}`);
      console.log(`  criticality: ${row.criticality}`);
      console.log(`  automation-suggestion: ${row['automation-suggestion']}`);
      console.log(`  action: ${row.action}`);
      console.log(`  pending-reply: ${row['pending-reply']}`);
      console.log(`  resolve-on-apply: ${row['resolve-on-apply']}`);
      console.log(`  similar-to: ${row['similar-to']}`);
    }
    return;
  }

  const [id, field, ...valueParts] = rest;
  if (!id || !field) {
    console.error(usage());
    process.exit(1);
    return;
  }
  const section = findSectionById(lines, id);

  if (cmd === 'get') {
    const f = findField(lines, section.start, section.end, field);
    if (f.kind === 'scalar') {
      console.log(f.suffix);
    } else if (f.kind === 'block') {
      console.log(
        lines
          .slice(f.contentStart, f.contentEnd)
          .map((l) => (l.startsWith('  ') ? l.slice(2) : l))
          .join('\n'),
      );
    } else {
      console.log(
        lines
          .slice(f.contentStart, f.contentEnd)
          .map((l) => l.replace(/^ {2}- /, ''))
          .join('\n'),
      );
    }
    return;
  }

  if (cmd === 'set') {
    requireKind(field, 'scalar', SCALAR_FIELDS, 'set-block/set-list');
    const f = findField(lines, section.start, section.end, field);
    const value = valueParts.join(' ');
    lines[f.lineIdx] = value === '' ? `${field}:` : `${field}: ${value}`;
    writeBack(file, lines, hadTrailingNewline);
    console.log('OK');
    return;
  }

  if (cmd === 'set-block') {
    requireKind(field, 'block', BLOCK_FIELDS, 'set (scalar) or set-list');
    const f = findField(lines, section.start, section.end, field);
    const stdin = readStdin().replace(/\n$/, '');
    const newContentLines = stdin.split('\n').map((l) => (l === '' ? '' : `  ${l}`));
    lines.splice(f.lineIdx, f.contentEnd - f.lineIdx, `${field}: |`, ...newContentLines);
    writeBack(file, lines, hadTrailingNewline);
    console.log('OK');
    return;
  }

  if (cmd === 'set-list') {
    requireKind(field, 'list', LIST_FIELDS, 'set (scalar) or set-block');
    const f = findField(lines, section.start, section.end, field);
    const stdin = readStdin().replace(/\n$/, '');
    const items = stdin.split('\n').filter((l) => l.trim() !== '');
    const newContentLines = items.map((l) => `  - ${l}`);
    lines.splice(f.lineIdx, f.contentEnd - f.lineIdx, `${field}:`, ...newContentLines);
    writeBack(file, lines, hadTrailingNewline);
    console.log('OK');
    return;
  }

  console.error(usage());
  process.exit(1);
}

try {
  main(process.argv.slice(2));
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
