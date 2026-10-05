import { ADO_RESOURCE, API_VERSION } from '../shared/constants';

import type { AzPort } from './ports';

// `az rest` cannot derive the Azure DevOps AAD resource from the URL, so it is always passed.
export const restArgs = (method: 'GET', uri: string, version: string): string[] => {
  const sep = uri.includes('?') ? '&' : '?';
  return [
    'rest',
    '--resource',
    ADO_RESOURCE,
    '--method',
    method,
    '--uri',
    `${uri}${sep}api-version=${version}`,
  ];
};

export const restGet = <T>(az: AzPort, uri: string, version = API_VERSION): T =>
  JSON.parse(az.run(restArgs('GET', uri, version))) as T;
