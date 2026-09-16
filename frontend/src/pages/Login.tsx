import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { login, getMe } from '@/services/auth'
import { useAuthStore } from '@/store/authStore'

export function Login() {
  const navigate = useNavigate()
  const setUser = useAuthStore((s) => s.setUser)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const mutation = useMutation({
    mutationFn: () => login(email, password),
    onSuccess: async () => {
      const user = await getMe()
      setUser(user)
      navigate('/jobs')
    },
  })

  return (
    <div className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold text-gray-900">Log in</h1>

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
        <div>
          <label className="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            required
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full rounded-md bg-primary-600 px-4 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Logging in…' : 'Log in'}
        </button>
        {mutation.isError && (
          <p className="text-sm text-red-600">Incorrect email or password.</p>
        )}
      </form>

      <p className="mt-4 text-sm text-gray-600">
        No account?{' '}
        <Link to="/signup" className="text-primary-600 hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  )
}
