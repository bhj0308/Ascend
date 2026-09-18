import axios from 'axios'

// Prefer the backend's `detail` (e.g. "Verify your email address before doing this")
// over a generic message, so users see why an action was refused.
export function describeError(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: string } | undefined)?.detail
    if (typeof detail === 'string' && detail) return detail
    if (!error.response) return 'Could not reach the server. Check your connection.'
  }
  return fallback
}
