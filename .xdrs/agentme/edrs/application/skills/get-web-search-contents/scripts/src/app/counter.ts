import { PACING_MS } from '../shared/constants';

import type { Deps } from './ports';
import type { SearchBudget } from './types';

export type Reservation = { allowed: boolean; budget: SearchBudget };

// Counts one search (a results page or a chat turn) against the run and spaces searches by PACING_MS.
export const reserveSearch = async (
  deps: Deps,
  runId: string,
  max: number,
  kind: 'search' | 'chat',
): Promise<Reservation> => {
  const state = (await deps.state.read(runId)) ?? { searches: 0, chatTurns: 0, lastAt: 0 };
  if (state.searches >= max) return { allowed: false, budget: { used: state.searches, max } };
  const wait = state.lastAt + PACING_MS - deps.clock.now();
  if (state.lastAt > 0 && wait > 0) await deps.clock.sleep(wait);
  const next = {
    searches: state.searches + 1,
    chatTurns: state.chatTurns + (kind === 'chat' ? 1 : 0),
    lastAt: deps.clock.now(),
  };
  await deps.state.write(runId, next);
  return { allowed: true, budget: { used: next.searches, max } };
};

export const currentBudget = async (
  deps: Deps,
  runId: string,
  max: number,
): Promise<SearchBudget> => {
  const state = await deps.state.read(runId);
  return { used: state?.searches ?? 0, max };
};
