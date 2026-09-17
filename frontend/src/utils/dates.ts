// Format a date-only string ("YYYY-MM-DD") without timezone drift.
// `new Date('2027-01-11')` is UTC midnight, which renders as the *previous*
// day anywhere west of UTC (e.g. Vancouver). Build the date from its parts in
// local time instead. Anything that isn't a plain date is returned unchanged.
export function formatDateOnly(value: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  if (!m) return value
  const [, y, mo, d] = m
  return new Date(Number(y), Number(mo) - 1, Number(d)).toLocaleDateString()
}
