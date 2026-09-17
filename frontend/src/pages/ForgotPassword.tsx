import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { forgotPassword } from '@/services/auth'

export function ForgotPassword() {
  const [email, setEmail] = useState('')

  const mutation = useMutation({
    mutationFn: () => forgotPassword(email),
  })

  const isRateLimited = axios.isAxiosError(mutation.error) && mutation.error.response?.status === 429

  return (
    <div className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold text-gray-900">Forgot password</h1>

      {mutation.isSuccess ? (
        <p className="mt-6 text-sm text-gray-700">{mutation.data.detail}</p>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            mutation.mutate()
          }}
          className="mt-6 space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              required
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full rounded-md bg-primary-600 px-4 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {mutation.isPending ? 'Sending…' : 'Send reset link'}
          </button>
          {mutation.isError && (
            <p className="text-sm text-red-600">
              {isRateLimited ? 'Too many attempts — try again in a minute.' : 'Something went wrong. Try again.'}
            </p>
          )}
        </form>
      )}

      <p className="mt-4 text-sm text-gray-600">
        <Link to="/login" className="text-primary-600 hover:underline">
          Back to log in
        </Link>
      </p>
    </div>
  )
}
