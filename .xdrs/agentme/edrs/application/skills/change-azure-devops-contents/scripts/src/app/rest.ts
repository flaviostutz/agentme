import { ADO_RESOURCE, API_VERSION } from '../shared/constants';

import type { Deps } from './ports';

type RestOptions = {
  method: 'GET' | 'POST' | 'PATCH';
  uri: string;
  version?: string;
  body?: unknown;
  contentType?: string;
};

// Calls `az rest`; a JSON body goes through a temp file so no text passes through a shell.
export const rest = <T>(deps: Deps, options: RestOptions): T => {
  const { method, uri, version = API_VERSION, body, contentType } = options;
  const sep = uri.includes('?') ? '&' : '?';
  const args = [
    'rest',
    '--resource',
    ADO_RESOURCE,
    '--method',
    method,
    '--uri',
    `${uri}${sep}api-version=${version}`,
  ];
  if (body === undefined) return JSON.parse(deps.az.run(args) || 'null') as T;
  if (contentType) args.push('--headers', `Content-Type=${contentType}`);
  return deps.bodyFile.withFile(
    JSON.stringify(body),
    (file) => JSON.parse(deps.az.run([...args, '--body', `@${file}`]) || 'null') as T,
  );
};

// Plain text of a HTML fragment, used to compare content that Azure DevOps may re-format.
export const plainText = (html: string | undefined | null): string =>
  (html ?? '')
    .replaceAll(/<[^>]+>/g, ' ')
    .replaceAll('&nbsp;', ' ')
    .replaceAll('&lt;', '<')
    .replaceAll('&gt;', '>')
    .replaceAll('&quot;', '"')
    .replaceAll('&#39;', "'")
    .replaceAll('&amp;', '&')
    .replaceAll(/\s+/g, ' ')
    .trim();
