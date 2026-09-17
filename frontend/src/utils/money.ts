// Format an integer-cents amount as a currency string.
export function formatCents(cents: number, currency: string): string {
  return new Intl.NumberFormat('en-CA', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(cents / 100)
}

// Contract term keys that hold integer-cents amounts.
export function isMoneyTerm(term: string): boolean {
  return term === 'salary' || term === 'hourly_rate'
}

// Contract term keys that hold a plain number (not money) and must be sent as one.
export function isNumericTerm(term: string): boolean {
  return term === 'hours_per_week'
}
