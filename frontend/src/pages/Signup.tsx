import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { signup, login, getMe } from '@/services/auth'
import { useAuthStore } from '@/store/authStore'
import type { UserType } from '@/types'

const USER_TYPES: { value: UserType; label: string }[] = [
  { value: 'founder', label: "I'm hiring (Founder / CTO)" },
  { value: 'engineer', label: "I'm a tech professional" },
  { value: 'iec_worker', label: "I'm on a working holiday (IEC)" },
  { value: 'immigrant', label: "I'm an immigrant looking for work" },
]

export function Signup() {
  const navigate = useNavigate()
  const setUser = useAuthStore((s) => s.setUser)
  const [form, setForm] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    user_type: 'engineer' as UserType,
  })

  const mutation = useMutation({
    mutationFn: async () => {
      await signup(form)
      await login(form.email, form.password)
      return getMe()
    },
    onSuccess: (user) => {
      setUser(user)
      navigate('/jobs')
    },
  })

  return (
    <div className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold text-gray-900">Create your account</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          mutation.mutate()
        }}
        className="mt-6 space-y-4"
      >
        <div>
          <label className="block text-sm font-medium text-gray-700">I am…</label>
          <select
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.user_type}
            onChange={(e) => setForm((f) => ({ ...f, user_type: e.target.value as UserType }))}
          >
            {USER_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">First name</label>
            <input
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={form.first_name}
              onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Last name</label>
            <input
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={form.last_name}
              onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            required
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            required
            minLength={8}
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
          />
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full rounded-md bg-primary-600 px-4 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Creating account…' : 'Sign up'}
        </button>
        {mutation.isError && (
          <p className="text-sm text-red-600">Could not create account. Email may already be in use.</p>
        )}
      </form>

      <p className="mt-4 text-sm text-gray-600">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-600 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  )
}
