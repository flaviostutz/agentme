const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/u;

const pad = (value: number, width: number): string => String(value).padStart(width, '0');

const daysInMonth = (year: number, month: number): number =>
  new Date(Date.UTC(year, month, 0)).getUTCDate();

export const isValidIsoDate = (value: string): boolean => {
  const match = ISO_DATE.exec(value);
  if (!match) return false;
  const [year, month, day] = [Number(match[1]), Number(match[2]), Number(match[3])];
  return month >= 1 && month <= 12 && day >= 1 && day <= daysInMonth(year, month);
};

// Adds calendar months, clamping the day (for example 2028-02-29 + 12 months = 2029-02-28).
export const addMonths = (isoDate: string, months: number): string => {
  const match = ISO_DATE.exec(isoDate);
  const [year, month, day] = [Number(match?.[1]), Number(match?.[2]), Number(match?.[3])];
  const total = year * 12 + (month - 1) + months;
  const targetYear = Math.floor(total / 12);
  const targetMonth = (total % 12) + 1;
  return `${pad(targetYear, 4)}-${pad(targetMonth, 2)}-${pad(Math.min(day, daysInMonth(targetYear, targetMonth)), 2)}`;
};

export const localToday = (now: Date = new Date()): string =>
  `${pad(now.getFullYear(), 4)}-${pad(now.getMonth() + 1, 2)}-${pad(now.getDate(), 2)}`;

export type ReviewDateStatus = 'ok' | 'invalid' | 'expired' | 'too-far';

// Valid ISO dates compare as plain strings.
export const reviewDateStatus = (value: string, today: string): ReviewDateStatus => {
  if (!isValidIsoDate(value)) return 'invalid';
  if (value < today) return 'expired';
  return value > addMonths(today, 12) ? 'too-far' : 'ok';
};
