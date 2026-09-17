import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { resetPassword } from '@/services/auth'

export function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [matchError, setMatchError] = useState(false)

  const mutation = useMutation({
    mutationFn: () => resetPassword(token as string, password),
  })

  const isInvalidLink = axios.isAxiosError(mutation.error) && mutation.error.response?.status === 400
  const errorDetail = axios.isAxiosError(mutation.error)
    ? (mutation.error.response?.data as { detail?: string } | undefined)?.detail
    : undefined

  if (!token) {
    return (
      <div className="mx-auto max-w-sm px-4 py-16">
        <h1 className="text-2xl font-bold text-gray-900">Reset password</h1>
        <p className="mt-6 text-sm text-red-600">This reset link is invalid.</p>
        <p className="mt-4 text-sm text-gray-600">
          <Link to="/forgot-password" className="text-primary-600 hover:underline">
            Request a new link
          </Link>
        </p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold text-gray-900">Reset password</h1>

      {mutation.isSuccess ? (
        <>
          <p className="mt-6 text-sm text-gray-700">{mutation.data.detail}</p>
          <p className="mt-4 text-sm text-gray-600">
            <Link to="/login" className="text-primary-600 hover:underline">
              Log in
            </Link>
          </p>
        </>
      ) : isInvalidLink ? (
        <>
          <p className="mt-6 text-sm text-red-600">{errorDetail}</p>
          <p className="mt-4 text-sm text-gray-600">
            <Link to="/forgot-password" className="text-primary-600 hover:underline">
              Request a new link
            </Link>
          </p>
        </>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            if (password !== confirmPassword) {
              setMatchError(true)
              return
            }
            setMatchError(false)
            mutation.mutate()
          }}
          className="mt-6 space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700">New password</label>
            <input
              type="password"
              required
              minLength={8}
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Confirm password</label>
            <input
              type="password"
              required
              minLength={8}
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full rounded-md bg-primary-600 px-4 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {mutation.isPending ? 'Resetting…' : 'Reset password'}
          </button>
          {matchError && <p className="text-sm text-red-600">Passwords do not match.</p>}
          {mutation.isError && !isInvalidLink && (
            <p className="text-sm text-red-600">{errorDetail || 'Something went wrong. Try again.'}</p>
          )}
        </form>
      )}
    </div>
  )
}
