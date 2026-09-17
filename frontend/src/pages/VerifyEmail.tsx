import { useEffect, useRef } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { getMe, verifyEmail } from '@/services/auth'
import { useAuthStore } from '@/store/authStore'

export function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const setUser = useAuthStore((s) => s.setUser)
  const currentUser = useAuthStore((s) => s.user)
  const hasRun = useRef(false)

  const mutation = useMutation({
    mutationFn: () => verifyEmail(token as string),
    onSuccess: async () => {
      if (currentUser) {
        const user = await getMe()
        setUser(user)
      }
    },
  })

  useEffect(() => {
    if (hasRun.current || !token) return
    hasRun.current = true
    mutation.mutate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  const errorDetail = axios.isAxiosError(mutation.error)
    ? (mutation.error.response?.data as { detail?: string } | undefined)?.detail
    : undefined

  if (!token) {
    return (
      <div className="mx-auto max-w-sm px-4 py-16">
        <h1 className="text-2xl font-bold text-gray-900">Verify email</h1>
        <p className="mt-6 text-sm text-red-600">This verification link is invalid.</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold text-gray-900">Verify email</h1>

      {mutation.isPending || mutation.isIdle ? (
        <p className="mt-6 text-sm text-gray-500">Verifying…</p>
      ) : mutation.isSuccess ? (
        <>
          <p className="mt-6 text-sm text-gray-700">{mutation.data.detail}</p>
          <p className="mt-4 text-sm text-gray-600">
            <Link to="/jobs" className="text-primary-600 hover:underline">
              Continue to jobs
            </Link>
          </p>
        </>
      ) : (
        <>
          <p className="mt-6 text-sm text-red-600">{errorDetail || 'Could not verify this email.'}</p>
          <p className="mt-4 text-sm text-gray-600">
            You can request a new link from the banner on your profile.
          </p>
        </>
      )}
    </div>
  )
}
