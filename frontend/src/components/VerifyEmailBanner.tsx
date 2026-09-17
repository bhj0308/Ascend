import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { sendVerification } from '@/services/auth'
import { useAuthStore } from '@/store/authStore'

export function VerifyEmailBanner() {
  const user = useAuthStore((s) => s.user)

  const mutation = useMutation({
    mutationFn: sendVerification,
  })

  if (!user || user.email_verified !== false) return null

  const isRateLimited = axios.isAxiosError(mutation.error) && mutation.error.response?.status === 429
  const errorDetail = axios.isAxiosError(mutation.error)
    ? (mutation.error.response?.data as { detail?: string } | undefined)?.detail
    : undefined

  return (
    <div className="flex items-center justify-center gap-2 bg-yellow-50 px-4 py-2 text-sm text-yellow-800">
      <span>Please verify your email.</span>
      <button
        type="button"
        onClick={() => mutation.mutate()}
        disabled={mutation.isPending || mutation.isSuccess}
        className="font-medium underline hover:no-underline disabled:no-underline disabled:opacity-60"
      >
        {mutation.isSuccess ? 'Sent' : mutation.isPending ? 'Sending…' : 'Resend'}
      </button>
      {mutation.isError && (
        <span className="text-yellow-900">
          {isRateLimited ? (errorDetail || 'Too many attempts — try again in a minute.') : 'Could not send. Try again.'}
        </span>
      )}
    </div>
  )
}
