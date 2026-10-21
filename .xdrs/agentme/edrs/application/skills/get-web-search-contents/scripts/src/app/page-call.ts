// A function that runs inside the page: the name lets tests tell calls apart, the source is what gets evaluated.
export type PageCall = { name: string; source: string };

export const pageCall = (fn: () => unknown): PageCall => ({
  name: fn.name,
  source: `(${fn.toString()})()`,
});
